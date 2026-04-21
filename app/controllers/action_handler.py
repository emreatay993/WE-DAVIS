# File: app/controllers/action_handler.py

import os
import re
import string
from collections import OrderedDict

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QAbstractItemView,
                             QListWidgetItem, QHBoxLayout, QPushButton, QMessageBox,
                             QFileDialog, QComboBox, QLabel)
from scipy.signal.windows import tukey

from ..analysis.ansys_exporter import AnsysExportUnits, AnsysExporter, _APPVOL_RAW_PATH_RE
from ..analysis.data_processing import apply_data_section, apply_tukey_window
from ..analysis.steady_state_estimator import (
    SteadyStateEstimateSnapshot,
    estimate_cycles_to_steady_state,
)
from ..analysis.steady_state_time_history_export import resolve_frequency_to_hz
from ..ui.tab_settings import SettingsTab
from ..units import ColumnUnitContext, ConversionSpec, convert_dataframe_copy, convert_series


class ActionHandler(QtCore.QObject):
    """
    Handles complex user-initiated actions like data exports.
    """
    def __init__(self, main_window, data_manager, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.data_manager = data_manager

    def _get_source_df(self):
        raw_df = getattr(self.main_window, "raw_primary_df", None)
        return raw_df if raw_df is not None else self.main_window.df

    def _get_export_mode(self):
        export_mode = getattr(self.main_window, "export_unit_mode", SettingsTab.EXPORT_SOURCE_UNITS)
        if export_mode in {SettingsTab.EXPORT_SOURCE_UNITS, SettingsTab.EXPORT_DISPLAY_UNITS}:
            return export_mode
        return SettingsTab.EXPORT_SOURCE_UNITS

    def _get_export_mode_slug(self):
        if self._get_export_mode() == SettingsTab.EXPORT_DISPLAY_UNITS:
            return "display_units"
        return "source_units"

    def _get_export_mode_label(self):
        return self._get_export_mode()

    def _get_export_context_map(self):
        if self._get_export_mode() == SettingsTab.EXPORT_DISPLAY_UNITS:
            context_map = getattr(self.main_window, "unit_context", None)
        else:
            context_map = getattr(self.main_window, "raw_unit_context", None)
            if context_map is None:
                context_map = getattr(self.main_window, "unit_context", None)
        return context_map if context_map is not None else {}

    def _get_display_context_map(self):
        context_map = getattr(self.main_window, "unit_context", None)
        return context_map if context_map is not None else {}

    def _build_export_frame(self, frame):
        export_frame = frame.copy(deep=True)
        export_context_map = self._get_export_context_map()
        if self._get_export_mode() != SettingsTab.EXPORT_DISPLAY_UNITS:
            return export_frame, export_context_map

        conversions = {}
        for column_name in export_frame.columns:
            context = export_context_map.get(column_name)
            if (
                context is None
                or context.native_only
                or context.normalized_unit is None
                or context.display_unit is None
                or context.normalized_unit == context.display_unit
            ):
                continue
            conversions[column_name] = ConversionSpec(
                source_unit=context.normalized_unit,
                target_unit=context.display_unit,
                family_hint=context.quantity_family,
            )

        if conversions:
            export_frame = convert_dataframe_copy(export_frame, conversions)
        return export_frame, export_context_map

    def _build_theta_display_context(self):
        active_display_units = getattr(self.main_window, "active_display_units_by_family", None) or {}
        theta_display_unit = active_display_units.get("phase", "deg")
        return ColumnUnitContext.from_source_unit(
            "Theta",
            "deg",
            display_unit=theta_display_unit,
            family_hint="phase",
        )

    def _convert_display_series_to_export_mode(self, values, context):
        series = pd.Series(values, copy=True)
        if (
            self._get_export_mode() == SettingsTab.EXPORT_DISPLAY_UNITS
            or context is None
            or context.native_only
            or context.normalized_unit is None
            or context.display_unit is None
            or context.normalized_unit == context.display_unit
        ):
            return series
        return convert_series(
            series,
            source_unit=context.display_unit,
            target_unit=context.normalized_unit,
            family_hint=context.quantity_family,
        )

    def _get_export_unit_label(self, context):
        if context is None:
            return None
        if self._get_export_mode() == SettingsTab.EXPORT_DISPLAY_UNITS:
            return context.display_unit or context.normalized_unit
        return context.normalized_unit or context.display_unit

    def _format_export_column_label(self, column_name, context):
        unit = self._get_export_unit_label(context)
        return f"{column_name} [{unit}]" if unit else column_name

    def _validate_ansys_export_units(self, export_frame, export_context_map):
        if export_frame is None or export_frame.empty:
            return None, "ANSYS export requires at least one selected data column."

        data_domain = self.main_window.data_domain
        expected_domain_family = "frequency" if data_domain == "FREQ" else "time" if data_domain == "TIME" else None
        if expected_domain_family is None:
            return None, f"ANSYS export does not support the '{data_domain}' data domain."

        family_units = {
            expected_domain_family: set(),
            "force": set(),
            "moment": set(),
            "phase": set(),
        }
        validation_errors = []

        for column_name in export_frame.columns:
            if column_name in {"NO", "DataFolder"}:
                continue

            if column_name == data_domain:
                expected_family = expected_domain_family
            elif column_name.startswith("Phase_"):
                expected_family = "phase"
            else:
                component_match = re.search(r"\b([TR])[1-3]$", column_name)
                if component_match is None:
                    validation_errors.append(
                        f"- Column '{column_name}' is not a supported ANSYS load channel."
                    )
                    continue
                expected_family = "force" if component_match.group(1) == "T" else "moment"

            context = export_context_map.get(column_name)
            export_unit = None if context is None else (context.display_unit or context.normalized_unit)
            resolved_family = "unknown" if context is None else context.quantity_family
            if (
                context is None
                or export_unit is None
                or context.native_only
                or resolved_family == "unknown"
            ):
                validation_errors.append(
                    f"- Column '{column_name}' does not have a known export unit for ANSYS."
                )
                continue
            if resolved_family != expected_family:
                validation_errors.append(
                    f"- Column '{column_name}' resolves to '{resolved_family}' [{export_unit}] but ANSYS export "
                    f"expects '{expected_family}'."
                )
                continue
            family_units[expected_family].add(export_unit)

        mixed_unit_errors = [
            f"- {family.title()} columns resolve to multiple export units: {', '.join(sorted(units))}."
            for family, units in family_units.items()
            if len(units) > 1
        ]
        validation_errors.extend(mixed_unit_errors)

        if validation_errors:
            error_message = (
                "ANSYS export only supports known load-compatible quantity families for the selected export mode.\n\n"
                f"Export mode: {self._get_export_mode_label()}\n"
                "Required mapping:\n"
                f"- {data_domain}: {expected_domain_family}\n"
                "- T1/T2/T3: force\n"
                "- R1/R2/R3: moment\n"
                "- Phase_*: phase\n\n"
                "Validation details:\n"
                + "\n".join(validation_errors)
            )
            return None, error_message

        default_domain_unit = "Hz" if expected_domain_family == "frequency" else "s"
        return AnsysExportUnits(
            domain_unit=next(iter(family_units[expected_domain_family]), default_domain_unit),
            force_unit=next(iter(family_units["force"]), "N"),
            moment_unit=next(iter(family_units["moment"]), "N*m"),
            phase_unit=next(iter(family_units["phase"]), "deg"),
        ), None

    def _get_ansys_base_paths(self):
        """All plausible ANSYS base directories. Skips raw App Volumes paths."""
        paths = []

        def _add(path):
            if path and path not in paths:
                paths.append(path)

        for drive in string.ascii_uppercase:
            for subdir in ("Program Files\\ANSYS Inc", "ANSYS Inc", "Ansys"):
                _add(rf"{drive}:\{subdir}")

        for name, value in os.environ.items():
            upper = name.upper()
            if not (upper.startswith("AWP_ROOT") or "ANSYS" in upper):
                continue
            if not value:
                continue
            if _APPVOL_RAW_PATH_RE.search(value):
                continue
            if os.path.isdir(value):
                _add(os.path.dirname(value.rstrip("\\/")))
                _add(value)

        return paths

    def _get_available_ansys_versions(self):
        """Return ``version -> base_path`` for usable ANSYS installations."""
        available = {}
        for base in self._get_ansys_base_paths():
            if not os.path.isdir(base):
                continue
            try:
                entries = os.listdir(base)
            except OSError as exc:
                print(f"[ansys-vdi] Could not scan {base}: {exc}")
                continue
            for entry in entries:
                if not entry.lower().startswith("v"):
                    continue
                version_text = entry[1:]
                if not version_text.isdigit():
                    continue
                version = int(version_text)
                dll = os.path.join(
                    base,
                    entry,
                    "aisol",
                    "Bin",
                    "winx64",
                    "Ansys.Mechanical.Embedding.dll",
                )
                if version not in available and os.path.isfile(dll):
                    available[version] = base
        return available

    def _get_current_time_domain_frequency_hz(self):
        tab = self.main_window.tab_time_domain_represent
        candidate_texts = [tab.data_point_selector.currentText()]
        candidate_texts.extend(
            tab.data_point_selector.itemText(index)
            for index in range(1, tab.data_point_selector.count())
        )

        for text in candidate_texts:
            try:
                return float(text)
            except (TypeError, ValueError):
                continue
        return 1.0

    def _get_current_time_domain_frequency_summary(self):
        selected_frequency = self._get_current_time_domain_frequency_hz()
        frequency_context = getattr(self.main_window, "raw_unit_context", {}).get("FREQ")
        frequency_hz = resolve_frequency_to_hz(selected_frequency, frequency_context)
        frequency_unit = None if frequency_context is None else frequency_context.normalized_unit
        return selected_frequency, frequency_unit, frequency_hz

    def _get_sides_for_export(self):
        """Prompt for export sides plus the ANSYS version/base path to use."""
        all_sides = self.main_window.tab_part_loads.side_filter_selector.all_items()
        pre_checked_sides = set(self.main_window.tab_part_loads.selected_sides())
        available_versions = self._get_available_ansys_versions()
        if not available_versions:
            QMessageBox.critical(
                self.main_window,
                "No ANSYS Installation Found",
                "No usable ANSYS install was detected on this machine.\n\n"
                "On Omnissa Horizon this usually means the App Volumes package "
                "carrying ANSYS is not attached for your user, or the machine "
                "still exposes a raw SVROOT path that non-wrapped processes "
                "cannot use.\n\n"
                "Contact IT to provision ANSYS natively on this desktop pool.",
            )
            return None, None, None

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Select Parts to Export")
        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        for side in all_sides:
            item = QListWidgetItem(side)
            list_widget.addItem(item)
            if side in pre_checked_sides:
                item.setSelected(True)
        layout.addWidget(list_widget)

        layout.addWidget(QLabel("ANSYS version:"))
        version_combo = QComboBox()
        for version in sorted(available_versions.keys(), reverse=True):
            base_path = available_versions[version]
            version_combo.addItem(f"ANSYS v{version} ({base_path})", (version, base_path))
        layout.addWidget(version_combo)

        button_layout = QHBoxLayout()
        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        if dialog.exec_() == QDialog.Accepted:
            selected_sides = [item.text() for item in list_widget.selectedItems()]
            selected_version, ansys_base_path = version_combo.currentData()
            return selected_sides, selected_version, ansys_base_path
        return None, None, None

    @QtCore.pyqtSlot()
    def handle_compare_data_selection(self):
        """Handles the request to load comparison data."""
        self.data_manager.load_comparison_data()

    @QtCore.pyqtSlot()
    def handle_open_steady_state_cycle_estimator(self):
        from ..ui.steady_state_cycle_estimator_dialog import SteadyStateCycleEstimatorDialog

        initial_frequency_hz = self._get_current_time_domain_frequency_hz()
        dialog = SteadyStateCycleEstimatorDialog(
            parent=self.main_window,
            initial_excitation_frequency_hz=initial_frequency_hz,
            initial_mode_frequency_hz=initial_frequency_hz,
        )
        dialog.exec_()

        try:
            excitation_frequency_hz = dialog.excitation_frequency_spin.value()
            mode_frequency_hz = (
                excitation_frequency_hz
                if dialog.assume_resonance_checkbox.isChecked()
                else dialog.mode_frequency_spin.value()
            )
            estimate = estimate_cycles_to_steady_state(
                damping_ratio=dialog.damping_ratio_spin.value(),
                excitation_frequency_hz=excitation_frequency_hz,
                mode_frequency_hz=mode_frequency_hz,
                residual_fraction=dialog.residual_percent_spin.value() / 100.0,
            )
        except ValueError:
            self.main_window.tab_time_domain_represent.latest_estimator_snapshot = None
            return

        self.main_window.tab_time_domain_represent.latest_estimator_snapshot = (
            SteadyStateEstimateSnapshot(
                estimate=estimate,
                assume_resonance=dialog.assume_resonance_checkbox.isChecked(),
            )
        )

    @QtCore.pyqtSlot()
    def handle_open_steady_state_time_history_export(self):
        from ..ui.steady_state_time_history_export_dialog import (
            SteadyStateTimeHistoryExportDialog,
        )

        tab = self.main_window.tab_time_domain_represent
        frequency_text = tab.data_point_selector.currentText()
        if not frequency_text or "Select a frequency" in frequency_text:
            QMessageBox.warning(
                self.main_window,
                "Selection Required",
                "Please select a frequency before opening the steady-state time-history export.",
            )
            return

        interval_text = tab.interval_selector.currentText()
        if "Select an Interval [deg]" in interval_text:
            QMessageBox.warning(
                self.main_window,
                "Selection Required",
                "Please select a valid interval before opening the steady-state time-history export.",
            )
            return

        try:
            interval_degrees = int(interval_text)
        except ValueError:
            QMessageBox.warning(
                self.main_window,
                "Invalid Interval",
                "The selected interval is not valid.",
            )
            return

        if not getattr(tab, "current_plot_data", None):
            QMessageBox.warning(
                self.main_window,
                "No Data",
                "No time-domain plot data is available. Please select a frequency and part selection first.",
            )
            return

        selected_frequency, _, frequency_hz = self._get_current_time_domain_frequency_summary()
        if frequency_hz <= 0.0:
            QMessageBox.warning(
                self.main_window,
                "Invalid Frequency",
                "The selected frequency must resolve to a positive value in Hz.",
            )
            return

        dialog = SteadyStateTimeHistoryExportDialog(
            parent=self.main_window,
            current_plot_data=tab.current_plot_data,
            interval_degrees=interval_degrees,
            selected_frequency_value=selected_frequency,
            selected_frequency_context=getattr(self.main_window, "raw_unit_context", {}).get("FREQ"),
            estimator_snapshot=getattr(tab, "latest_estimator_snapshot", None),
            selected_parts=self.main_window.tab_part_loads.selected_sides(),
        )
        dialog.exec_()

    @QtCore.pyqtSlot()
    def handle_time_domain_represent_export(self):
        """
        Handles the request to extract and save the reconstructed time-domain data.
        """
        try:
            tab = self.main_window.tab_time_domain_represent
            interval_text = tab.interval_selector.currentText()
            if "Select an Interval [deg]" in interval_text:
                QMessageBox.warning(self.main_window, "Selection Required", "Please select a valid interval.")
                return
            interval = int(interval_text)

            if not hasattr(tab, 'current_plot_data') or not tab.current_plot_data:
                QMessageBox.warning(self.main_window, "No Data", "No plot data to extract. Please select a frequency first.")
                return

            num_points = 360 // interval
            sample_indices = [i * interval for i in range(num_points + 1)]
            first_plot_data = next(iter(tab.current_plot_data.values()))
            theta_values = pd.Series(first_plot_data["theta"], copy=True).iloc[sample_indices].reset_index(drop=True)
            theta_context = self._build_theta_display_context()
            exported_theta = self._convert_display_series_to_export_mode(theta_values, theta_context)
            data_dict = {self._format_export_column_label('Theta', theta_context): exported_theta.tolist()}
            display_context_map = self._get_display_context_map()

            for col, plot_data in tab.current_plot_data.items():
                full_y_data = pd.Series(plot_data['y_data'], copy=True).iloc[sample_indices].reset_index(drop=True)
                column_context = display_context_map.get(col)
                exported_y_data = self._convert_display_series_to_export_mode(full_y_data, column_context)
                data_dict[self._format_export_column_label(col, column_context)] = exported_y_data.tolist()

            df_to_export = pd.DataFrame(data_dict)

            save_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Extracted Data",
                f"extracted_time_represent_data_{self._get_export_mode_slug()}.csv",
                "CSV Files (*.csv)",
            )

            if save_path:
                df_to_export.to_csv(save_path, index=False)
                QMessageBox.information(
                    self.main_window,
                    "Export Successful",
                    "Data successfully saved using Settings > Export Units: "
                    f"{self._get_export_mode_label()} mode to:\n{save_path}",
                )
                os.startfile(os.path.dirname(save_path))

        except (ValueError, KeyError) as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred during data extraction: {e}")

    @QtCore.pyqtSlot()
    def handle_ansys_export(self):
        """Controller slot to manage the Ansys export process."""
        df = self._get_source_df()
        data_domain = self.main_window.data_domain
        if df is None:
            QMessageBox.warning(self.main_window, "No Data", "Please load data before exporting.")
            return

        export_selection = self._get_sides_for_export()
        if not export_selection:
            return
        if len(export_selection) == 2:
            selected_sides, version_data = export_selection
            selected_version, ansys_base_path = version_data
        else:
            selected_sides, selected_version, ansys_base_path = export_selection
        if not selected_sides:
            return

        cols_to_keep = [data_domain]
        for side in selected_sides:
            side_pattern = re.compile(rf'\b{re.escape(side)}\b')
            cols_to_keep.extend(
                [c for c in df.columns if side_pattern.search(c) and not any(s in c for s in ['T2/T3', 'R2/R3'])]
            )
        df_processed = df[list(OrderedDict.fromkeys(cols_to_keep))].copy()

        if data_domain == 'TIME':
            tab = self.main_window.tab_part_loads
            if tab.section_checkbox.isChecked():
                try:
                    t_min = float(tab.section_min_input.text())
                    t_max = float(tab.section_max_input.text())
                    if t_min < t_max:
                        df_processed = apply_data_section(df_processed,
                                                          tab.section_min_input.text(),
                                                          tab.section_max_input.text())
                    else:
                        QMessageBox.warning(self.main_window, "Invalid Range",
                                            "Min Time must be less than Max Time.")
                except ValueError:
                    QMessageBox.warning(self.main_window, "Invalid Input",
                                        "Please enter valid numeric values for Min and Max Time.")

            if tab.tukey_checkbox.isChecked():
                if len(df_processed) > 1:
                    df_processed = apply_tukey_window(df_processed, tab.tukey_alpha_spin.value())
                else:
                    print("Warning: Cannot apply Tukey window to a dataset with one or zero points.")

        df_export_processed, export_context_map = self._build_export_frame(df_processed)
        export_units, validation_error = self._validate_ansys_export_units(df_export_processed, export_context_map)
        if validation_error:
            QMessageBox.warning(self.main_window, "Unsupported ANSYS Export", validation_error)
            return

        df_combined_export = pd.DataFrame()
        export_mode_slug = self._get_export_mode_slug()
        for side in selected_sides:
            side_pattern = re.compile(rf'\b{re.escape(side)}\b')
            side_cols_to_keep = [data_domain]
            side_cols_to_keep.extend([c for c in df_export_processed.columns if side_pattern.search(c)])
            df_part_export = df_export_processed[list(OrderedDict.fromkeys(side_cols_to_keep))]

            df_part_export.to_csv(
                f"extracted_data_for_{side}_in_{export_mode_slug}.csv",
                index=False,
            )

            if df_combined_export.empty:
                df_combined_export = df_part_export
            else:
                df_to_concat = df_part_export.drop(columns=[data_domain])
                df_combined_export = pd.concat([df_combined_export, df_to_concat], axis=1)

        df_combined_export.to_csv(
            f"extracted_loads_of_all_selected_parts_in_{export_mode_slug}.csv",
            index=False,
        )

        exporter = AnsysExporter(version=selected_version, ansys_base_path=ansys_base_path)
        if data_domain == 'FREQ':
            exporter.create_harmonic_template(df_export_processed, data_domain, export_units=export_units)
        elif data_domain == 'TIME':
            exporter.create_transient_template(df_export_processed, data_domain, export_units=export_units)

