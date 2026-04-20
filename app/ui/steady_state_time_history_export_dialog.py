from __future__ import annotations

from collections import OrderedDict

import os

from PyQt5 import QtCore, QtGui, QtWebEngineWidgets, QtWidgets
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from .. import config_manager
from ..analysis.steady_state_time_history_export import (
    build_seconds_time_history_frame,
    build_time_history_csv_headers,
    convert_time_history_frame_for_export,
    resolve_frequency_to_hz,
)
from ..plotting.plotter import Plotter, load_fig_to_webview


class SteadyStateTimeHistoryExportDialog(QDialog):
    def __init__(
        self,
        parent=None,
        *,
        current_plot_data,
        interval_degrees: int,
        selected_frequency_value: float,
        selected_frequency_context,
        estimator_snapshot=None,
        selected_parts=None,
    ):
        super().__init__(parent)
        self._current_plot_data = OrderedDict(current_plot_data or {})
        self._interval_degrees = int(interval_degrees)
        self._selected_frequency_value = float(selected_frequency_value)
        self._selected_frequency_context = selected_frequency_context
        self._estimator_snapshot = estimator_snapshot
        self._selected_parts = list(selected_parts or [])
        self._trace_contexts = OrderedDict(
            (trace_name, trace_data.get("unit_context"))
            for trace_name, trace_data in self._current_plot_data.items()
        )
        self._plotter = getattr(parent, "plotter", None) or Plotter()
        self._family_selectors = OrderedDict()
        self._unknown_label_inputs = OrderedDict()
        self._seeded_cycle_text = (
            str(estimator_snapshot.estimate.rounded_cycle_count)
            if estimator_snapshot is not None
            else ""
        )
        self._setup_ui()
        self._refresh_preview()

    def _setup_ui(self):
        self.setWindowTitle("Steady-State Time-History Export")
        self.resize(1080, 840)

        summary_group = QGroupBox("Export Summary")
        summary_group.setStyleSheet(config_manager.GROUPBOX_STYLE)
        summary_layout = QFormLayout(summary_group)

        self.frequency_summary_label = QLabel(self._build_frequency_summary_text())
        self.frequency_summary_label.setWordWrap(True)
        summary_layout.addRow("Selected frequency", self.frequency_summary_label)

        parts_summary = ", ".join(self._selected_parts) if self._selected_parts else "Current plotted traces"
        self.parts_summary_label = QLabel(parts_summary)
        self.parts_summary_label.setWordWrap(True)
        summary_layout.addRow("Selected parts", self.parts_summary_label)

        self.interval_summary_label = QLabel(f"{self._interval_degrees} deg")
        summary_layout.addRow("Angular interval", self.interval_summary_label)

        self.cycles_input = QLineEdit(self._seeded_cycle_text)
        self.cycles_input.setValidator(QtGui.QIntValidator(1, 10_000_000, self))
        self.cycles_input.setPlaceholderText("Enter whole cycles")
        summary_layout.addRow("Cycles", self.cycles_input)

        self.cycle_source_label = QLabel()
        self.cycle_source_label.setWordWrap(True)
        summary_layout.addRow("", self.cycle_source_label)

        self.estimator_summary_label = QLabel(self._build_estimator_summary_text())
        self.estimator_summary_label.setWordWrap(True)
        self.estimator_summary_label.setVisible(bool(self.estimator_summary_label.text()))
        summary_layout.addRow("Estimator snapshot", self.estimator_summary_label)

        units_group = QGroupBox("Export Units")
        units_group.setStyleSheet(config_manager.GROUPBOX_STYLE)
        units_layout = QVBoxLayout(units_group)
        units_layout.addWidget(
            QLabel(
                "These selectors affect only this preview and export. They do not change the Settings tab."
            )
        )

        self.family_grid = QGridLayout()
        self.family_grid.setColumnStretch(1, 1)
        units_layout.addLayout(self.family_grid)
        self._populate_family_controls()

        self.unknown_units_group = QGroupBox("Unknown Unit Labels")
        self.unknown_units_group.setStyleSheet(config_manager.GROUPBOX_STYLE)
        unknown_layout = QFormLayout(self.unknown_units_group)
        for trace_name, context in self._trace_contexts.items():
            if context is not None and context.quantity_family != "unknown":
                continue
            initial_label = ""
            if context is not None:
                initial_label = context.display_unit or context.normalized_unit or ""
            line_edit = QLineEdit(initial_label)
            line_edit.setPlaceholderText("Optional CSV header label")
            line_edit.textChanged.connect(self._refresh_preview)
            unknown_layout.addRow(trace_name, line_edit)
            self._unknown_label_inputs[trace_name] = line_edit
        self.unknown_units_group.setVisible(bool(self._unknown_label_inputs))

        preview_group = QGroupBox("Preview")
        preview_group.setStyleSheet(config_manager.GROUPBOX_STYLE)
        preview_layout = QVBoxLayout(preview_group)
        self.preview_status_label = QLabel()
        self.preview_status_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_status_label)

        self.preview_plot = QtWebEngineWidgets.QWebEngineView()
        self.preview_plot.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        preview_layout.addWidget(self.preview_plot)

        button_row = QHBoxLayout()
        button_row.addStretch()
        self.export_button = QPushButton("Export CSV")
        self.close_button = QPushButton("Close")
        button_row.addWidget(self.export_button)
        button_row.addWidget(self.close_button)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(summary_group)
        main_layout.addWidget(units_group)
        main_layout.addWidget(self.unknown_units_group)
        main_layout.addWidget(preview_group, stretch=1)
        main_layout.addLayout(button_row)

        self.cycles_input.textChanged.connect(self._on_cycles_changed)
        self.export_button.clicked.connect(self._handle_export)
        self.close_button.clicked.connect(self.reject)
        self._update_cycle_source_note()

    def _populate_family_controls(self):
        row = 0

        time_selector = QComboBox()
        time_selector.addItem("s")
        time_selector.setCurrentText("s")
        time_selector.setEnabled(False)
        self._family_selectors["time"] = time_selector
        self.family_grid.addWidget(QLabel("Time"), row, 0)
        self.family_grid.addWidget(time_selector, row, 1)
        row += 1

        known_families = OrderedDict()
        for context in self._trace_contexts.values():
            if context is None or context.quantity_family == "unknown":
                continue
            known_families.setdefault(context.quantity_family, context)

        for family, context in known_families.items():
            selector = QComboBox()
            for unit_name in context.compatible_display_units:
                selector.addItem(unit_name)
            selector.setCurrentText(context.display_unit or context.normalized_unit or "")
            selector.currentIndexChanged.connect(self._refresh_preview)
            self._family_selectors[family] = selector
            self.family_grid.addWidget(QLabel(family.title()), row, 0)
            self.family_grid.addWidget(selector, row, 1)
            row += 1

    def _build_frequency_summary_text(self) -> str:
        frequency_hz = resolve_frequency_to_hz(
            self._selected_frequency_value,
            self._selected_frequency_context,
        )
        source_unit = None
        if self._selected_frequency_context is not None:
            source_unit = self._selected_frequency_context.normalized_unit

        if source_unit and source_unit != "Hz":
            return f"{self._selected_frequency_value:g} {source_unit} ({frequency_hz:g} Hz)"
        if source_unit == "Hz":
            return f"{self._selected_frequency_value:g} Hz"
        return f"{self._selected_frequency_value:g} (assumed Hz)"

    def _build_estimator_summary_text(self) -> str:
        if self._estimator_snapshot is None:
            return ""

        estimate = self._estimator_snapshot.estimate
        return (
            f"Damping ratio {estimate.damping_ratio:.5g}, residual transient "
            f"{estimate.residual_fraction * 100.0:.3g}%, recommended whole cycles "
            f"{estimate.rounded_cycle_count}, estimated run time {estimate.estimated_time_s:.6g} s."
        )

    def _on_cycles_changed(self):
        self._update_cycle_source_note()
        self._refresh_preview()

    def _update_cycle_source_note(self):
        cycle_text = self.cycles_input.text().strip()
        if self._estimator_snapshot is None:
            if cycle_text:
                self.cycle_source_label.setText("Using manual cycle entry.")
            else:
                self.cycle_source_label.setText(
                    "No prior estimator result is available. Enter the cycle count manually."
                )
            return

        estimate = self._estimator_snapshot.estimate
        if cycle_text == self._seeded_cycle_text:
            self.cycle_source_label.setText(
                "Cycles are prefilled from the last estimator result."
            )
            return

        if cycle_text:
            self.cycle_source_label.setText(
                f"Using manual cycle entry instead of the estimator recommendation of "
                f"{estimate.rounded_cycle_count} cycles."
            )
            return

        self.cycle_source_label.setText(
            "Cleared manual cycle entry. Enter a positive whole number of cycles."
        )

    def _parse_cycles(self) -> int:
        cycle_text = self.cycles_input.text().strip()
        if not cycle_text:
            raise ValueError("Please enter a positive whole number of cycles.")
        cycles = int(cycle_text)
        if cycles <= 0:
            raise ValueError("Cycles must be a positive whole number.")
        return cycles

    def _current_family_units(self):
        return {
            family: selector.currentText()
            for family, selector in self._family_selectors.items()
            if selector.currentText()
        }

    def _current_unknown_unit_labels(self):
        labels = {}
        for trace_name, line_edit in self._unknown_label_inputs.items():
            label = line_edit.text().strip()
            if "[" in label or "]" in label:
                raise ValueError(
                    f"Manual unit label for '{trace_name}' cannot contain '[' or ']'."
                )
            labels[trace_name] = label
        return labels

    def _build_preview_frame(self):
        cycles = self._parse_cycles()
        frequency_hz = resolve_frequency_to_hz(
            self._selected_frequency_value,
            self._selected_frequency_context,
        )
        base_frame = build_seconds_time_history_frame(
            self._current_plot_data,
            interval_degrees=self._interval_degrees,
            cycles=cycles,
            frequency_hz=frequency_hz,
        )
        converted_frame = convert_time_history_frame_for_export(
            base_frame,
            trace_contexts=self._trace_contexts,
            family_units=self._current_family_units(),
        )
        converted_frame.columns = build_time_history_csv_headers(
            list(converted_frame.columns),
            trace_contexts=self._trace_contexts,
            family_units=self._current_family_units(),
            manual_unknown_labels=self._current_unknown_unit_labels(),
        )
        return converted_frame, cycles, frequency_hz

    def _preview_y_axis_title(self, frame) -> str:
        trace_units = []
        for column_name in frame.columns:
            if column_name == "Time [s]":
                continue
            if " [" not in column_name or not column_name.endswith("]"):
                return "Value"
            trace_units.append(column_name.rsplit(" [", 1)[1][:-1])

        if len(set(trace_units)) == 1:
            return f"Value [{trace_units[0]}]"
        return "Value"

    def _refresh_preview(self):
        try:
            preview_frame, cycles, frequency_hz = self._build_preview_frame()
        except Exception as exc:
            self.preview_status_label.setText(str(exc))
            self.export_button.setEnabled(False)
            load_fig_to_webview(self._plotter.create_standard_figure({}, "", ""), self.preview_plot)
            return

        preview_plot_frame = preview_frame.set_index("Time [s]")
        preview_plot_frame.attrs["trace_units"] = {}
        for column_name in preview_plot_frame.columns:
            if " [" in column_name and column_name.endswith("]"):
                preview_plot_frame.attrs["trace_units"][column_name] = column_name.rsplit(" [", 1)[1][:-1]

        figure = self._plotter.create_standard_figure(
            preview_plot_frame,
            "Steady-State Time-History Preview",
            y_axis_title=self._preview_y_axis_title(preview_frame),
        )
        load_fig_to_webview(figure, self.preview_plot)

        row_count = len(preview_frame.index)
        end_time = preview_frame["Time [s]"].iloc[-1]
        self.preview_status_label.setText(
            f"{row_count} samples from 0 to {end_time:.6g} s across {cycles} cycle(s) "
            f"at {frequency_hz:.6g} Hz."
        )
        self.export_button.setEnabled(True)

    def _handle_export(self):
        try:
            export_frame, _, _ = self._build_preview_frame()
        except Exception as exc:
            QMessageBox.warning(self, "Invalid Export Settings", str(exc))
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Steady-State Time History",
            "steady_state_time_history_seconds.csv",
            "CSV Files (*.csv)",
        )
        if not save_path:
            return

        export_frame.to_csv(save_path, index=False)
        QMessageBox.information(
            self,
            "Export Successful",
            f"Steady-state time-history data saved to:\n{save_path}",
        )
        os.startfile(os.path.dirname(save_path))
