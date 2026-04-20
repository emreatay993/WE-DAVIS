# File: app/controllers/plot_controller.py

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PyQt5 import QtCore

from ..analysis.data_processing import (
    apply_data_section,
    apply_low_pass_filter,
    apply_tukey_window,
    build_dt_by_folder,
    build_fs_by_folder,
    build_multi_series_for_single,
    build_series_by_folder,
)
from ..units import ColumnUnitContext, convert_scalar, convert_series


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
    DELTA_SYMBOL = "\u0394"
    TIME_STEP_LABEL = f"Time Step ({DELTA_SYMBOL}t)"
    FS_LABEL = "Sampling Rate (Hz)"

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

    def _get_raw_df(self):
        raw_df = getattr(self.main_window, "raw_primary_df", None)
        return raw_df if raw_df is not None else self._get_df()

    def _get_raw_compare_df(self):
        raw_df = getattr(self.main_window, "raw_comparison_df", None)
        return raw_df if raw_df is not None else self._get_compare_df()

    def _get_unit_context_map(self, comparison: bool = False):
        context_map = getattr(
            self.main_window,
            "comparison_unit_context" if comparison else "unit_context",
            None,
        )
        return context_map if context_map is not None else {}

    def _get_active_display_units(self):
        active_display_units = getattr(self.main_window, "active_display_units_by_family", None)
        return active_display_units if active_display_units is not None else {}

    def _get_common_columns(self):
        """
        Returns a sorted list of data columns that are present in
        BOTH the primary and comparison dataframes.
        """
        df = self._get_df()
        df_compare = self._get_compare_df()

        if df is None:
            return []

        excluded_cols = {"FREQ", "TIME", "NO", "DataFolder"}
        data_cols_primary = [
            col for col in df.columns
            if col not in excluded_cols and not col.startswith("Phase_")
        ]

        if df_compare is None:
            return sorted(data_cols_primary)

        cols_compare = set(df_compare.columns)
        common_cols = [
            col for col in data_cols_primary
            if col in cols_compare
        ]

        return sorted(common_cols)

    def _get_data_domain(self):
        return self.main_window.data_domain

    def _get_display_unit_for_family(self, family: str, fallback_unit: str) -> str:
        return self._get_active_display_units().get(family, fallback_unit)

    def _get_column_context(self, column_name: str, comparison: bool = False):
        return self._get_unit_context_map(comparison=comparison).get(column_name)

    def _get_domain_context(self, comparison: bool = False):
        data_domain = self._get_data_domain()
        context = self._get_column_context(data_domain, comparison=comparison)
        if context is not None and (context.display_unit is not None or context.normalized_unit is not None):
            return context
        if data_domain == "TIME":
            return ColumnUnitContext.from_source_unit(
                data_domain,
                "s",
                display_unit=self._get_display_unit_for_family("time", "s"),
                family_hint="time",
            )
        if data_domain == "FREQ":
            return ColumnUnitContext.from_source_unit(
                data_domain,
                "Hz",
                display_unit=self._get_display_unit_for_family("frequency", "Hz"),
                family_hint="frequency",
            )
        return None

    def _get_theta_context(self):
        return ColumnUnitContext.from_source_unit(
            "Theta",
            "deg",
            display_unit=self._get_display_unit_for_family("phase", "deg"),
            family_hint="phase",
        )

    def _get_computed_metric_context(self, metric_name: str):
        if metric_name == self.TIME_STEP_LABEL:
            return ColumnUnitContext.from_source_unit(
                metric_name,
                "s",
                display_unit=self._get_display_unit_for_family("time", "s"),
                family_hint="time",
            )
        if metric_name == self.FS_LABEL:
            return ColumnUnitContext.from_source_unit(
                metric_name,
                "Hz",
                display_unit=self._get_display_unit_for_family("frequency", "Hz"),
                family_hint="frequency",
            )
        return None

    def _convert_series_for_context(self, series: pd.Series, context):
        converted = series.copy(deep=True)
        if (
            context is None
            or context.normalized_unit is None
            or context.display_unit is None
            or context.native_only
            or context.normalized_unit == context.display_unit
        ):
            return converted
        return convert_series(
            converted,
            source_unit=context.normalized_unit,
            target_unit=context.display_unit,
            family_hint=context.quantity_family,
        )

    def _convert_series_to_unit(self, series: pd.Series, context, target_unit: str):
        converted = series.copy(deep=True)
        if context is None or context.normalized_unit is None or context.normalized_unit == target_unit:
            return converted
        return convert_series(
            converted,
            source_unit=context.normalized_unit,
            target_unit=target_unit,
            family_hint=context.quantity_family,
        )

    def _convert_scalar_for_context(self, value, context):
        if (
            context is None
            or context.normalized_unit is None
            or context.display_unit is None
            or context.native_only
            or context.normalized_unit == context.display_unit
        ):
            return value
        return convert_scalar(
            value,
            source_unit=context.normalized_unit,
            target_unit=context.display_unit,
            family_hint=context.quantity_family,
        )

    def _convert_scalar_to_unit(self, value, context, target_unit: str):
        if context is None or context.normalized_unit is None or context.normalized_unit == target_unit:
            return value
        return convert_scalar(
            value,
            source_unit=context.normalized_unit,
            target_unit=target_unit,
            family_hint=context.quantity_family,
        )

    def _base_axis_label(self, axis_title: str | None, fallback: str) -> str:
        if not axis_title:
            return fallback
        return axis_title.split(" [", 1)[0]

    def _format_axis_title(self, axis_label: str, context) -> str:
        if context is None:
            return axis_label
        display_unit = context.display_unit or context.normalized_unit
        return f"{axis_label} [{display_unit}]" if display_unit else axis_label

    def _build_y_axis_title(self, contexts, label: str = "Value") -> str:
        usable_contexts = [
            context
            for context in contexts
            if context is not None and (context.display_unit or context.normalized_unit)
        ]
        if not usable_contexts:
            return label

        families = {
            context.quantity_family
            for context in usable_contexts
            if context.quantity_family != "unknown"
        }
        units = {context.display_unit or context.normalized_unit for context in usable_contexts}
        if len(families) > 1 or len(units) > 1:
            return "Mixed Units"

        unit = next(iter(units))
        return f"{label} [{unit}]"

    def _project_index(self, index, context):
        projected_index = pd.Index(index)
        if context is None:
            return projected_index
        index_series = pd.Series(projected_index.to_numpy(copy=True))
        converted_index = self._convert_series_for_context(index_series, context)
        return pd.Index(converted_index.to_numpy(copy=True))

    def _apply_trace_metadata(self, plot_df: pd.DataFrame, column_contexts=None, unit_overrides=None, family_overrides=None):
        projected = plot_df.copy(deep=True)
        column_contexts = column_contexts or {}
        unit_overrides = unit_overrides or {}
        family_overrides = family_overrides or {}
        projected.attrs["trace_units"] = {}
        projected.attrs["trace_families"] = {}

        for column_name in projected.columns:
            context = column_contexts.get(column_name)
            projected.attrs["trace_units"][column_name] = unit_overrides.get(
                column_name,
                None if context is None else (context.display_unit or context.normalized_unit),
            )
            projected.attrs["trace_families"][column_name] = family_overrides.get(
                column_name,
                None if context is None else context.quantity_family,
            )
        return projected

    def _project_domain_index(self, plot_df: pd.DataFrame, comparison: bool = False, x_axis_context=None, x_axis_label: str | None = None):
        projected = plot_df.copy(deep=True)
        axis_context = x_axis_context if x_axis_context is not None else self._get_domain_context(comparison=comparison)
        fallback_label = "Freq" if self._get_data_domain() == "FREQ" else "Time"
        axis_label = x_axis_label or self._base_axis_label(projected.index.name, fallback_label)
        projected.index = self._project_index(projected.index, axis_context)
        projected.index.name = self._format_axis_title(axis_label, axis_context)
        return projected

    def _project_plot_frame(
        self,
        plot_df: pd.DataFrame,
        column_contexts=None,
        comparison: bool = False,
        x_axis_context=None,
        x_axis_label: str | None = None,
        apply_y_conversion: bool = True,
        unit_overrides=None,
        family_overrides=None,
    ):
        projected = self._project_domain_index(
            plot_df,
            comparison=comparison,
            x_axis_context=x_axis_context,
            x_axis_label=x_axis_label,
        )
        resolved_contexts = {
            column_name: (
                column_contexts.get(column_name)
                if column_contexts is not None and column_name in column_contexts
                else self._get_column_context(column_name, comparison=comparison)
            )
            for column_name in projected.columns
        }
        if apply_y_conversion:
            for column_name, context in resolved_contexts.items():
                projected.loc[:, column_name] = self._convert_series_for_context(projected[column_name], context)
        return self._apply_trace_metadata(
            projected,
            column_contexts=resolved_contexts,
            unit_overrides=unit_overrides,
            family_overrides=family_overrides,
        )

    def _project_plot_dict(
        self,
        dfs_for_plot,
        column_contexts=None,
        comparison: bool = False,
        x_axis_context=None,
        x_axis_label: str | None = None,
        apply_y_conversion: bool = True,
        unit_overrides=None,
        family_overrides=None,
    ):
        return {
            trace_name: self._project_plot_frame(
                df,
                column_contexts=column_contexts,
                comparison=comparison,
                x_axis_context=x_axis_context,
                x_axis_label=x_axis_label,
                apply_y_conversion=apply_y_conversion,
                unit_overrides=unit_overrides,
                family_overrides=family_overrides,
            )
            for trace_name, df in dfs_for_plot.items()
        }

    def _get_plot_df(self, cols, source_df=None, comparison: bool = False):
        """Prepares a projected DataFrame for plotting with the correct index."""
        df = self._get_raw_compare_df() if comparison else self._get_raw_df()
        if df is None:
            return pd.DataFrame()

        source_df = source_df if source_df is not None else df
        data_domain = self._get_data_domain()
        if not all(col in source_df.columns for col in [data_domain] + cols):
            return pd.DataFrame()

        x_label = "Time [s]" if data_domain == "TIME" else "Freq [Hz]"
        plot_df = source_df[cols].copy()
        plot_df.index = source_df[data_domain]
        plot_df.index.name = x_label
        return self._project_plot_frame(plot_df, comparison=comparison)

    def _is_multi_folder(self) -> bool:
        df = self._get_df()
        try:
            return df is not None and "DataFolder" in df.columns and df["DataFolder"].nunique() > 1
        except Exception:
            return False

    def _is_computed_metric(self, name: str) -> bool:
        return name in (self.TIME_STEP_LABEL, self.FS_LABEL)

    def _get_phase_col(self, col: str) -> str:
        return f"Phase_{col}"

    def _update_phase_plot_for_single(self, selected_col: str, is_multi_folder: bool) -> None:
        """Shows/hides the phase plot matching current behavior for Single Data tab."""
        df = self._get_raw_df()
        tab = self.main_window.tab_single_data
        if self._is_computed_metric(selected_col):
            tab.set_phase_plot_visibility(False)
            return
        if self._get_data_domain() == "FREQ" and not is_multi_folder:
            phase_col = self._get_phase_col(selected_col)
            if phase_col in df.columns:
                phase_df = self._get_plot_df([phase_col])
                phase_context = self._get_column_context(phase_col)
                phase_fig = self.plotter.create_standard_figure(
                    {phase_col: phase_df},
                    f"Phase of {selected_col}",
                    self._build_y_axis_title([phase_context], label="Phase"),
                )
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

    @dataclass
    class InterfaceDataOptions:
        interface_side_pairs: list[tuple[str, str]]

    def _snapshot_interface_data_options(self) -> "PlotController.InterfaceDataOptions":
        tab = self.main_window.tab_interface_data
        if hasattr(tab, "selected_interface_side_pairs"):
            interface_side_pairs = list(tab.selected_interface_side_pairs())
        else:
            interface = tab.interface_selector.currentText()
            side = tab.side_selector.currentText()
            interface_side_pairs = [(interface, side)] if interface and side else []
        return PlotController.InterfaceDataOptions(
            interface_side_pairs=interface_side_pairs,
        )

    @dataclass
    class PartLoadsOptions:
        sides: list[str]
        exclude: bool
        section_enabled: bool
        section_min_text: str
        section_max_text: str
        tukey_enabled: bool
        tukey_alpha: float

    def _snapshot_part_loads_options(self) -> "PlotController.PartLoadsOptions":
        tab = self.main_window.tab_part_loads
        if hasattr(tab, "selected_sides"):
            sides = list(tab.selected_sides())
        else:
            side = tab.side_filter_selector.currentText()
            sides = [side] if side else []
        return PlotController.PartLoadsOptions(
            sides=sides,
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

    def _snapshot_compare_data_options(self) -> "PlotController.CompareDataOptions":
        tab = self.main_window.tab_compare_data
        return PlotController.CompareDataOptions(
            selected_column=tab.compare_column_selector.currentText(),
        )

    @dataclass
    class ComparePartLoadsOptions:
        side: str
        exclude: bool

    def _snapshot_compare_part_loads_options(self) -> "PlotController.ComparePartLoadsOptions":
        tab = self.main_window.tab_compare_part_loads
        return PlotController.ComparePartLoadsOptions(
            side=tab.side_filter_selector.currentText(),
            exclude=tab.exclude_checkbox.isChecked(),
        )

    @dataclass
    class TimeDomainRepresentOptions:
        frequency_text: str
        selected_side: str

    def _snapshot_time_domain_represent_options(self) -> "PlotController.TimeDomainRepresentOptions":
        tab_time = self.main_window.tab_time_domain_represent
        part_loads_tab = self.main_window.tab_part_loads
        if hasattr(part_loads_tab, "selected_sides"):
            selected_sides = part_loads_tab.selected_sides()
            side = selected_sides[0] if selected_sides else ""
        else:
            side = part_loads_tab.side_filter_selector.currentText()
        return PlotController.TimeDomainRepresentOptions(
            frequency_text=tab_time.data_point_selector.currentText(),
            selected_side=side,
        )

    def _should_exclude_component(self, col_name: str) -> bool:
        """
        Checks if a column should be excluded based on the T2/T3/R2/R3 filter,
        while correctly preserving resultants like 'T2/T3'.
        """
        if re.search(r"\bT2\b", col_name) and not re.search(r"T2/T3", col_name):
            return True
        if re.search(r"\bT3\b", col_name) and not re.search(r"T2/T3", col_name):
            return True
        if re.search(r"\bR2\b", col_name) and not re.search(r"R2/R3", col_name):
            return True
        if re.search(r"\bR3\b", col_name) and not re.search(r"R2/R3", col_name):
            return True
        return False

    def _filter_part_load_cols(self, all_columns, side, required_components, exclude):
        side_pattern = re.compile(rf"\b{re.escape(side)}\b")
        side_cols = [col for col in all_columns if side_pattern.search(col)]
        component_cols = [col for col in side_cols if any(comp in col for comp in required_components)]
        final_cols = [col for col in component_cols if "Phase_" not in col]
        if exclude:
            final_cols = [col for col in final_cols if not self._should_exclude_component(col)]
        return final_cols

    def _calculate_differences(self, columns):
        """Calculates display-projected differences for columns present in both datasets."""
        df = self._get_raw_df()
        df_compare = self._get_raw_compare_df()
        data_domain = self._get_data_domain()

        if df is None or df_compare is None:
            return pd.DataFrame(), {}

        diff_dict = {}
        diff_contexts = {}
        for col in columns:
            if col not in df.columns or col not in df_compare.columns:
                print(f"Skipping difference calculation for '{col}': Column not present in both datasets.")
                continue

            primary_context = self._get_column_context(col, comparison=False)
            compare_context = self._get_column_context(col, comparison=True) or primary_context
            mag1 = self._convert_series_for_context(df[col], primary_context)
            mag2 = self._convert_series_for_context(df_compare[col], compare_context)
            diff = pd.Series(np.nan, index=mag1.index, dtype=float)

            if data_domain == "FREQ":
                phase_col = f"Phase_{col}"
                if phase_col in df.columns and phase_col in df_compare.columns:
                    try:
                        phase_context = self._get_column_context(phase_col, comparison=False)
                        phase_context_compare = self._get_column_context(phase_col, comparison=True) or phase_context
                        p1_rad = self._convert_series_to_unit(df[phase_col], phase_context, "rad")
                        p2_rad = self._convert_series_to_unit(df_compare[phase_col], phase_context_compare, "rad")
                        if pd.api.types.is_numeric_dtype(mag1) and pd.api.types.is_numeric_dtype(mag2):
                            diff = pd.Series(
                                np.abs((mag1 * np.exp(1j * p1_rad)) - (mag2 * np.exp(1j * p2_rad))),
                                index=mag1.index,
                            )
                        else:
                            print(f"Skipping complex diff for '{col}': Non-numeric magnitude data.")
                    except Exception as e:
                        print(f"Error calculating complex difference for '{col}': {e}")
                else:
                    try:
                        if pd.api.types.is_numeric_dtype(mag1) and pd.api.types.is_numeric_dtype(mag2):
                            diff = np.abs(mag1 - mag2)
                        else:
                            print(f"Skipping simple diff for '{col}': Non-numeric magnitude data.")
                    except Exception as e:
                        print(f"Error calculating simple difference for '{col}': {e}")
            else:
                try:
                    if pd.api.types.is_numeric_dtype(mag1) and pd.api.types.is_numeric_dtype(mag2):
                        diff = np.abs(mag1 - mag2)
                    else:
                        print(f"Skipping time diff for '{col}': Non-numeric magnitude data.")
                except Exception as e:
                    print(f"Error calculating time difference for '{col}': {e}")

            if not pd.isna(diff).all():
                diff_column = f"{self.DELTA_SYMBOL} {col}"
                diff_dict[diff_column] = diff
                diff_contexts[diff_column] = primary_context
            else:
                print(f"Failed to calculate valid difference for '{col}'.")

        return (pd.DataFrame(diff_dict) if diff_dict else pd.DataFrame(), diff_contexts)

    # region Signal Slots
    @QtCore.pyqtSlot()
    def update_all_plots_from_settings(self):
        if hasattr(self.main_window, "apply_unit_preferences_from_settings"):
            self.main_window.apply_unit_preferences_from_settings()
        if self._get_df() is None:
            return

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
        df = self._get_raw_df()
        if df is None:
            return

        tab = self.main_window.tab_single_data
        opts = self._snapshot_single_data_options()
        selected_col = opts.selected_col
        if not selected_col:
            return

        is_multi_folder = self._is_multi_folder()
        selected_context = self._get_column_context(selected_col)

        if self._get_data_domain() == "TIME" and selected_col == self.TIME_STEP_LABEL:
            selected_context = self._get_computed_metric_context(selected_col)
            dfs_for_plot = build_dt_by_folder(
                df,
                section_enabled=opts.section_enabled,
                t_min_text=opts.section_min_text,
                t_max_text=opts.section_max_text,
            )
            if not is_multi_folder and dfs_for_plot:
                only_key = next(iter(dfs_for_plot))
                dfs_for_plot = {selected_col: dfs_for_plot[only_key]}
            dfs_for_plot = self._project_plot_dict(dfs_for_plot, column_contexts={f"{self.DELTA_SYMBOL}t [s]": selected_context})
            y_axis_title = self._build_y_axis_title([selected_context], label="Time Step")
            fig = self.plotter.create_standard_figure(dfs_for_plot, title=self.TIME_STEP_LABEL, y_axis_title=y_axis_title)
        elif self._get_data_domain() == "TIME" and selected_col == self.FS_LABEL:
            selected_context = self._get_computed_metric_context(selected_col)
            dfs_for_plot = build_fs_by_folder(
                df,
                section_enabled=opts.section_enabled,
                t_min_text=opts.section_min_text,
                t_max_text=opts.section_max_text,
            )
            if not is_multi_folder and dfs_for_plot:
                only_key = next(iter(dfs_for_plot))
                dfs_for_plot = {selected_col: dfs_for_plot[only_key]}
            dfs_for_plot = self._project_plot_dict(dfs_for_plot, column_contexts={"Sampling Rate [Hz]": selected_context})
            y_axis_title = self._build_y_axis_title([selected_context], label="Sampling Rate")
            fig = self.plotter.create_standard_figure(dfs_for_plot, title=self.FS_LABEL, y_axis_title=y_axis_title)
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
            dfs_for_plot = self._project_plot_dict(dfs_for_plot, column_contexts={selected_col: selected_context})
            plot_title = f"{selected_col} Plot"
            y_axis_title = self._build_y_axis_title([selected_context])
            if self.main_window.tab_settings.rolling_min_max_checkbox.isChecked() and self._get_data_domain() == "TIME":
                try:
                    points = int(self.main_window.tab_settings.desired_num_points_input.text())
                    as_bars = self.main_window.tab_settings.plot_as_bars_checkbox.isChecked()
                    fig = self.plotter.create_rolling_envelope_figure(
                        dfs_for_plot,
                        plot_title,
                        points,
                        as_bars,
                        y_axis_title=y_axis_title,
                    )
                except ValueError:
                    fig = self.plotter.create_standard_figure(
                        dfs_for_plot,
                        title=f"{plot_title} (Invalid Points)",
                        y_axis_title=y_axis_title,
                    )
            else:
                fig = self.plotter.create_standard_figure(dfs_for_plot, title=plot_title, y_axis_title=y_axis_title)

        tab.display_regular_plot(fig)
        self._update_phase_plot_for_single(selected_col, is_multi_folder)

        if self._get_data_domain() == "TIME" and opts.spectrum_enabled and not is_multi_folder:
            self.update_spectrum_plot_only()

    @QtCore.pyqtSlot()
    def update_interface_data_plots(self):
        df = self._get_raw_df()
        if df is None:
            return

        tab = self.main_window.tab_interface_data
        opts = self._snapshot_interface_data_options()
        interface_side_pairs = opts.interface_side_pairs
        if not interface_side_pairs:
            tab.display_t_series_plot(
                self.plotter.create_standard_figure(
                    pd.DataFrame(),
                    "Translational Components",
                )
            )
            tab.display_r_series_plot(
                self.plotter.create_standard_figure(
                    pd.DataFrame(),
                    "Rotational Components",
                )
            )
            return

        t_frames = []
        r_frames = []
        t_contexts = {}
        r_contexts = {}
        use_prefixed_labels = len(interface_side_pairs) > 1
        for interface, side in interface_side_pairs:
            t_cols = [
                c
                for c in df.columns
                if c.startswith(interface)
                and side in c
                and any(s in c for s in ["T1", "T2", "T3", "T2/T3"])
                and "Phase_" not in c
            ]
            r_cols = [
                c
                for c in df.columns
                if c.startswith(interface)
                and side in c
                and any(s in c for s in ["R1", "R2", "R3", "R2/R3"])
                and "Phase_" not in c
            ]

            combo_label = f"{interface} - {side}"

            if t_cols:
                combo_contexts = {column_name: self._get_column_context(column_name) for column_name in t_cols}
                projected = self._project_plot_frame(
                    build_multi_series_for_single(
                        df,
                        columns=t_cols,
                        data_domain=self._get_data_domain(),
                        section_enabled=False,
                    ),
                    column_contexts=combo_contexts,
                )
                if use_prefixed_labels:
                    projected = projected.rename(columns={column_name: f"{combo_label} - {column_name}" for column_name in projected.columns})
                t_frames.append(projected)
                for column_name, context in combo_contexts.items():
                    trace_name = f"{combo_label} - {column_name}" if use_prefixed_labels else column_name
                    t_contexts[trace_name] = context

            if r_cols:
                combo_contexts = {column_name: self._get_column_context(column_name) for column_name in r_cols}
                projected = self._project_plot_frame(
                    build_multi_series_for_single(
                        df,
                        columns=r_cols,
                        data_domain=self._get_data_domain(),
                        section_enabled=False,
                    ),
                    column_contexts=combo_contexts,
                )
                if use_prefixed_labels:
                    projected = projected.rename(columns={column_name: f"{combo_label} - {column_name}" for column_name in projected.columns})
                r_frames.append(projected)
                for column_name, context in combo_contexts.items():
                    trace_name = f"{combo_label} - {column_name}" if use_prefixed_labels else column_name
                    r_contexts[trace_name] = context

        t_df = pd.concat(t_frames, axis=1) if t_frames else pd.DataFrame()
        r_df = pd.concat(r_frames, axis=1) if r_frames else pd.DataFrame()
        if not t_df.empty:
            t_df = self._apply_trace_metadata(t_df, column_contexts=t_contexts)
        if not r_df.empty:
            r_df = self._apply_trace_metadata(r_df, column_contexts=r_contexts)

        tab.display_t_series_plot(
            self.plotter.create_standard_figure(
                t_df,
                "Translational Components" if use_prefixed_labels else f"Translational Components - {interface_side_pairs[0][1]}",
                self._build_y_axis_title(t_contexts.values()),
            )
        )
        tab.display_r_series_plot(
            self.plotter.create_standard_figure(
                r_df,
                "Rotational Components" if use_prefixed_labels else f"Rotational Components - {interface_side_pairs[0][1]}",
                self._build_y_axis_title(r_contexts.values()),
            )
        )

    @QtCore.pyqtSlot()
    def update_part_loads_plots(self):
        df = self._get_raw_df()
        if df is None:
            return

        opts = self._snapshot_part_loads_options()
        tab = self.main_window.tab_part_loads
        sides = opts.sides
        if not sides:
            tab.display_t_series_plot(
                self.plotter.create_standard_figure(
                    pd.DataFrame(),
                    "Translational Components",
                )
            )
            tab.display_r_series_plot(
                self.plotter.create_standard_figure(
                    pd.DataFrame(),
                    "Rotational Components",
                )
            )
            return

        exclude = opts.exclude
        df_processed = df.copy()
        if self._get_data_domain() == "TIME":
            if opts.section_enabled:
                df_processed = apply_data_section(df_processed, opts.section_min_text, opts.section_max_text)
            if opts.tukey_enabled:
                df_processed = apply_tukey_window(df_processed, opts.tukey_alpha)

        t_frames = []
        r_frames = []
        t_contexts = {}
        r_contexts = {}
        use_prefixed_labels = len(sides) > 1
        for side in sides:
            t_cols = self._filter_part_load_cols(df_processed.columns, side, ["T1", "T2", "T3", "T2/T3"], exclude)
            r_cols = self._filter_part_load_cols(df_processed.columns, side, ["R1", "R2", "R3", "R2/R3"], exclude)

            if t_cols:
                combo_contexts = {column_name: self._get_column_context(column_name) for column_name in t_cols}
                projected = self._project_plot_frame(
                    build_multi_series_for_single(
                        df_processed,
                        columns=t_cols,
                        data_domain=self._get_data_domain(),
                        section_enabled=False,
                        tukey_enabled=False,
                    ),
                    column_contexts=combo_contexts,
                )
                if use_prefixed_labels:
                    projected = projected.rename(columns={column_name: f"{side} - {column_name}" for column_name in projected.columns})
                t_frames.append(projected)
                for column_name, context in combo_contexts.items():
                    trace_name = f"{side} - {column_name}" if use_prefixed_labels else column_name
                    t_contexts[trace_name] = context

            if r_cols:
                combo_contexts = {column_name: self._get_column_context(column_name) for column_name in r_cols}
                projected = self._project_plot_frame(
                    build_multi_series_for_single(
                        df_processed,
                        columns=r_cols,
                        data_domain=self._get_data_domain(),
                        section_enabled=False,
                        tukey_enabled=False,
                    ),
                    column_contexts=combo_contexts,
                )
                if use_prefixed_labels:
                    projected = projected.rename(columns={column_name: f"{side} - {column_name}" for column_name in projected.columns})
                r_frames.append(projected)
                for column_name, context in combo_contexts.items():
                    trace_name = f"{side} - {column_name}" if use_prefixed_labels else column_name
                    r_contexts[trace_name] = context

        t_df = pd.concat(t_frames, axis=1) if t_frames else pd.DataFrame()
        r_df = pd.concat(r_frames, axis=1) if r_frames else pd.DataFrame()
        if not t_df.empty:
            t_df = self._apply_trace_metadata(t_df, column_contexts=t_contexts)
        if not r_df.empty:
            r_df = self._apply_trace_metadata(r_df, column_contexts=r_contexts)

        tab.display_t_series_plot(
            self.plotter.create_standard_figure(
                t_df,
                "Translational Components" if use_prefixed_labels else f"Translational Components - {sides[0]}",
                self._build_y_axis_title(t_contexts.values()),
            )
        )
        tab.display_r_series_plot(
            self.plotter.create_standard_figure(
                r_df,
                "Rotational Components" if use_prefixed_labels else f"Rotational Components- {sides[0]}",
                self._build_y_axis_title(r_contexts.values()),
            )
        )

    @QtCore.pyqtSlot()
    def update_time_domain_represent_plot(self):
        df = self._get_raw_df()
        if df is None or self._get_data_domain() != "FREQ":
            return

        tab = self.main_window.tab_time_domain_represent
        try:
            opts = self._snapshot_time_domain_represent_options()
            freq_text = opts.frequency_text
            if not freq_text or "Select a frequency" in freq_text:
                return
            freq = float(freq_text)

            selected_side = opts.selected_side
            if not selected_side:
                tab.display_plot(go.Figure())
                return

            side_pattern = re.compile(rf"\b{re.escape(selected_side)}\b")
            plot_cols = [
                c for c in df.columns
                if side_pattern.search(c)
                and not c.startswith("Phase_")
                and any(s in c for s in ["T1", "T2", "T3", "R1", "R2", "R3", "T2/T3", "R2/R3"])
            ]

            theta = np.linspace(0, 360, 361)
            rads = np.radians(theta)
            plot_data = {}
            data_at_freq = df[df["FREQ"] == freq].iloc[0]

            for col in plot_cols:
                phase_col = f"Phase_{col}"
                if phase_col in data_at_freq:
                    phase_context = self._get_column_context(phase_col)
                    phase_radians = self._convert_scalar_to_unit(data_at_freq[phase_col], phase_context, "rad")
                    plot_data[col] = data_at_freq[col] * np.cos(rads - phase_radians)

            df_time_domain = pd.DataFrame(plot_data, index=theta)
            df_time_domain.index.name = "Theta [deg]"
            column_contexts = {column_name: self._get_column_context(column_name) for column_name in plot_cols}
            df_time_domain = self._project_plot_frame(
                df_time_domain,
                column_contexts=column_contexts,
                x_axis_context=self._get_theta_context(),
                x_axis_label="Theta",
            )
            tab.current_plot_data = {
                column_name: {
                    "theta": df_time_domain.index.to_numpy(copy=True),
                    "y_data": df_time_domain[column_name].to_numpy(copy=True),
                }
                for column_name in df_time_domain.columns
            }

            frequency_context = self._get_domain_context()
            displayed_freq = self._convert_scalar_for_context(freq, frequency_context)
            displayed_freq_text = f"{displayed_freq:g}" if isinstance(displayed_freq, (int, float, np.floating)) else f"{displayed_freq}"
            frequency_unit = None if frequency_context is None else (frequency_context.display_unit or frequency_context.normalized_unit)
            if frequency_unit:
                title = f"Time Domain Representation at {displayed_freq_text} {frequency_unit} for {selected_side}"
            else:
                title = f"Time Domain Representation at {displayed_freq_text} for {selected_side}"
            fig = self.plotter.create_standard_figure(
                df_time_domain,
                title,
                self._build_y_axis_title(column_contexts.values()),
            )
            tab.display_plot(fig)
        except (ValueError, IndexError) as e:
            print(f"Could not update time domain representation plot: {e}")
            tab.display_plot(go.Figure())

    @QtCore.pyqtSlot()
    def update_compare_column_list(self):
        common_columns = self._get_common_columns()
        self.main_window.tab_compare_data.update_column_selector(common_columns)

    @QtCore.pyqtSlot()
    def update_compare_data_plots(self):
        if self._get_raw_df() is None or self._get_raw_compare_df() is None:
            return

        tab = self.main_window.tab_compare_data
        selected_column = tab.compare_column_selector.currentText()
        if not selected_column:
            return

        df1 = self._get_plot_df([selected_column], source_df=self._get_raw_df(), comparison=False)
        df2 = self._get_plot_df([selected_column], source_df=self._get_raw_compare_df(), comparison=True)
        selected_context = self._get_column_context(selected_column, comparison=False)

        fig_compare = self.plotter.create_comparison_figure(
            df1,
            df2,
            selected_column,
            f"{selected_column} Comparison",
            y_axis_title=self._build_y_axis_title([selected_context]),
        )
        tab.display_comparison_plot(fig_compare)

        diff_df, diff_contexts = self._calculate_differences([selected_column])
        if diff_df.empty:
            return

        domain_col = self._get_data_domain()
        abs_diff_df = pd.DataFrame({"Absolute Difference": diff_df.iloc[:, 0].values})
        abs_diff_df.index = self._get_raw_df()[domain_col]
        abs_diff_df.index.name = "Time [s]" if domain_col == "TIME" else "Freq [Hz]"
        abs_diff_df = self._project_plot_frame(
            abs_diff_df,
            column_contexts={"Absolute Difference": selected_context},
            apply_y_conversion=False,
        )
        fig_abs_diff = self.plotter.create_standard_figure(
            abs_diff_df,
            f"{selected_column} Absolute Difference",
            self._build_y_axis_title([selected_context]),
        )
        tab.display_absolute_diff_plot(fig_abs_diff)

        with np.errstate(divide="ignore", invalid="ignore"):
            relative_diff = np.divide(
                100 * diff_df.iloc[:, 0].to_numpy(copy=True),
                np.abs(df1.iloc[:, 0].to_numpy(copy=True)),
            )
            relative_diff = pd.Series(relative_diff)
            relative_diff.fillna(0, inplace=True)
        rel_diff_df = pd.DataFrame({"Relative Difference (%)": relative_diff.values})
        rel_diff_df.index = self._get_raw_df()[domain_col]
        rel_diff_df.index.name = "Time [s]" if domain_col == "TIME" else "Freq [Hz]"
        rel_diff_df = self._project_domain_index(rel_diff_df)
        rel_diff_df = self._apply_trace_metadata(
            rel_diff_df,
            unit_overrides={"Relative Difference (%)": "%"},
            family_overrides={"Relative Difference (%)": "percent"},
        )
        fig_rel_diff = self.plotter.create_standard_figure(
            rel_diff_df,
            f"{selected_column} Relative Difference (%)",
            "Percent (%)",
        )
        tab.display_relative_diff_plot(fig_rel_diff)

    @QtCore.pyqtSlot()
    def update_compare_part_loads_plots(self):
        if self._get_raw_df() is None or self._get_raw_compare_df() is None:
            return

        tab = self.main_window.tab_compare_part_loads
        selected_side = tab.side_filter_selector.currentText()
        if not selected_side:
            return

        exclude = tab.exclude_checkbox.isChecked()
        t_cols = self._filter_part_load_cols(self._get_raw_df().columns, selected_side, ["T1", "T2", "T3", "T2/T3"], exclude)
        r_cols = self._filter_part_load_cols(self._get_raw_df().columns, selected_side, ["R1", "R2", "R3", "R2/R3"], exclude)

        domain_col = self._get_data_domain()
        t_diff, t_diff_contexts = self._calculate_differences(t_cols)
        r_diff, r_diff_contexts = self._calculate_differences(r_cols)
        t_diff_df = pd.DataFrame(t_diff) if not t_diff.empty else pd.DataFrame()
        r_diff_df = pd.DataFrame(r_diff) if not r_diff.empty else pd.DataFrame()
        if not t_diff_df.empty:
            t_diff_df.index = self._get_raw_df()[domain_col]
            t_diff_df.index.name = "Time [s]" if domain_col == "TIME" else "Freq [Hz]"
            t_diff_df = self._project_plot_frame(
                t_diff_df,
                column_contexts=t_diff_contexts,
                apply_y_conversion=False,
            )
        if not r_diff_df.empty:
            r_diff_df.index = self._get_raw_df()[domain_col]
            r_diff_df.index.name = "Time [s]" if domain_col == "TIME" else "Freq [Hz]"
            r_diff_df = self._project_plot_frame(
                r_diff_df,
                column_contexts=r_diff_contexts,
                apply_y_conversion=False,
            )

        fig_t = self.plotter.create_standard_figure(
            t_diff_df,
            f"Translational Components, Difference ({self.DELTA_SYMBOL}) - {selected_side}",
            self._build_y_axis_title(t_diff_contexts.values()),
        )
        tab.display_t_series_plot(fig_t)

        fig_r = self.plotter.create_standard_figure(
            r_diff_df,
            f"Rotational Components, Difference ({self.DELTA_SYMBOL}) - {selected_side}",
            self._build_y_axis_title(r_diff_contexts.values()),
        )
        tab.display_r_series_plot(fig_r)

    @QtCore.pyqtSlot()
    def update_spectrum_plot_only(self):
        """A dedicated function that only updates the spectrum plot."""
        df = self._get_raw_df()
        if df is None or self._get_data_domain() != "TIME":
            return

        tab = self.main_window.tab_single_data
        opts = self._snapshot_single_data_options()
        selected_col = opts.selected_col
        if not selected_col or selected_col in (self.TIME_STEP_LABEL, self.FS_LABEL) or not opts.spectrum_enabled:
            return

        if self._is_multi_folder():
            return

        try:
            source_df = df
            if opts.section_enabled:
                source_df = apply_data_section(source_df, opts.section_min_text, opts.section_max_text)
            plot_df = self._get_plot_df([selected_col], source_df=source_df)
            if opts.filter_enabled:
                try:
                    cutoff = float(opts.cutoff_frequency_text)
                    order = opts.filter_order
                    plot_df = apply_low_pass_filter(plot_df, selected_col, cutoff, order)
                except ValueError:
                    pass

            fig_spec = self.plotter.create_spectrum_figure(
                plot_df,
                num_slices=int(opts.num_slices_text),
                plot_type=opts.plot_type,
                colorscale=opts.colorscale,
            )
            tab.set_spectrum_plot_visibility(True)
            tab.display_spectrum_plot(fig_spec)
        except (ValueError, IndexError, ZeroDivisionError) as e:
            print(f"Could not generate spectrum: {e}")
            tab.set_spectrum_plot_visibility(False)
    # endregion
