# File: app/controllers/plot_controller.py

import re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from PyQt5 import QtCore
from dataclasses import dataclass

from ..analysis.data_processing import (
    apply_data_section,
    apply_tukey_window,
    apply_low_pass_filter,
    compute_time_step_series,
    compute_sampling_rate_series,
    build_series_by_folder,
    build_dt_by_folder,
    build_fs_by_folder,
    build_multi_series_for_single,
)


@dataclass
class SingleDataOptions:
    selected_col: str
    section_enabled: bool
    section_min_text: str
    section_max_text: str
    filter_enabled: bool
    cutoff_frequency_text: str
    filter_order: int
    spectrum_enabled: bool
    num_slices_text: str
    plot_type: str
    colorscale: str


class PlotController(QtCore.QObject):
    # Constants for computed selections
    TIME_STEP_LABEL = 'Time Step (Δt)'
    FS_LABEL = 'Sampling Rate (Hz)'

    """
    Handles all logic for updating plots in response to UI changes.
    """
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.plotter = self.main_window.plotter

    def _get_df(self):
        return self.main_window.df

    def _get_compare_df(self):
        return self.main_window.df_compare

    def _get_common_columns(self):
        """
        Returns a sorted list of data columns that are present in
        BOTH the primary and comparison dataframes.
        """
        df = self._get_df()
        df_compare = self._get_compare_df()

        if df is None:
            # If primary isn't loaded, return empty
            return []

        # Get data columns from the primary dataframe (exclude metadata columns)
        excluded_cols = {'FREQ', 'TIME', 'NO', 'DataFolder'}
        data_cols_primary = [
            col for col in df.columns
            if col not in excluded_cols and not col.startswith('Phase_')
        ]

        if df_compare is None:
            # If compare isn't loaded, just return all primary columns
            # This handles the initial state before a comparison file is chosen.
            return sorted(data_cols_primary)

        # Both are loaded, find the intersection
        cols_compare = set(df_compare.columns)
        common_cols = [
            col for col in data_cols_primary
            if col in cols_compare
        ]

        return sorted(common_cols)

    def _get_data_domain(self):
        return self.main_window.data_domain

    def _get_plot_df(self, cols, source_df=None):
        """Prepares a DataFrame for plotting with the correct index."""
        df = self._get_df()
        if df is None:
            return pd.DataFrame()
            
        source_df = source_df if source_df is not None else df
        data_domain = self._get_data_domain()

        if not all(col in source_df.columns for col in [data_domain] + cols):
            return pd.DataFrame()

        x_label = 'Time [s]' if data_domain == 'TIME' else 'Freq [Hz]'
        x_data = source_df[data_domain]
        plot_df = source_df[cols].copy()
        plot_df.index = x_data
        plot_df.index.name = x_label
        return plot_df

    def _is_multi_folder(self) -> bool:
        df = self._get_df()
        try:
            return df is not None and 'DataFolder' in df.columns and df['DataFolder'].nunique() > 1
        except Exception:
            return False

    def _is_computed_metric(self, name: str) -> bool:
        return name in (self.TIME_STEP_LABEL, self.FS_LABEL)

    def _get_phase_col(self, col: str) -> str:
        return f'Phase_{col}'

    def _update_phase_plot_for_single(self, selected_col: str, is_multi_folder: bool) -> None:
        """Shows/hides the phase plot matching current behavior for Single Data tab."""
        df = self._get_df()
        tab = self.main_window.tab_single_data
        if self._is_computed_metric(selected_col):
            tab.set_phase_plot_visibility(False)
            return
        if self._get_data_domain() == 'FREQ' and not is_multi_folder:
            phase_col = self._get_phase_col(selected_col)
            if phase_col in df.columns:
                phase_df = self._get_plot_df([phase_col])
                phase_fig = self.plotter.create_standard_figure({phase_col: phase_df}, f'Phase of {selected_col}', 'Phase [deg]')
                tab.set_phase_plot_visibility(True)
                tab.display_phase_plot(phase_fig)
            else:
                tab.set_phase_plot_visibility(False)
        else:
            tab.set_phase_plot_visibility(False)

    def _snapshot_single_data_options(self) -> SingleDataOptions:
        tab = self.main_window.tab_single_data
        return SingleDataOptions(
            selected_col=tab.column_selector.currentText(),
            section_enabled=tab.section_checkbox.isChecked(),
            section_min_text=tab.section_min_input.text(),
            section_max_text=tab.section_max_input.text(),
            filter_enabled=tab.filter_checkbox.isChecked(),
            cutoff_frequency_text=tab.cutoff_frequency_input.text(),
            filter_order=tab.filter_order_input.value(),
            spectrum_enabled=tab.spectrum_checkbox.isChecked(),
            num_slices_text=tab.num_slices_input.text(),
            plot_type=tab.plot_type_selector.currentText(),
            colorscale=tab.colorscale_selector.currentText(),
        )

    # Additional snapshot dataclasses and methods for other tabs
    @dataclass
    class InterfaceDataOptions:
        interface: str
        side: str

    def _snapshot_interface_data_options(self) -> 'PlotController.InterfaceDataOptions':
        tab = self.main_window.tab_interface_data
        return PlotController.InterfaceDataOptions(
            interface=tab.interface_selector.currentText(),
            side=tab.side_selector.currentText(),
        )

    @dataclass
    class PartLoadsOptions:
        side: str
        exclude: bool
        section_enabled: bool
        section_min_text: str
        section_max_text: str
        tukey_enabled: bool
        tukey_alpha: float

    def _snapshot_part_loads_options(self) -> 'PlotController.PartLoadsOptions':
        tab = self.main_window.tab_part_loads
        return PlotController.PartLoadsOptions(
            side=tab.side_filter_selector.currentText(),
            exclude=tab.exclude_checkbox.isChecked(),
            section_enabled=tab.section_checkbox.isChecked(),
            section_min_text=tab.section_min_input.text(),
            section_max_text=tab.section_max_input.text(),
            tukey_enabled=tab.tukey_checkbox.isChecked(),
            tukey_alpha=tab.tukey_alpha_spin.value(),
        )

    @dataclass
    class CompareDataOptions:
        selected_column: str

    def _snapshot_compare_data_options(self) -> 'PlotController.CompareDataOptions':
        tab = self.main_window.tab_compare_data
        return PlotController.CompareDataOptions(
            selected_column=tab.compare_column_selector.currentText(),
        )

    @dataclass
    class ComparePartLoadsOptions:
        side: str
        exclude: bool

    def _snapshot_compare_part_loads_options(self) -> 'PlotController.ComparePartLoadsOptions':
        tab = self.main_window.tab_compare_part_loads
        return PlotController.ComparePartLoadsOptions(
            side=tab.side_filter_selector.currentText(),
            exclude=tab.exclude_checkbox.isChecked(),
        )

    @dataclass
    class TimeDomainRepresentOptions:
        frequency_text: str
        selected_side: str

    def _snapshot_time_domain_represent_options(self) -> 'PlotController.TimeDomainRepresentOptions':
        tab_time = self.main_window.tab_time_domain_represent
        # Side comes from Part Loads tab's side filter per existing behavior
        side = self.main_window.tab_part_loads.side_filter_selector.currentText()
        return PlotController.TimeDomainRepresentOptions(
            frequency_text=tab_time.data_point_selector.currentText(),
            selected_side=side,
        )

    def _should_exclude_component(self, col_name: str) -> bool:
        """
        Checks if a column should be excluded based on the T2/T3/R2/R3 filter,
        while correctly preserving resultants like 'T2/T3'.
        """
        # Match T2 but not T2/T3
        if re.search(r'\bT2\b', col_name) and not re.search(r'T2/T3', col_name):
            return True
        # Match T3 but not T2/T3
        if re.search(r'\bT3\b', col_name) and not re.search(r'T2/T3', col_name):
            return True
        # Match R2 but not R2/R3
        if re.search(r'\bR2\b', col_name) and not re.search(r'R2/R3', col_name):
            return True
        # Match R3 but not R2/R3
        if re.search(r'\bR3\b', col_name) and not re.search(r'R2/R3', col_name):
            return True
        return False

    def _filter_part_load_cols(self, all_columns, side, required_components, exclude):
        """
        A shared helper to filter DataFrame columns for part loads based on UI selections.
        """
        side_pattern = re.compile(rf'\b{re.escape(side)}\b')

        # Step 1: Find columns relevant to the selected side using a regex pattern.
        side_cols = [col for col in all_columns if side_pattern.search(col)]

        # Step 2: From those, find columns for the required components (e.g., 'T1', 'T2').
        component_cols = [col for col in side_cols if any(comp in col for comp in required_components)]

        # Step 3: Exclude any phase angle columns.
        final_cols = [col for col in component_cols if 'Phase_' not in col]

        # Step 4: If the exclude box is checked, remove T2, T3, R2, R3 (but keep resultants).
        if exclude:
            final_cols = [col for col in final_cols if not self._should_exclude_component(col)]

        return final_cols

    def _calculate_differences(self, columns):
        """Calculates the absolute difference between two dataframes for given columns,
           gracefully skipping columns not present in both dataframes."""
        df = self._get_df()
        df_compare = self._get_compare_df()
        data_domain = self._get_data_domain()

        if df is None or df_compare is None:
            return pd.DataFrame()

        diff_dict = {}
        for col in columns:
            # Explicitly check if the main column exists in BOTH dataframes first
            if col not in df.columns or col not in df_compare.columns:
                print(f"Skipping difference calculation for '{col}': Column not present in both datasets.")
                continue

            mag1, mag2 = df[col], df_compare[col]
            diff = np.nan  # Default to NaN difference if calculation fails

            if data_domain == 'FREQ':
                phase_col = f'Phase_{col}'
                # Check if phase columns exist in BOTH dataframes
                if phase_col in df.columns and phase_col in df_compare.columns:
                    try:
                        p1_rad = np.deg2rad(df[phase_col])
                        p2_rad = np.deg2rad(df_compare[phase_col])
                        # Ensure magnitudes are numeric before complex calculation
                        if pd.api.types.is_numeric_dtype(mag1) and pd.api.types.is_numeric_dtype(mag2):
                            diff = np.abs((mag1 * np.exp(1j * p1_rad)) - (mag2 * np.exp(1j * p2_rad)))
                        else:
                            print(f"Skipping complex diff for '{col}': Non-numeric magnitude data.")
                    except Exception as e:
                        print(f"Error calculating complex difference for '{col}': {e}")
                else:
                    # Fallback to magnitude difference only if phase columns aren't BOTH present
                    try:
                        if pd.api.types.is_numeric_dtype(mag1) and pd.api.types.is_numeric_dtype(mag2):
                            diff = np.abs(mag1 - mag2)
                        else:
                            print(f"Skipping simple diff for '{col}': Non-numeric magnitude data.")
                    except Exception as e:
                        print(f"Error calculating simple difference for '{col}': {e}")

            else:  # TIME domain
                try:
                    if pd.api.types.is_numeric_dtype(mag1) and pd.api.types.is_numeric_dtype(mag2):
                        diff = np.abs(mag1 - mag2)
                    else:
                        print(f"Skipping time diff for '{col}': Non-numeric magnitude data.")
                except Exception as e:
                    print(f"Error calculating time difference for '{col}': {e}")

            # Only add to dict if calculation was successful (not NaN)
            if not pd.isna(diff).all():  # Check if the entire series is not NaN
                diff_dict[f'Δ {col}'] = diff
            else:
                print(f"Failed to calculate valid difference for '{col}'.")

        # Return an empty DataFrame if no valid differences were calculated
        return pd.DataFrame(diff_dict) if diff_dict else pd.DataFrame()

    # region Signal Slots
    @QtCore.pyqtSlot()
    def update_all_plots_from_settings(self):
        if self._get_df() is None: return

        settings_tab = self.main_window.tab_settings
        self.plotter.legend_font_size = int(settings_tab.legend_font_size_selector.currentText())
        self.plotter.default_font_size = int(settings_tab.default_font_size_selector.currentText())
        self.plotter.hover_font_size = int(settings_tab.hover_font_size_selector.currentText())
        self.plotter.hover_mode = settings_tab.hover_mode_selector.currentText()
        try:
            self.plotter.trace_opacity = float(settings_tab.opacity_spin.value())
        except Exception:
            self.plotter.trace_opacity = 1.0

        self.update_single_data_plots()
        self.update_interface_data_plots()
        self.update_part_loads_plots()
        self.update_time_domain_represent_plot()
        self.update_compare_data_plots()
        self.update_compare_part_loads_plots()

    @QtCore.pyqtSlot()
    def update_single_data_plots(self):
        df = self._get_df()
        if df is None: return
        tab = self.main_window.tab_single_data
        opts = self._snapshot_single_data_options()
        selected_col = opts.selected_col
        if not selected_col: return

        is_multi_folder = self._is_multi_folder()
        # Use builders to construct the plot data map
        if self._get_data_domain() == 'TIME' and selected_col == self.TIME_STEP_LABEL:
            dfs_for_plot = build_dt_by_folder(df, section_enabled=opts.section_enabled,
                                              t_min_text=opts.section_min_text, t_max_text=opts.section_max_text)
            # Key for single-folder case should be selected_col to keep legend titles consistent
            if not is_multi_folder and dfs_for_plot:
                only_key = next(iter(dfs_for_plot))
                dfs_for_plot = {selected_col: dfs_for_plot[only_key]}
        elif self._get_data_domain() == 'TIME' and selected_col == self.FS_LABEL:
            dfs_for_plot = build_fs_by_folder(df, section_enabled=opts.section_enabled,
                                              t_min_text=opts.section_min_text, t_max_text=opts.section_max_text)
            if not is_multi_folder and dfs_for_plot:
                only_key = next(iter(dfs_for_plot))
                dfs_for_plot = {selected_col: dfs_for_plot[only_key]}
        else:
            dfs_for_plot = build_series_by_folder(
                df,
                selected_col=selected_col,
                data_domain=self._get_data_domain(),
                section_enabled=opts.section_enabled,
                t_min_text=opts.section_min_text,
                t_max_text=opts.section_max_text,
                filter_enabled=opts.filter_enabled,
                cutoff_text=opts.cutoff_frequency_text,
                filter_order=opts.filter_order,
            )

        plot_title = f"{selected_col} Plot"
        if selected_col == self.TIME_STEP_LABEL:
            fig = self.plotter.create_standard_figure(dfs_for_plot, title=self.TIME_STEP_LABEL, y_axis_title='Time Step [s]')
        elif selected_col == self.FS_LABEL:
            fig = self.plotter.create_standard_figure(dfs_for_plot, title=self.FS_LABEL, y_axis_title='Sampling Rate [Hz]')
        elif self.main_window.tab_settings.rolling_min_max_checkbox.isChecked() and self._get_data_domain() == 'TIME':
            try:
                points = int(self.main_window.tab_settings.desired_num_points_input.text())
                as_bars = self.main_window.tab_settings.plot_as_bars_checkbox.isChecked()
                fig = self.plotter.create_rolling_envelope_figure(dfs_for_plot, plot_title, points, as_bars)
            except ValueError:
                fig = self.plotter.create_standard_figure(dfs_for_plot, title=f"{plot_title} (Invalid Points)")
        else:
            fig = self.plotter.create_standard_figure(dfs_for_plot, title=plot_title)
        tab.display_regular_plot(fig)

        self._update_phase_plot_for_single(selected_col, is_multi_folder)

        if self._get_data_domain() == 'TIME' and opts.spectrum_enabled and not is_multi_folder:
            self.update_spectrum_plot_only()

    @QtCore.pyqtSlot()
    def update_interface_data_plots(self):
        df = self._get_df()
        if df is None: return
        tab = self.main_window.tab_interface_data
        opts = self._snapshot_interface_data_options()
        interface = opts.interface
        side = opts.side
        if not interface or not side: return

        t_cols = [c for c in df.columns if c.startswith(interface) and side in c and any(s in c for s in ['T1', 'T2', 'T3', 'T2/T3']) and 'Phase_' not in c]
        r_cols = [c for c in df.columns if c.startswith(interface) and side in c and any(s in c for s in ['R1', 'R2', 'R3', 'R2/R3']) and 'Phase_' not in c]

        t_df = build_multi_series_for_single(
            df,
            columns=t_cols,
            data_domain=self._get_data_domain(),
            section_enabled=False,
        )
        r_df = build_multi_series_for_single(
            df,
            columns=r_cols,
            data_domain=self._get_data_domain(),
            section_enabled=False,
        )

        tab.display_t_series_plot(self.plotter.create_standard_figure(t_df, f'Translational Components - {side}'))
        tab.display_r_series_plot(self.plotter.create_standard_figure(r_df, f'Rotational Components - {side}'))

    @QtCore.pyqtSlot()
    def update_part_loads_plots(self):
        df = self._get_df()
        if df is None: return
        opts = self._snapshot_part_loads_options()
        tab = self.main_window.tab_part_loads
        side = opts.side
        if not side: return

        exclude = opts.exclude
        df_processed = df.copy()

        # Call helper functions for data processing
        if self._get_data_domain() == 'TIME':
            if opts.section_enabled:
                df_processed = apply_data_section(df_processed, opts.section_min_text, opts.section_max_text)

            if opts.tukey_enabled:
                df_processed = apply_tukey_window(df_processed, opts.tukey_alpha)

        # Filter columns from the (potentially) processed DataFrame
        t_cols = self._filter_part_load_cols(df_processed.columns, side, ['T1', 'T2', 'T3', 'T2/T3'], exclude)
        r_cols = self._filter_part_load_cols(df_processed.columns, side, ['R1', 'R2', 'R3', 'R2/R3'], exclude)

        # Use the processed DataFrame as the source for the plots (single-folder builder)
        t_df = build_multi_series_for_single(
            df_processed,
            columns=t_cols,
            data_domain=self._get_data_domain(),
            section_enabled=False,
            tukey_enabled=False,
        )
        r_df = build_multi_series_for_single(
            df_processed,
            columns=r_cols,
            data_domain=self._get_data_domain(),
            section_enabled=False,
            tukey_enabled=False,
        )
        tab.display_t_series_plot(self.plotter.create_standard_figure(t_df, f'Translational Components - {side}'))
        tab.display_r_series_plot(self.plotter.create_standard_figure(r_df, f'Rotational Components- {side}'))
    
    @QtCore.pyqtSlot()
    def update_time_domain_represent_plot(self):
        df = self._get_df()
        if df is None or self._get_data_domain() != 'FREQ': return
        
        tab = self.main_window.tab_time_domain_represent
        try:
            opts = self._snapshot_time_domain_represent_options()
            freq_text = opts.frequency_text
            if not freq_text or "Select a frequency" in freq_text: return
            freq = float(freq_text)

            selected_side = opts.selected_side
            if not selected_side:
                tab.display_plot(go.Figure())
                return

            side_pattern = re.compile(rf'\b{re.escape(selected_side)}\b')
            plot_cols = [c for c in df.columns if side_pattern.search(c) and not c.startswith('Phase_') and
                         any(s in c for s in ['T1', 'T2', 'T3', 'R1', 'R2', 'R3', 'T2/T3', 'R2/R3'])]

            theta = np.linspace(0, 360, 361)
            rads = np.radians(theta)
            plot_data = {}
            tab.current_plot_data = {}
            data_at_freq = df[df['FREQ'] == freq].iloc[0]

            for col in plot_cols:
                phase_col = f'Phase_{col}'
                if phase_col in data_at_freq:
                    amplitude = data_at_freq[col]
                    phase_deg = data_at_freq[phase_col]
                    y_data = amplitude * np.cos(rads - np.radians(phase_deg))
                    plot_data[col] = y_data
                    tab.current_plot_data[col] = {'theta': theta, 'y_data': y_data}
            
            df_time_domain = pd.DataFrame(plot_data, index=theta)
            df_time_domain.index.name = "Theta [deg]"
            
            title = f'Time Domain Representation at {freq} Hz for {selected_side}'
            fig = self.plotter.create_standard_figure(df_time_domain, title)
            tab.display_plot(fig)

        except (ValueError, IndexError) as e:
            print(f"Could not update time domain representation plot: {e}")
            tab.display_plot(go.Figure())

    @QtCore.pyqtSlot()
    def update_compare_column_list(self):
        """
        Fetches the common columns and tells the UI
        to repopulate the compare_column_selector.
        """
        common_columns = self._get_common_columns()
        self.main_window.tab_compare_data.update_column_selector(common_columns)

    @QtCore.pyqtSlot()
    def update_compare_data_plots(self):
        if self._get_df() is None or self._get_compare_df() is None: return
        tab = self.main_window.tab_compare_data
        selected_column = tab.compare_column_selector.currentText()
        if not selected_column: return

        df1 = self._get_plot_df([selected_column])
        df2 = self._get_plot_df([selected_column], source_df=self._get_compare_df())
        
        fig_compare = self.plotter.create_comparison_figure(df1, df2, selected_column, f'{selected_column} Comparison')
        tab.display_comparison_plot(fig_compare)
        
        diff_df = self._calculate_differences([selected_column])
        if diff_df.empty: return

        # Build plot-ready DataFrame with domain index for absolute difference
        domain_col = self._get_data_domain()
        abs_diff_df = pd.DataFrame({'Absolute Difference': diff_df.iloc[:, 0].values})
        abs_diff_df.index = self._get_df()[domain_col]
        abs_diff_df.index.name = 'Time [s]' if domain_col == 'TIME' else 'Freq [Hz]'
        fig_abs_diff = self.plotter.create_standard_figure(abs_diff_df,
                                                           f'{selected_column} Absolute Difference')
        tab.display_absolute_diff_plot(fig_abs_diff)
        
        with np.errstate(divide='ignore', invalid='ignore'):
            relative_diff = np.divide(100 * diff_df.iloc[:, 0], np.abs(self._get_df()[selected_column]))
            relative_diff.fillna(0, inplace=True)
        rel_diff_df = pd.DataFrame({'Relative Difference (%)': relative_diff.values})
        rel_diff_df.index = self._get_df()[domain_col]
        rel_diff_df.index.name = 'Time [s]' if domain_col == 'TIME' else 'Freq [Hz]'
        fig_rel_diff = self.plotter.create_standard_figure(rel_diff_df,
                                                           f'{selected_column} Relative Difference (%)', "Percent (%)")
        tab.display_relative_diff_plot(fig_rel_diff)

    @QtCore.pyqtSlot()
    def update_compare_part_loads_plots(self):
        if self._get_df() is None or self._get_compare_df() is None: return
        tab = self.main_window.tab_compare_part_loads
        selected_side = tab.side_filter_selector.currentText()
        if not selected_side: return

        exclude = tab.exclude_checkbox.isChecked()

        t_cols = self._filter_part_load_cols(self._get_df().columns, selected_side,
                                             ["T1", "T2", "T3", "T2/T3"], exclude)
        r_cols = self._filter_part_load_cols(self._get_df().columns, selected_side,
                                             ["R1", "R2", "R3", "R2/R3"], exclude)

        # Build plot-ready DataFrames with domain index for differences
        domain_col = self._get_data_domain()
        t_diff = self._calculate_differences(t_cols)
        r_diff = self._calculate_differences(r_cols)
        t_diff_df = pd.DataFrame(t_diff) if not t_diff.empty else pd.DataFrame()
        r_diff_df = pd.DataFrame(r_diff) if not r_diff.empty else pd.DataFrame()
        if not t_diff_df.empty:
            t_diff_df.index = self._get_df()[domain_col]
            t_diff_df.index.name = 'Time [s]' if domain_col == 'TIME' else 'Freq [Hz]'
        if not r_diff_df.empty:
            r_diff_df.index = self._get_df()[domain_col]
            r_diff_df.index.name = 'Time [s]' if domain_col == 'TIME' else 'Freq [Hz]'
        
        fig_t = self.plotter.create_standard_figure(t_diff_df,
                                                    f'Translational Components, Difference (Δ) - {selected_side}')
        tab.display_t_series_plot(fig_t)
        
        fig_r = self.plotter.create_standard_figure(r_diff_df,
                                                    f'Rotational Components, Difference (Δ) - {selected_side}')
        tab.display_r_series_plot(fig_r)

    @QtCore.pyqtSlot()
    def update_spectrum_plot_only(self):
        """A dedicated function that only updates the spectrum plot."""
        df = self._get_df()
        if df is None or self._get_data_domain() != 'TIME': return

        tab = self.main_window.tab_single_data
        opts = self._snapshot_single_data_options()
        selected_col = opts.selected_col
        if not selected_col or selected_col in (self.TIME_STEP_LABEL, self.FS_LABEL) or not opts.spectrum_enabled: return

        is_multi_folder = self._is_multi_folder()
        if is_multi_folder: return

        try:
            # Re-create the source DataFrame for the spectrum plot
            source_df = df
            # Apply Section Data before spectrum if enabled
            if opts.section_enabled:
                source_df = apply_data_section(source_df, opts.section_min_text, opts.section_max_text)
            plot_df = self._get_plot_df([selected_col], source_df=source_df)
            if opts.filter_enabled:
                try:
                    cutoff = float(opts.cutoff_frequency_text)
                    order = opts.filter_order
                    plot_df = apply_low_pass_filter(plot_df, selected_col, cutoff, order)
                except ValueError:
                    pass # Ignore if cutoff is not a valid number

            # Generate and display the spectrum plot
            fig_spec = self.plotter.create_spectrum_figure(
                plot_df,
                num_slices=int(opts.num_slices_text),
                plot_type=opts.plot_type,
                colorscale=opts.colorscale
            )
            tab.set_spectrum_plot_visibility(True)
            tab.display_spectrum_plot(fig_spec)
        except (ValueError, IndexError, ZeroDivisionError) as e:
            print(f"Could not generate spectrum: {e}")
            tab.set_spectrum_plot_visibility(False)
    # endregion