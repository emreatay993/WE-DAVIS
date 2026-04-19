from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd

try:
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QMessageBox
except ModuleNotFoundError:
    import sys
    from types import ModuleType

    def _install_pyqt5_stub() -> None:
        pyqt5_module = ModuleType("PyQt5")
        qtcore_module = ModuleType("PyQt5.QtCore")
        qtwidgets_module = ModuleType("PyQt5.QtWidgets")

        class _BoundSignal:
            def __init__(self) -> None:
                self._slots = []

            def connect(self, slot) -> None:
                self._slots.append(slot)

            def emit(self, *args, **kwargs) -> None:
                for slot in list(self._slots):
                    slot(*args, **kwargs)

        class _SignalDescriptor:
            def __init__(self) -> None:
                self._name = None

            def __set_name__(self, owner, name) -> None:
                self._name = f"__signal_{name}"

            def __get__(self, instance, owner):
                if instance is None:
                    return self
                if not hasattr(instance, self._name):
                    setattr(instance, self._name, _BoundSignal())
                return getattr(instance, self._name)

        class QObject:
            def __init__(self, parent=None) -> None:
                self.parent = parent

        class QCoreApplication:
            _instance = None

            def __init__(self, args=None) -> None:
                QCoreApplication._instance = self

            @classmethod
            def instance(cls):
                return cls._instance

        class QUrl:
            @staticmethod
            def fromLocalFile(path):
                return path

        def pyqtSignal(*args, **kwargs):
            return _SignalDescriptor()

        def pyqtSlot(*args, **kwargs):
            def decorator(function):
                return function
            return decorator

        class QFileDialog:
            @staticmethod
            def getExistingDirectory(*args, **kwargs):
                return ""

        class QMessageBox:
            @staticmethod
            def warning(*args, **kwargs):
                return None

            @staticmethod
            def critical(*args, **kwargs):
                return None

            @staticmethod
            def information(*args, **kwargs):
                return None

        qtcore_module.QObject = QObject
        qtcore_module.QCoreApplication = QCoreApplication
        qtcore_module.QUrl = QUrl
        qtcore_module.pyqtSignal = pyqtSignal
        qtcore_module.pyqtSlot = pyqtSlot
        qtwidgets_module.QFileDialog = QFileDialog
        qtwidgets_module.QMessageBox = QMessageBox

        pyqt5_module.QtCore = qtcore_module
        pyqt5_module.QtWidgets = qtwidgets_module
        sys.modules["PyQt5"] = pyqt5_module
        sys.modules["PyQt5.QtCore"] = qtcore_module
        sys.modules["PyQt5.QtWidgets"] = qtwidgets_module

    _install_pyqt5_stub()
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QMessageBox

try:
    import plotly.graph_objects  # noqa: F401
except ModuleNotFoundError:
    import sys
    from types import ModuleType

    def _install_plotly_and_endaq_stubs() -> None:
        plotly_module = ModuleType("plotly")
        graph_objects_module = ModuleType("plotly.graph_objects")
        io_module = ModuleType("plotly.io")
        endaq_module = ModuleType("endaq")
        endaq_calc_module = ModuleType("endaq.calc")
        endaq_calc_fft_module = ModuleType("endaq.calc.fft")
        endaq_plot_module = ModuleType("endaq.plot")

        class _BaseTrace:
            def __init__(self, **kwargs) -> None:
                for key, value in kwargs.items():
                    setattr(self, key, value)

        class Scatter(_BaseTrace):
            pass

        class Heatmap(_BaseTrace):
            pass

        class Surface(_BaseTrace):
            pass

        class Figure:
            def __init__(self, *args, **kwargs) -> None:
                self.data = []
                self.layout = SimpleNamespace(
                    xaxis=SimpleNamespace(title=SimpleNamespace(text=None)),
                    yaxis=SimpleNamespace(title=SimpleNamespace(text=None)),
                    title=SimpleNamespace(text=None),
                )

            def add_trace(self, trace) -> None:
                self.data.append(trace)

            def update_layout(self, **kwargs) -> None:
                if "title" in kwargs:
                    self.layout.title.text = kwargs["title"]
                if "xaxis_title" in kwargs:
                    self.layout.xaxis.title.text = kwargs["xaxis_title"]
                if "yaxis_title" in kwargs:
                    self.layout.yaxis.title.text = kwargs["yaxis_title"]

        def to_html(*args, **kwargs):
            return "<html></html>"

        def rolling_fft(df, *args, **kwargs):
            return df

        def rolling_min_max_envelope(df, *args, **kwargs):
            figure = Figure()
            for column_name in df.columns:
                figure.add_trace(Scatter(name=column_name, x=df.index, y=df[column_name], hovertemplate=None, opacity=None))
            return figure

        def spectrum_over_time(df, *args, **kwargs):
            figure = Figure()
            figure.add_trace(Heatmap(colorscale=None))
            return figure

        graph_objects_module.Figure = Figure
        graph_objects_module.Scatter = Scatter
        graph_objects_module.Heatmap = Heatmap
        graph_objects_module.Surface = Surface
        io_module.to_html = to_html
        endaq_calc_fft_module.rolling_fft = rolling_fft
        endaq_plot_module.rolling_min_max_envelope = rolling_min_max_envelope
        endaq_plot_module.spectrum_over_time = spectrum_over_time

        plotly_module.graph_objects = graph_objects_module
        plotly_module.io = io_module
        endaq_module.calc = endaq_calc_module
        endaq_module.plot = endaq_plot_module
        endaq_calc_module.fft = endaq_calc_fft_module

        sys.modules["plotly"] = plotly_module
        sys.modules["plotly.graph_objects"] = graph_objects_module
        sys.modules["plotly.io"] = io_module
        sys.modules["endaq"] = endaq_module
        sys.modules["endaq.calc"] = endaq_calc_module
        sys.modules["endaq.calc.fft"] = endaq_calc_fft_module
        sys.modules["endaq.plot"] = endaq_plot_module

    _install_plotly_and_endaq_stubs()

try:
    import scipy.signal  # noqa: F401
except ModuleNotFoundError:
    import sys
    from types import ModuleType

    def _install_scipy_stub() -> None:
        scipy_module = ModuleType("scipy")
        signal_module = ModuleType("scipy.signal")
        windows_module = ModuleType("scipy.signal.windows")

        def tukey(length, alpha=0.5):
            return np.ones(length)

        def butter(order, cutoff, btype="low", analog=False):
            return np.array([1.0]), np.array([1.0])

        def filtfilt(b, a, values):
            return values

        windows_module.tukey = tukey
        signal_module.windows = windows_module
        signal_module.butter = butter
        signal_module.filtfilt = filtfilt
        scipy_module.signal = signal_module

        sys.modules["scipy"] = scipy_module
        sys.modules["scipy.signal"] = signal_module
        sys.modules["scipy.signal.windows"] = windows_module

    _install_scipy_stub()

from app.controllers.plot_controller import PlotController
from app.data_manager import DataManager
from app.plotting.plotter import Plotter
from app.units import ColumnUnitContext


class _Selector:
    def __init__(self, text: str = "") -> None:
        self._text = text

    def currentText(self) -> str:
        return self._text

    def setCurrentText(self, text: str) -> None:
        self._text = text


class _TextInput:
    def __init__(self, text: str = "") -> None:
        self._text = text

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text


class _CheckInput:
    def __init__(self, checked: bool = False) -> None:
        self._checked = checked

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool) -> None:
        self._checked = checked


class _ValueInput:
    def __init__(self, value) -> None:
        self._value = value

    def value(self):
        return self._value

    def setValue(self, value) -> None:
        self._value = value


class _SingleDataTab:
    def __init__(self, selected_col: str) -> None:
        self.column_selector = _Selector(selected_col)
        self.section_checkbox = _CheckInput(False)
        self.section_min_input = _TextInput("")
        self.section_max_input = _TextInput("")
        self.filter_checkbox = _CheckInput(False)
        self.cutoff_frequency_input = _TextInput("")
        self.filter_order_input = _ValueInput(2)
        self.spectrum_checkbox = _CheckInput(False)
        self.num_slices_input = _TextInput("8")
        self.plot_type_selector = _Selector("Heatmap")
        self.colorscale_selector = _Selector("Hot")
        self.regular_plot = None
        self.phase_plot = None
        self.phase_visible = False
        self.spectrum_plot = None
        self.spectrum_visible = False

    def display_regular_plot(self, figure) -> None:
        self.regular_plot = figure

    def set_phase_plot_visibility(self, visible: bool) -> None:
        self.phase_visible = visible

    def display_phase_plot(self, figure) -> None:
        self.phase_plot = figure

    def set_spectrum_plot_visibility(self, visible: bool) -> None:
        self.spectrum_visible = visible

    def display_spectrum_plot(self, figure) -> None:
        self.spectrum_plot = figure


class _InterfaceDataTab:
    def __init__(self, interface: str, side: str) -> None:
        self.interface_selector = _Selector(interface)
        self.side_selector = _Selector(side)
        self.t_series_plot = None
        self.r_series_plot = None

    def display_t_series_plot(self, figure) -> None:
        self.t_series_plot = figure

    def display_r_series_plot(self, figure) -> None:
        self.r_series_plot = figure


class _PartLoadsTab:
    def __init__(self, side: str) -> None:
        self.side_filter_selector = _Selector(side)
        self.exclude_checkbox = _CheckInput(False)
        self.section_checkbox = _CheckInput(False)
        self.section_min_input = _TextInput("")
        self.section_max_input = _TextInput("")
        self.tukey_checkbox = _CheckInput(False)
        self.tukey_alpha_spin = _ValueInput(0.1)
        self.t_series_plot = None
        self.r_series_plot = None

    def display_t_series_plot(self, figure) -> None:
        self.t_series_plot = figure

    def display_r_series_plot(self, figure) -> None:
        self.r_series_plot = figure


class _TimeDomainRepresentTab:
    def __init__(self, frequency_text: str) -> None:
        self.data_point_selector = _Selector(frequency_text)
        self.plot = None
        self.current_plot_data = {}

    def display_plot(self, figure) -> None:
        self.plot = figure


class _CompareDataTab:
    def __init__(self, selected_col: str) -> None:
        self.compare_column_selector = _Selector(selected_col)
        self.comparison_plot = None
        self.absolute_diff_plot = None
        self.relative_diff_plot = None
        self.updated_columns = None

    def display_comparison_plot(self, figure) -> None:
        self.comparison_plot = figure

    def display_absolute_diff_plot(self, figure) -> None:
        self.absolute_diff_plot = figure

    def display_relative_diff_plot(self, figure) -> None:
        self.relative_diff_plot = figure

    def update_column_selector(self, columns) -> None:
        self.updated_columns = list(columns)


class _ComparePartLoadsTab:
    def __init__(self, side: str) -> None:
        self.side_filter_selector = _Selector(side)
        self.exclude_checkbox = _CheckInput(False)
        self.t_series_plot = None
        self.r_series_plot = None

    def display_t_series_plot(self, figure) -> None:
        self.t_series_plot = figure

    def display_r_series_plot(self, figure) -> None:
        self.r_series_plot = figure


class _SettingsTab:
    def __init__(self) -> None:
        self.legend_font_size_selector = _Selector("10")
        self.default_font_size_selector = _Selector("12")
        self.hover_font_size_selector = _Selector("15")
        self.hover_mode_selector = _Selector("closest")
        self.opacity_spin = _ValueInput(0.75)
        self.rolling_min_max_checkbox = _CheckInput(False)
        self.desired_num_points_input = _TextInput("500")
        self.plot_as_bars_checkbox = _CheckInput(False)


class _RecordingPlotter:
    def __init__(self) -> None:
        self.legend_font_size = None
        self.default_font_size = None
        self.hover_font_size = None
        self.hover_mode = None
        self.trace_opacity = None
        self.calls = []

    def _record(self, kind: str, **payload):
        figure = SimpleNamespace(kind=kind, **payload)
        self.calls.append(figure)
        return figure

    def create_standard_figure(self, data_to_plot, title, y_axis_title="Value"):
        return self._record("standard", data_to_plot=data_to_plot, title=title, y_axis_title=y_axis_title)

    def create_comparison_figure(self, df1, df2, column, title, y_axis_title="Value"):
        return self._record("comparison", df1=df1, df2=df2, column=column, title=title, y_axis_title=y_axis_title)

    def create_difference_figure(self, diff_df, title, y_title):
        return self._record("difference", diff_df=diff_df, title=title, y_title=y_title)

    def create_rolling_envelope_figure(self, df_dict, title, desired_num_points, plot_as_bars, y_axis_title="Value"):
        return self._record(
            "rolling",
            df_dict=df_dict,
            title=title,
            desired_num_points=desired_num_points,
            plot_as_bars=plot_as_bars,
            y_axis_title=y_axis_title,
        )

    def create_spectrum_figure(self, df, num_slices, plot_type, freq_max=None, colorscale="Hot"):
        return self._record(
            "spectrum",
            df=df,
            num_slices=num_slices,
            plot_type=plot_type,
            freq_max=freq_max,
            colorscale=colorscale,
        )


def _apply_display_units(unit_context, display_units):
    projected = {}
    for column_name, context in unit_context.items():
        if context.display_unit is None or context.quantity_family == "unknown":
            projected[column_name] = context
            continue
        projected[column_name] = context.with_display_unit(
            display_units.get(context.quantity_family, context.display_unit)
        )
    return projected


def _build_main_window(
    df: pd.DataFrame,
    data_domain: str,
    unit_context,
    *,
    df_compare: pd.DataFrame | None = None,
    comparison_unit_context=None,
    display_units=None,
    single_selected: str = "",
    compare_selected: str = "",
    interface: str = "I1",
    side: str = "STBD",
    time_domain_frequency: str = "",
):
    display_units = dict(display_units or {})
    active_display_units = {}
    for context in unit_context.values():
        if context.display_unit is not None and context.quantity_family != "unknown":
            active_display_units.setdefault(
                context.quantity_family,
                display_units.get(context.quantity_family, context.display_unit),
            )
    active_display_units.update(display_units)

    comparison_unit_context = comparison_unit_context or {}
    projected_context = _apply_display_units(unit_context, active_display_units)
    projected_compare_context = _apply_display_units(comparison_unit_context, active_display_units)

    main_window = SimpleNamespace()
    main_window.plotter = _RecordingPlotter()
    main_window.df = df
    main_window.raw_primary_df = df.copy(deep=True)
    main_window.df_compare = df_compare
    main_window.raw_comparison_df = None if df_compare is None else df_compare.copy(deep=True)
    main_window.data_domain = data_domain
    main_window.unit_context = projected_context
    main_window.comparison_unit_context = projected_compare_context
    main_window.active_display_units_by_family = active_display_units
    main_window.tab_settings = _SettingsTab()
    main_window.tab_single_data = _SingleDataTab(single_selected)
    main_window.tab_interface_data = _InterfaceDataTab(interface, side)
    main_window.tab_part_loads = _PartLoadsTab(side)
    main_window.tab_time_domain_represent = _TimeDomainRepresentTab(time_domain_frequency)
    main_window.tab_compare_data = _CompareDataTab(compare_selected or single_selected)
    main_window.tab_compare_part_loads = _ComparePartLoadsTab(side)
    main_window.apply_unit_preferences_from_settings = lambda: None
    return main_window


class PlotUnitProjectionBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.qt_app = QtCore.QCoreApplication.instance() or QtCore.QCoreApplication([])
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.frequency_sample = cls.repo_root / "resources" / "sample_data" / "frequency_sample"
        cls.time_sample = cls.repo_root / "resources" / "sample_data" / "time_transient_sample"

    def setUp(self) -> None:
        self.data_manager = DataManager()
        self.warning_patcher = patch.object(QMessageBox, "warning", return_value=None)
        self.critical_patcher = patch.object(QMessageBox, "critical", return_value=None)
        self.information_patcher = patch.object(QMessageBox, "information", return_value=None)
        self.warning_patcher.start()
        self.critical_patcher.start()
        self.information_patcher.start()
        self.addCleanup(self.warning_patcher.stop)
        self.addCleanup(self.critical_patcher.stop)
        self.addCleanup(self.information_patcher.stop)

    def _load_primary_folder(self, folder: Path):
        emitted = []
        failures = []
        self.data_manager.dataLoaded.connect(
            lambda data, data_domain, folder_path, unit_context: emitted.append(
                (data, data_domain, folder_path, unit_context)
            )
        )
        self.data_manager.dataLoadFailed.connect(failures.append)
        self.data_manager.load_data_from_paths([str(folder)])
        self.assertFalse(failures, failures[0] if failures else None)
        self.assertEqual(len(emitted), 1)
        return emitted[0]


class PlotterMetadataTests(unittest.TestCase):
    def test_standard_figure_hover_uses_projected_axis_and_unit_metadata(self) -> None:
        df = pd.DataFrame({"Force_A": [1000.0, 1200.0]})
        df.index = pd.Index([1.0, 2.0], name="Freq [kHz]")
        df.attrs["trace_units"] = {"Force_A": "N"}
        df.attrs["trace_families"] = {"Force_A": "force"}

        figure = Plotter().create_standard_figure(df, "Projected Force", "Value [N]")

        self.assertEqual(figure.layout.xaxis.title.text, "Freq [kHz]")
        self.assertEqual(figure.layout.yaxis.title.text, "Value [N]")
        self.assertIn("Freq [kHz]", figure.data[0].hovertemplate)
        self.assertIn("Value [N]", figure.data[0].hovertemplate)


class PlotUnitProjectionControllerTests(PlotUnitProjectionBase):
    def test_single_data_frequency_projection_and_phase_plot_use_display_units(self) -> None:
        df, data_domain, _, unit_context = self._load_primary_folder(self.frequency_sample)
        selected_column = "I1 - STBD REAR MOUNT (CS-8012) T1"
        main_window = _build_main_window(
            df,
            data_domain,
            unit_context,
            display_units={"force": "N", "phase": "rad", "frequency": "kHz"},
            single_selected=selected_column,
            compare_selected=selected_column,
            interface="I1",
            side="STBD",
            time_domain_frequency=str(df["FREQ"].iloc[0]),
        )

        controller = PlotController(main_window)
        controller.update_single_data_plots()

        regular_plot = main_window.tab_single_data.regular_plot
        phase_plot = main_window.tab_single_data.phase_plot
        regular_df = next(iter(regular_plot.data_to_plot.values()))
        phase_df = next(iter(phase_plot.data_to_plot.values()))

        self.assertEqual(regular_plot.y_axis_title, "Value [N]")
        self.assertEqual(regular_df.index.name, "Freq [kHz]")
        self.assertAlmostEqual(regular_df.iloc[0, 0], df[selected_column].iloc[0] * 1000.0, places=6)
        self.assertTrue(main_window.tab_single_data.phase_visible)
        self.assertEqual(phase_plot.y_axis_title, "Phase [rad]")
        self.assertAlmostEqual(
            phase_df.iloc[0, 0],
            np.deg2rad(df[f"Phase_{selected_column}"].iloc[0]),
            places=6,
        )

    def test_computed_metrics_use_projected_units(self) -> None:
        df = pd.DataFrame({"TIME": [0.0, 0.001, 0.002], "Signal_A": [1.0, 2.0, 3.0], "DataFolder": ["sample"] * 3})
        unit_context = {
            "TIME": ColumnUnitContext.from_source_unit("TIME", None),
            "Signal_A": ColumnUnitContext.from_source_unit("Signal_A", "kN"),
            "DataFolder": ColumnUnitContext.from_source_unit("DataFolder", None),
        }
        main_window = _build_main_window(
            df,
            "TIME",
            unit_context,
            display_units={"time": "ms", "frequency": "kHz"},
            single_selected=PlotController.TIME_STEP_LABEL,
            side="STBD",
        )

        controller = PlotController(main_window)
        controller.update_single_data_plots()
        dt_plot = main_window.tab_single_data.regular_plot
        dt_df = next(iter(dt_plot.data_to_plot.values()))
        self.assertEqual(dt_plot.y_axis_title, "Time Step [ms]")
        self.assertTrue(np.isnan(dt_df.iloc[0, 0]))
        self.assertAlmostEqual(dt_df.iloc[1, 0], 1.0, places=6)

        main_window.tab_single_data.column_selector.setCurrentText(PlotController.FS_LABEL)
        controller.update_single_data_plots()
        fs_plot = main_window.tab_single_data.regular_plot
        fs_df = next(iter(fs_plot.data_to_plot.values()))
        self.assertEqual(fs_plot.y_axis_title, "Sampling Rate [kHz]")
        self.assertAlmostEqual(fs_df.iloc[1, 0], 1.0, places=6)

    def test_interface_data_uses_mixed_units_label_for_grouped_projection(self) -> None:
        df = pd.DataFrame(
            {
                "TIME": [0.0, 1.0],
                "I1 - STBD Mount T1": [1.0, 2.0],
                "I1 - STBD Mount T2": [0.1, 0.2],
                "I1 - STBD Mount R1": [0.5, 1.0],
                "I1 - STBD Mount R2": [1.0, 2.0],
            }
        )
        unit_context = {
            "TIME": ColumnUnitContext.from_source_unit("TIME", None),
            "I1 - STBD Mount T1": ColumnUnitContext.from_source_unit("I1 - STBD Mount T1", "kN"),
            "I1 - STBD Mount T2": ColumnUnitContext.from_source_unit("I1 - STBD Mount T2", "m"),
            "I1 - STBD Mount R1": ColumnUnitContext.from_source_unit("I1 - STBD Mount R1", "kN*m"),
            "I1 - STBD Mount R2": ColumnUnitContext.from_source_unit("I1 - STBD Mount R2", "deg", family_hint="angular displacement"),
        }
        main_window = _build_main_window(
            df,
            "TIME",
            unit_context,
            display_units={"force": "N", "displacement": "mm", "moment": "N*mm", "angular displacement": "rad"},
            interface="I1",
            side="STBD",
        )

        controller = PlotController(main_window)
        controller.update_interface_data_plots()

        t_plot = main_window.tab_interface_data.t_series_plot
        t_df = t_plot.data_to_plot
        self.assertEqual(t_plot.y_axis_title, "Mixed Units")
        self.assertAlmostEqual(t_df.iloc[0]["I1 - STBD Mount T1"], 1000.0, places=6)
        self.assertAlmostEqual(t_df.iloc[0]["I1 - STBD Mount T2"], 100.0, places=6)

    def test_part_loads_and_compare_part_loads_use_mixed_units_and_converted_values(self) -> None:
        df = pd.DataFrame(
            {
                "TIME": [0.0, 1.0],
                "Mount STBD T1": [1.0, 2.0],
                "Mount STBD T2": [0.1, 0.2],
                "Mount STBD R1": [0.5, 1.0],
                "Mount STBD R2": [1.0, 2.0],
            }
        )
        df_compare = pd.DataFrame(
            {
                "TIME": [0.0, 1.0],
                "Mount STBD T1": [0.9, 1.8],
                "Mount STBD T2": [0.09, 0.18],
                "Mount STBD R1": [0.45, 0.9],
                "Mount STBD R2": [0.9, 1.8],
            }
        )
        unit_context = {
            "TIME": ColumnUnitContext.from_source_unit("TIME", None),
            "Mount STBD T1": ColumnUnitContext.from_source_unit("Mount STBD T1", "kN"),
            "Mount STBD T2": ColumnUnitContext.from_source_unit("Mount STBD T2", "m"),
            "Mount STBD R1": ColumnUnitContext.from_source_unit("Mount STBD R1", "kN*m"),
            "Mount STBD R2": ColumnUnitContext.from_source_unit("Mount STBD R2", "deg", family_hint="angular displacement"),
        }
        main_window = _build_main_window(
            df,
            "TIME",
            unit_context,
            df_compare=df_compare,
            comparison_unit_context=unit_context,
            display_units={"force": "N", "displacement": "mm", "moment": "N*mm", "angular displacement": "rad"},
            side="STBD",
        )

        controller = PlotController(main_window)
        controller.update_part_loads_plots()
        controller.update_compare_part_loads_plots()

        part_plot = main_window.tab_part_loads.t_series_plot
        diff_plot = main_window.tab_compare_part_loads.t_series_plot
        self.assertEqual(part_plot.y_axis_title, "Mixed Units")
        self.assertEqual(diff_plot.y_axis_title, "Mixed Units")
        self.assertAlmostEqual(part_plot.data_to_plot.iloc[0]["Mount STBD T1"], 1000.0, places=6)
        self.assertAlmostEqual(part_plot.data_to_plot.iloc[0]["Mount STBD T2"], 100.0, places=6)
        self.assertAlmostEqual(diff_plot.data_to_plot.iloc[0][f"{PlotController.DELTA_SYMBOL} Mount STBD T1"], 100.0, places=6)
        self.assertAlmostEqual(diff_plot.data_to_plot.iloc[0][f"{PlotController.DELTA_SYMBOL} Mount STBD T2"], 10.0, places=6)

    def test_compare_data_absolute_difference_scales_and_relative_difference_stays_stable(self) -> None:
        df = pd.DataFrame({"TIME": [0.0, 1.0], "Force_A": [1.0, 2.0]})
        df_compare = pd.DataFrame({"TIME": [0.0, 1.0], "Force_A": [0.5, 1.5]})
        unit_context = {
            "TIME": ColumnUnitContext.from_source_unit("TIME", None),
            "Force_A": ColumnUnitContext.from_source_unit("Force_A", "kN"),
        }
        main_window = _build_main_window(
            df,
            "TIME",
            unit_context,
            df_compare=df_compare,
            comparison_unit_context=unit_context,
            display_units={"force": "kN"},
            single_selected="Force_A",
            compare_selected="Force_A",
        )
        controller = PlotController(main_window)

        controller.update_compare_data_plots()
        abs_kN = main_window.tab_compare_data.absolute_diff_plot.data_to_plot.iloc[:, 0].tolist()
        rel_kN = main_window.tab_compare_data.relative_diff_plot.data_to_plot.iloc[:, 0].tolist()

        main_window.unit_context = _apply_display_units(unit_context, {"force": "N"})
        main_window.comparison_unit_context = _apply_display_units(unit_context, {"force": "N"})
        main_window.active_display_units_by_family["force"] = "N"
        controller.update_compare_data_plots()
        abs_N = main_window.tab_compare_data.absolute_diff_plot.data_to_plot.iloc[:, 0].tolist()
        rel_N = main_window.tab_compare_data.relative_diff_plot.data_to_plot.iloc[:, 0].tolist()

        self.assertEqual(main_window.tab_compare_data.absolute_diff_plot.y_axis_title, "Value [N]")
        self.assertEqual(main_window.tab_compare_data.relative_diff_plot.y_axis_title, "Percent (%)")
        self.assertEqual(abs_kN, [0.5, 0.5])
        self.assertEqual(abs_N, [500.0, 500.0])
        self.assertEqual(rel_kN, rel_N)

    def test_time_domain_representation_projects_theta_frequency_title_and_trace_units(self) -> None:
        df = pd.DataFrame(
            {
                "FREQ": [1000.0],
                "Mount STBD T1": [1.0],
                "Phase_Mount STBD T1": [0.0],
                "Mount STBD T2": [0.1],
                "Phase_Mount STBD T2": [90.0],
            }
        )
        unit_context = {
            "FREQ": ColumnUnitContext.from_source_unit("FREQ", "Hz"),
            "Mount STBD T1": ColumnUnitContext.from_source_unit("Mount STBD T1", "kN"),
            "Phase_Mount STBD T1": ColumnUnitContext.from_source_unit("Phase_Mount STBD T1", "deg", family_hint="phase"),
            "Mount STBD T2": ColumnUnitContext.from_source_unit("Mount STBD T2", "m"),
            "Phase_Mount STBD T2": ColumnUnitContext.from_source_unit("Phase_Mount STBD T2", "deg", family_hint="phase"),
        }
        main_window = _build_main_window(
            df,
            "FREQ",
            unit_context,
            display_units={"force": "N", "displacement": "mm", "phase": "rad", "frequency": "kHz"},
            side="STBD",
            time_domain_frequency="1000.0",
        )

        controller = PlotController(main_window)
        controller.update_time_domain_represent_plot()

        time_domain_plot = main_window.tab_time_domain_represent.plot
        time_domain_df = time_domain_plot.data_to_plot
        self.assertEqual(time_domain_plot.y_axis_title, "Mixed Units")
        self.assertEqual(time_domain_df.index.name, "Theta [rad]")
        self.assertIn("1 kHz", time_domain_plot.title)
        self.assertAlmostEqual(time_domain_df.iloc[0]["Mount STBD T1"], 1000.0, places=6)
        self.assertAlmostEqual(time_domain_df.iloc[0]["Mount STBD T2"], 0.0, places=6)
        self.assertAlmostEqual(time_domain_df.index[180], np.pi, places=6)


class PlotUnitProjectionSmokeTests(PlotUnitProjectionBase):
    def test_frequency_sample_single_data_and_compare_projection_smoke(self) -> None:
        df, data_domain, _, unit_context = self._load_primary_folder(self.frequency_sample)
        selected_column = "I1 - STBD REAR MOUNT (CS-8012) T1"
        compare_df = df.copy(deep=True)
        compare_df[selected_column] = compare_df[selected_column] * 0.9
        main_window = _build_main_window(
            df,
            data_domain,
            unit_context,
            df_compare=compare_df,
            comparison_unit_context=unit_context,
            display_units={"force": "N", "phase": "rad", "frequency": "kHz"},
            single_selected=selected_column,
            compare_selected=selected_column,
            interface="I1",
            side="STBD",
            time_domain_frequency=str(df["FREQ"].iloc[0]),
        )

        controller = PlotController(main_window)
        controller.update_single_data_plots()
        controller.update_compare_data_plots()

        regular_df = next(iter(main_window.tab_single_data.regular_plot.data_to_plot.values()))
        absolute_diff_df = main_window.tab_compare_data.absolute_diff_plot.data_to_plot
        relative_diff_df = main_window.tab_compare_data.relative_diff_plot.data_to_plot

        self.assertEqual(main_window.tab_single_data.regular_plot.y_axis_title, "Value [N]")
        self.assertEqual(main_window.tab_single_data.phase_plot.y_axis_title, "Phase [rad]")
        self.assertEqual(regular_df.index.name, "Freq [kHz]")
        self.assertEqual(main_window.tab_compare_data.absolute_diff_plot.y_axis_title, "Value [N]")
        self.assertEqual(main_window.tab_compare_data.relative_diff_plot.y_axis_title, "Percent (%)")
        self.assertGreater(float(absolute_diff_df.iloc[0, 0]), 0.0)
        self.assertGreaterEqual(float(relative_diff_df.iloc[0, 0]), 0.0)

    def test_time_sample_single_data_part_loads_and_computed_metric_smoke(self) -> None:
        df, data_domain, _, unit_context = self._load_primary_folder(self.time_sample)
        selected_column = "I1 - STBD REAR MOUNT (CS-8012) T1"
        main_window = _build_main_window(
            df,
            data_domain,
            unit_context,
            display_units={"force": "N", "time": "ms"},
            single_selected=selected_column,
            interface="I1",
            side="STBD",
        )

        controller = PlotController(main_window)
        controller.update_single_data_plots()
        controller.update_part_loads_plots()
        main_window.tab_single_data.column_selector.setCurrentText(PlotController.TIME_STEP_LABEL)
        controller.update_single_data_plots()

        regular_plot = main_window.tab_single_data.regular_plot
        regular_df = next(iter(regular_plot.data_to_plot.values()))
        self.assertEqual(regular_plot.y_axis_title, "Time Step [ms]")
        self.assertEqual(main_window.tab_part_loads.t_series_plot.y_axis_title, "Value [N]")
        self.assertEqual(regular_df.index.name, "Time [ms]")
        self.assertTrue(np.isnan(regular_df.iloc[0, 0]))
        self.assertGreater(float(regular_df.iloc[1, 0]), 0.0)


if __name__ == "__main__":
    unittest.main()
