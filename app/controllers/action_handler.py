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

from ..analysis.ansys_exporter import AnsysExporter
from ..analysis.data_processing import apply_data_section, apply_tukey_window


class ActionHandler(QtCore.QObject):
    """
    Handles complex user-initiated actions like data exports.
    """
    def __init__(self, main_window, data_manager, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.data_manager = data_manager

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
            theta_points = [i * interval for i in range(num_points + 1)]
            data_dict = {'Theta': theta_points}

            for col, plot_data in tab.current_plot_data.items():
                full_theta = plot_data['theta']
                full_y_data = plot_data['y_data']
                sampled_y_data = [full_y_data[theta] for theta in theta_points]
                data_dict[col] = sampled_y_data

            df_to_export = pd.DataFrame(data_dict)

            save_path, _ = QFileDialog.getSaveFileName(
                self.main_window, "Save Extracted Data", "extracted_time_represent_data.csv", "CSV Files (*.csv)"
            )

            if save_path:
                df_to_export.to_csv(save_path, index=False)
                QMessageBox.information(self.main_window, "Export Successful", f"Data successfully saved to:\n{save_path}")
                os.startfile(os.path.dirname(save_path))

        except (ValueError, KeyError) as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred during data extraction: {e}")

    @QtCore.pyqtSlot()
    def handle_ansys_export(self):
        """Controller slot to manage the Ansys export process."""
        df = self.main_window.df
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

        df_combined_converted = pd.DataFrame()
        for side in selected_sides:
            side_pattern = re.compile(rf'\b{re.escape(side)}\b')
            side_cols_to_keep = [data_domain]
            side_cols_to_keep.extend([c for c in df_processed.columns if side_pattern.search(c)])
            df_part_processed = df_processed[list(OrderedDict.fromkeys(side_cols_to_keep))]

            df_part_processed.to_csv(f"extracted_data_for_{side}_in_original_units.csv", index=False)

            df_part_converted = df_part_processed.copy()
            for col in df_part_converted.columns:
                if col not in [data_domain, 'NO'] and not col.startswith('Phase_'):
                    df_part_converted[col] *= 1000
            df_part_converted.to_csv(f"extracted_{side}_loads_multiplied_by_1000.csv", index=False)

            if df_combined_converted.empty:
                df_combined_converted = df_part_converted
            else:
                df_to_concat = df_part_converted.drop(columns=[data_domain])
                df_combined_converted = pd.concat([df_combined_converted, df_to_concat], axis=1)

        df_combined_converted.to_csv("extracted_loads_of_all_selected_parts_in_converted_units.csv", index=False)

        exporter = AnsysExporter(version=selected_version, ansys_base_path=ansys_base_path)
        if data_domain == 'FREQ':
            exporter.create_harmonic_template(df_processed, data_domain)
        elif data_domain == 'TIME':
            time_diffs = df['TIME'].diff().dropna()
            sample_rate = 1 / time_diffs.mean() if not time_diffs.empty else 0
            exporter.create_transient_template(df_processed, data_domain, sample_rate)

