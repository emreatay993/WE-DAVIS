# File: app/data_manager.py

import os
import sys
import pandas as pd
import re
from dataclasses import dataclass
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from .units import ColumnUnitContext, build_unit_contexts


@dataclass(frozen=True)
class PldHeaderMetadata:
    interface_labels: list[str]
    interface_units: list[str | None]
    phase_unit: str | None
    domain_units: dict[str, str | None]


class DataManager(QtCore.QObject):
    """
    Handles all data loading, parsing, and management.
    Emits a signal when data is successfully loaded.
    """
    dataLoaded = QtCore.pyqtSignal(pd.DataFrame, str, str, object)
    dataLoadFailed = QtCore.pyqtSignal(str)
    comparisonDataLoaded = QtCore.pyqtSignal(pd.DataFrame, object)
    loadingProgress = QtCore.pyqtSignal(int, int, str)  # (current_index, total_folders, folder_name)

    def __init__(self, parent=None):
        super().__init__(parent)

    def load_data_from_directory(self):
        folder = self._select_directory('Please select a directory for raw data and headers')
        if not folder:
            sys.exit(1)

        # This initial load is just a special case of loading from a list of paths
        self.load_data_from_paths([folder])

    ## The core method for handling single or multiple folder selections
    def load_data_from_paths(self, folder_paths):
        """
        Loads data from a list of folder paths, validates them, combines them,
        and emits the result.
        """
        combined_dfs = []
        combined_unit_context = {}
        data_domain = None  # Determined by the first valid folder
        first_valid_folder = None

        total_folders = len(folder_paths)
        for idx, folder in enumerate(folder_paths, start=1):
            # Emit progress signal
            folder_name = os.path.basename(folder)
            self.loadingProgress.emit(idx, total_folders, folder_name)
            
            try:
                # 1. Validate folder contents
                full_pld_files = self._get_file_path(folder, 'full.pld')
                max_pld_files = self._get_file_path(folder, 'max.pld')

                if not full_pld_files or not max_pld_files:
                    QMessageBox.warning(None, "Invalid Folder",
                                        f"Folder '{os.path.basename(folder)}' is missing required .pld files. Skipping.")
                    continue

                # 2. Read and determine domain for this folder
                df_temp, current_domain, unit_context = self._load_pld_dataset(
                    full_pld_files,
                    max_pld_files[0],
                    data_folder=os.path.basename(folder),
                )

                # 3. Validate Domain Consistency
                if data_domain is None:  # First valid folder sets the domain
                    data_domain = current_domain
                    first_valid_folder = folder
                elif current_domain != data_domain:
                    QMessageBox.warning(None, "Domain Mismatch",
                                        f"Folder '{os.path.basename(folder)}' has domain '{current_domain}' but expected '{data_domain}'. Skipping.")
                    continue

                # 4. Merge per-folder unit metadata for the final combined frame
                for column_name, column_context in unit_context.items():
                    combined_unit_context.setdefault(column_name, column_context)
                combined_dfs.append(df_temp)

            except ValueError as e:
                QMessageBox.warning(None, "Invalid Data",
                                    f"Data in '{os.path.basename(folder)}' is invalid. Skipping.\n{e}")
                continue
            except Exception as e:
                QMessageBox.critical(None, "Load Error", f"Failed to load data from '{os.path.basename(folder)}':\n{e}")
                continue  # Skip to the next folder

        if not combined_dfs:
            self.dataLoadFailed.emit("No valid data could be loaded from the selected folder(s).")
            return

        # Concatenate all valid DataFrames
        final_df = pd.concat(combined_dfs, ignore_index=True)

        # Sort the final DataFrame by the domain column
        final_df = final_df.sort_values(by=data_domain).reset_index(drop=True)
        final_unit_context = self._align_unit_context_to_columns(final_df.columns, combined_unit_context)

        # Emit the signal with the combined results
        self.dataLoaded.emit(final_df, data_domain, first_valid_folder, final_unit_context)


    def _build_column_layout(self, header_metadata, data_domain, column_count):
        """Determines the final column layout and unit context for a loaded dataset."""
        column_names = ['NO', data_domain]
        source_units_by_column = {
            'NO': None,
            data_domain: header_metadata.domain_units.get(data_domain),
        }
        family_hints_by_column = {}

        if data_domain == 'FREQ':
            for label, unit in zip(header_metadata.interface_labels, header_metadata.interface_units):
                column_names.append(label)
                source_units_by_column[label] = unit

                phase_label = f"Phase_{label}"
                column_names.append(phase_label)
                source_units_by_column[phase_label] = header_metadata.phase_unit
                if header_metadata.phase_unit is not None:
                    family_hints_by_column[phase_label] = 'phase'
        elif data_domain == 'TIME':
            for label, unit in zip(header_metadata.interface_labels, header_metadata.interface_units):
                column_names.append(label)
                source_units_by_column[label] = unit

        additional_cols = column_count - len(column_names)
        if additional_cols > 0:
            for index in range(1, additional_cols + 1):
                extra_column_name = f"Extra_Column_{index}"
                column_names.append(extra_column_name)
                source_units_by_column[extra_column_name] = None

        column_names = column_names[:column_count]
        source_units_by_column = {
            column_name: source_units_by_column.get(column_name)
            for column_name in column_names
        }
        family_hints_by_column = {
            column_name: family_hints_by_column[column_name]
            for column_name in column_names
            if column_name in family_hints_by_column
        }
        unit_context = build_unit_contexts(
            source_units_by_column,
            family_hints_by_column=family_hints_by_column,
        )
        return column_names, unit_context

    def _select_directory(self, title):
        folder = QFileDialog.getExistingDirectory(None, title)
        return folder

    def _get_file_path(self, folder, file_suffix):
        return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(file_suffix)]

    def _read_pld_log_file(self, file_path):
        df = pd.read_csv(file_path, delimiter='|', skipinitialspace=True, skip_blank_lines=True)
        df = df.dropna(how='all').dropna(axis=1, how='all')
        df.columns = [str(column_name).strip() for column_name in df.columns]
        df = df.loc[:, ~df.columns.str.startswith('Unnamed:')]

        interface_labels = []
        interface_units = []
        if 'Interface Label' in df.columns:
            metadata_rows = df[df['Interface Label'].notna()].copy()
            interface_labels = metadata_rows['Interface Label'].astype(str).str.strip().tolist()
            if 'UNIT' in metadata_rows.columns:
                interface_units = [self._clean_header_value(value) for value in metadata_rows['UNIT'].tolist()]
            else:
                interface_units = [None] * len(interface_labels)

        domain_units = {}
        phase_unit = None
        for column_name in df.columns:
            normalized_name, unit = self._parse_metadata_column(column_name)
            if unit is None:
                continue
            if normalized_name == 'PHASE':
                phase_unit = unit
            elif normalized_name in {'FREQ', 'TIME'}:
                domain_units[normalized_name] = unit

        return PldHeaderMetadata(
            interface_labels=interface_labels,
            interface_units=interface_units,
            phase_unit=phase_unit,
            domain_units=domain_units,
        )

    def _read_pld_file(self, file_path):
        df = pd.read_csv(file_path, delimiter='|', skipinitialspace=True, skip_blank_lines=True, comment='_', low_memory=False)
        df = df.apply(pd.to_numeric)
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')
        df.columns = df.columns.str.strip()
        df.reset_index(drop=True, inplace=True)
        return df

    def _load_pld_dataset(self, full_pld_files, max_pld_file, data_folder=None):
        dfs = [self._read_pld_file(path) for path in full_pld_files]
        df = pd.concat(dfs, ignore_index=True)
        data_domain = self._detect_data_domain(df)

        header_metadata = self._read_pld_log_file(max_pld_file)
        column_names, unit_context = self._build_column_layout(header_metadata, data_domain, len(df.columns))
        df.columns = column_names

        if data_folder is not None:
            df['DataFolder'] = data_folder

        unit_context = self._align_unit_context_to_columns(df.columns, unit_context)
        return df, data_domain, unit_context

    def _detect_data_domain(self, df):
        if 'FREQ' in df.columns:
            return 'FREQ'
        if 'TIME' in df.columns:
            return 'TIME'
        raise ValueError("Dataset has no TIME or FREQ column.")

    def _align_unit_context_to_columns(self, column_names, unit_context):
        return {
            column_name: unit_context.get(column_name, ColumnUnitContext.from_source_unit(column_name, None))
            for column_name in column_names
        }

    def _clean_header_value(self, value):
        if pd.isna(value):
            return None
        cleaned_value = str(value).strip()
        return cleaned_value or None

    def _parse_metadata_column(self, column_name):
        match = re.match(r'^(?P<label>[^()]+?)\s*\((?P<unit>[^()]+)\)\s*$', column_name.strip())
        if not match:
            return column_name.strip().upper(), None
        return match.group('label').strip().upper(), self._clean_header_value(match.group('unit'))

    def load_comparison_data(self):
        """Loads a secondary dataset for comparison purposes."""
        folder = self._select_directory('Please select a directory for COMPARISON data')
        if not folder:
            return

        try:
            # This logic is identical to the initial load, but simplified
            file_path_full_data = self._get_file_path(folder, 'full.pld')
            file_path_headers_data = self._get_file_path(folder, 'max.pld')

            if not file_path_full_data or not file_path_headers_data:
                QMessageBox.critical(None, 'Error', "No required files found in comparison folder.")
                return

            df_compare, _, unit_context_compare = self._load_pld_dataset(
                file_path_full_data,
                file_path_headers_data[0],
            )
            self.comparisonDataLoaded.emit(df_compare, unit_context_compare)

        except Exception as e:
            QMessageBox.critical(None, 'Error', f"An error occurred loading comparison data: {str(e)}")
