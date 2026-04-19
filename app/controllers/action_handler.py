# File: app/controllers/action_handler.py

import os
import re
from collections import OrderedDict

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QAbstractItemView,
                             QListWidgetItem, QHBoxLayout, QPushButton, QMessageBox,
                             QFileDialog, QComboBox, QLabel, QGroupBox)
from scipy.signal.windows import tukey

from ..analysis.ansys_exporter import AnsysExportUnits, AnsysExporter
from ..analysis.data_processing import apply_data_section, apply_tukey_window
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
        """Returns list of possible ANSYS installation base paths to search."""
        paths = []
        
        # Check all available drive letters
        for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            paths.append(rf"{drive}:\Program Files\ANSYS Inc")
            paths.append(rf"{drive}:\ANSYS Inc")
            paths.append(rf"{drive}:\Ansys")
        
        # Also check environment variables that might point to ANSYS
        for env_var in os.environ:
            if 'ANSYS' in env_var.upper() or 'AWP_ROOT' in env_var.upper():
                env_path = os.environ[env_var]
                if os.path.isdir(env_path):
                    # Get parent directory in case env points to version folder
                    parent = os.path.dirname(env_path)
                    if parent not in paths:
                        paths.append(parent)
                    if env_path not in paths:
                        paths.append(env_path)
        
        return paths

    def _get_available_ansys_versions(self):
        """Scans for available ANSYS versions across all possible installation directories."""
        available_versions = {}  # version -> base_path mapping
        
        for ansys_base_path in self._get_ansys_base_paths():
            if os.path.exists(ansys_base_path):
                try:
                    for item in os.listdir(ansys_base_path):
                        if item.startswith('v') and os.path.isdir(os.path.join(ansys_base_path, item)):
                            # Extract version number (e.g., 'v232' -> 232)
                            version_num = item[1:]  # Remove 'v' prefix
                            if version_num.isdigit():
                                version = int(version_num)
                                # Store with the base path (first found wins)
                                if version not in available_versions:
                                    available_versions[version] = ansys_base_path
                except Exception as e:
                    print(f"Error scanning ANSYS versions in {ansys_base_path}: {e}")
        
        # Store the paths for later use
        self._ansys_version_paths = available_versions
        
        # Return sorted list of versions (latest first)
        return sorted(available_versions.keys(), reverse=True)

    def _get_sides_for_export(self):
        """Creates and shows a dialog to select multiple sides for export and ANSYS version."""
        all_sides = [self.main_window.tab_part_loads.side_filter_selector.itemText(i) for i in
                     range(self.main_window.tab_part_loads.side_filter_selector.count())]
        current_side = self.main_window.tab_part_loads.side_filter_selector.currentText()

        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Select Parts to Export")
        layout = QVBoxLayout(dialog)
        
        # Parts selection group
        parts_group = QGroupBox("Select Parts")
        parts_layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        for side in all_sides:
            item = QListWidgetItem(side)
            list_widget.addItem(item)
            if side == current_side:
                item.setSelected(True)
        
        parts_layout.addWidget(list_widget)
        parts_group.setLayout(parts_layout)
        
        # ANSYS version selection group
        version_group = QGroupBox("ANSYS Version")
        version_layout = QVBoxLayout()
        version_combo = QComboBox()
        
        available_versions = self._get_available_ansys_versions()
        
        if available_versions:
            for version in available_versions:
                # Store both version and path as tuple in item data
                base_path = self._ansys_version_paths.get(version, r"C:\Program Files\ANSYS Inc")
                version_combo.addItem(f"ANSYS v{version} ({base_path})", (version, base_path))
            version_combo.setCurrentIndex(0)  # Select latest version by default
        else:
            version_combo.addItem("Use Latest Available", (None, None))
        
        version_layout.addWidget(QLabel("Select ANSYS version for template generation:"))
        version_layout.addWidget(version_combo)
        version_group.setLayout(version_layout)

        # Buttons
        button_layout = QHBoxLayout()
        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        layout.addWidget(parts_group)
        layout.addWidget(version_group)
        layout.addLayout(button_layout)

        if dialog.exec_() == QDialog.Accepted:
            selected_sides = [item.text() for item in list_widget.selectedItems()]
            version_data = version_combo.currentData()  # (version, base_path) tuple
            return selected_sides, version_data
        return None, (None, None)

    @QtCore.pyqtSlot()
    def handle_compare_data_selection(self):
        """Handles the request to load comparison data."""
        self.data_manager.load_comparison_data()

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
            data_dict = {'Theta': exported_theta.tolist()}
            display_context_map = self._get_display_context_map()

            for col, plot_data in tab.current_plot_data.items():
                full_y_data = pd.Series(plot_data['y_data'], copy=True).iloc[sample_indices].reset_index(drop=True)
                column_context = display_context_map.get(col)
                exported_y_data = self._convert_display_series_to_export_mode(full_y_data, column_context)
                data_dict[col] = exported_y_data.tolist()

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
                    f"Data successfully saved in {self._get_export_mode_label()} mode to:\n{save_path}",
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

        selected_sides, version_data = self._get_sides_for_export()
        if not selected_sides:
            return
        
        selected_version, ansys_base_path = version_data

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

