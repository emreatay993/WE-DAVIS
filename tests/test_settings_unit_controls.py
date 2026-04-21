from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from types import MethodType, ModuleType, SimpleNamespace

import pandas as pd


def _install_pyqt5_stub() -> None:
    pyqt5_module = sys.modules.get("PyQt5", ModuleType("PyQt5"))
    qtcore_module = sys.modules.get("PyQt5.QtCore", ModuleType("PyQt5.QtCore"))
    qtwidgets_module = sys.modules.get("PyQt5.QtWidgets", ModuleType("PyQt5.QtWidgets"))
    qtgui_module = sys.modules.get("PyQt5.QtGui", ModuleType("PyQt5.QtGui"))

    class _BoundSignal:
        def __init__(self) -> None:
            self._slots = []

        def connect(self, slot) -> None:
            self._slots.append(slot)

        def emit(self, *args, **kwargs) -> None:
            for slot in list(self._slots):
                try:
                    slot(*args, **kwargs)
                except TypeError:
                    slot()

        __call__ = emit

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

    class _QtNamespace:
        Checked = 2
        AlignBottom = 0
        LeftDockWidgetArea = 0
        Key_K = 75
        Key_L = 76

    class _WidgetBase:
        def __init__(self, parent=None) -> None:
            self.parent = parent
            self._layout = None
            self._visible = True
            self._enabled = True
            self._signals_blocked = False
            self._stylesheet = ""
            self._tooltip = ""

        def setLayout(self, layout) -> None:
            self._layout = layout

        def layout(self):
            return self._layout

        def setVisible(self, visible: bool) -> None:
            self._visible = visible

        def isVisible(self) -> bool:
            return self._visible

        def setEnabled(self, enabled: bool) -> None:
            self._enabled = enabled

        def isEnabled(self) -> bool:
            return self._enabled

        def blockSignals(self, blocked: bool) -> None:
            self._signals_blocked = blocked

        def setStyleSheet(self, stylesheet: str) -> None:
            self._stylesheet = stylesheet

        def setToolTip(self, tooltip: str) -> None:
            self._tooltip = tooltip

        def setParent(self, parent) -> None:
            self.parent = parent

        def deleteLater(self) -> None:
            return None

    class _LayoutItem:
        def __init__(self, value) -> None:
            self.value = value

        def widget(self):
            return self.value if isinstance(self.value, _WidgetBase) else None

        def layout(self):
            return self.value if isinstance(self.value, _LayoutBase) else None

    class _LayoutBase:
        def __init__(self, parent=None) -> None:
            self.parent = parent
            self.items = []
            self.contents_margins = (0, 0, 0, 0)

        def addWidget(self, widget, alignment=None) -> None:
            self.items.append(widget)

        def addLayout(self, layout) -> None:
            self.items.append(layout)

        def addStretch(self) -> None:
            self.items.append("stretch")

        def setContentsMargins(self, left, top, right, bottom) -> None:
            self.contents_margins = (left, top, right, bottom)

        def removeWidget(self, widget) -> None:
            self.items = [item for item in self.items if item is not widget]

        def count(self) -> int:
            return len(self.items)

        def takeAt(self, index: int):
            value = self.items.pop(index)
            return _LayoutItem(value)

    class QWidget(_WidgetBase):
        pass

    class QGroupBox(QWidget):
        def __init__(self, title="", parent=None) -> None:
            super().__init__(parent)
            self.title = title

    class QLabel(QWidget):
        def __init__(self, text="", parent=None) -> None:
            super().__init__(parent)
            self._text = text
            self.word_wrap = False

        def setText(self, text: str) -> None:
            self._text = text

        def text(self) -> str:
            return self._text

        def setWordWrap(self, enabled: bool) -> None:
            self.word_wrap = enabled

    class QComboBox(QWidget):
        currentIndexChanged = _SignalDescriptor()

        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self._items = []
            self._current_index = -1

        def addItems(self, items) -> None:
            items = list(items)
            self._items.extend(items)
            if self._current_index == -1 and self._items:
                self._current_index = 0

        def clear(self) -> None:
            self._items = []
            self._current_index = -1

        def setCurrentText(self, text: str) -> None:
            if text not in self._items:
                return
            next_index = self._items.index(text)
            if next_index == self._current_index:
                return
            self._current_index = next_index
            if not self._signals_blocked:
                self.currentIndexChanged.emit(next_index)

        def currentText(self) -> str:
            if 0 <= self._current_index < len(self._items):
                return self._items[self._current_index]
            return ""

        def count(self) -> int:
            return len(self._items)

        def itemText(self, index: int) -> str:
            return self._items[index]

    class QCheckBox(QWidget):
        stateChanged = _SignalDescriptor()

        def __init__(self, text="", parent=None) -> None:
            super().__init__(parent)
            self.text = text
            self._checked = False

        def setChecked(self, checked: bool) -> None:
            checked = bool(checked)
            if checked == self._checked:
                return
            self._checked = checked
            if not self._signals_blocked:
                self.stateChanged.emit(_QtNamespace.Checked if checked else 0)

        def isChecked(self) -> bool:
            return self._checked

    class QLineEdit(QWidget):
        textChanged = _SignalDescriptor()

        def __init__(self, text="", parent=None) -> None:
            super().__init__(parent)
            self._text = text

        def setText(self, text: str) -> None:
            if text == self._text:
                return
            self._text = text
            if not self._signals_blocked:
                self.textChanged.emit(text)

        def text(self) -> str:
            return self._text

    class QDoubleSpinBox(QWidget):
        valueChanged = _SignalDescriptor()

        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self._value = 0.0

        def setRange(self, minimum: float, maximum: float) -> None:
            self.minimum = minimum
            self.maximum = maximum

        def setSingleStep(self, step: float) -> None:
            self.step = step

        def setDecimals(self, decimals: int) -> None:
            self.decimals = decimals

        def setValue(self, value: float) -> None:
            value = float(value)
            if value == self._value:
                return
            self._value = value
            if not self._signals_blocked:
                self.valueChanged.emit(value)

        def value(self) -> float:
            return self._value

    class QVBoxLayout(_LayoutBase):
        pass

    class QHBoxLayout(_LayoutBase):
        pass

    class QMainWindow(QWidget):
        pass

    class QTabWidget(QWidget):
        currentChanged = _SignalDescriptor()

    class QMenuBar(QWidget):
        pass

    class QMenu(QWidget):
        pass

    class QAction(QObject):
        triggered = _SignalDescriptor()

        def __init__(self, text="", parent=None) -> None:
            super().__init__(parent)
            self.text = text

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

    class QFileDialog:
        @staticmethod
        def getExistingDirectory(*args, **kwargs):
            return ""

        @staticmethod
        def getSaveFileName(*args, **kwargs):
            return "", ""

        @staticmethod
        def Options():
            return None

    class QApplication:
        @staticmethod
        def processEvents() -> None:
            return None

    class QIcon:
        def __init__(self, *args, **kwargs) -> None:
            return None

    def pyqtSignal(*args, **kwargs):
        return _SignalDescriptor()

    def pyqtSlot(*args, **kwargs):
        def decorator(function):
            return function
        return decorator

    qtcore_module.QObject = getattr(qtcore_module, "QObject", QObject)
    qtcore_module.QCoreApplication = getattr(qtcore_module, "QCoreApplication", QCoreApplication)
    qtcore_module.QUrl = getattr(qtcore_module, "QUrl", QUrl)
    qtcore_module.Qt = getattr(qtcore_module, "Qt", _QtNamespace)
    qtcore_module.pyqtSignal = pyqtSignal
    qtcore_module.pyqtSlot = pyqtSlot

    qtwidgets_module.QAction = getattr(qtwidgets_module, "QAction", QAction)
    qtwidgets_module.QApplication = getattr(qtwidgets_module, "QApplication", QApplication)
    qtwidgets_module.QCheckBox = getattr(qtwidgets_module, "QCheckBox", QCheckBox)
    qtwidgets_module.QComboBox = getattr(qtwidgets_module, "QComboBox", QComboBox)
    qtwidgets_module.QDoubleSpinBox = getattr(qtwidgets_module, "QDoubleSpinBox", QDoubleSpinBox)
    qtwidgets_module.QFileDialog = getattr(qtwidgets_module, "QFileDialog", QFileDialog)
    qtwidgets_module.QGroupBox = getattr(qtwidgets_module, "QGroupBox", QGroupBox)
    qtwidgets_module.QHBoxLayout = getattr(qtwidgets_module, "QHBoxLayout", QHBoxLayout)
    qtwidgets_module.QLabel = getattr(qtwidgets_module, "QLabel", QLabel)
    qtwidgets_module.QLineEdit = getattr(qtwidgets_module, "QLineEdit", QLineEdit)
    qtwidgets_module.QMainWindow = getattr(qtwidgets_module, "QMainWindow", QMainWindow)
    qtwidgets_module.QMenu = getattr(qtwidgets_module, "QMenu", QMenu)
    qtwidgets_module.QMenuBar = getattr(qtwidgets_module, "QMenuBar", QMenuBar)
    qtwidgets_module.QMessageBox = getattr(qtwidgets_module, "QMessageBox", QMessageBox)
    qtwidgets_module.QTabWidget = getattr(qtwidgets_module, "QTabWidget", QTabWidget)
    qtwidgets_module.QVBoxLayout = getattr(qtwidgets_module, "QVBoxLayout", QVBoxLayout)
    qtwidgets_module.QWidget = getattr(qtwidgets_module, "QWidget", QWidget)

    qtgui_module.QIcon = getattr(qtgui_module, "QIcon", QIcon)

    if not hasattr(qtwidgets_module.QFileDialog, "getSaveFileName"):
        qtwidgets_module.QFileDialog.getSaveFileName = staticmethod(QFileDialog.getSaveFileName)
    if not hasattr(qtwidgets_module.QFileDialog, "Options"):
        qtwidgets_module.QFileDialog.Options = staticmethod(QFileDialog.Options)

    pyqt5_module.QtCore = qtcore_module
    pyqt5_module.QtWidgets = qtwidgets_module
    pyqt5_module.QtGui = qtgui_module

    sys.modules["PyQt5"] = pyqt5_module
    sys.modules["PyQt5.QtCore"] = qtcore_module
    sys.modules["PyQt5.QtWidgets"] = qtwidgets_module
    sys.modules["PyQt5.QtGui"] = qtgui_module


def _install_plotly_stub() -> None:
    if "plotly" in sys.modules:
        return

    plotly_module = ModuleType("plotly")
    graph_objects_module = ModuleType("plotly.graph_objects")

    class Figure:
        def __init__(self, *args, **kwargs) -> None:
            return None

    graph_objects_module.Figure = Figure
    plotly_module.graph_objects = graph_objects_module
    sys.modules["plotly"] = plotly_module
    sys.modules["plotly.graph_objects"] = graph_objects_module


def _install_main_window_dependency_stubs() -> None:
    stub_modules = {
        "app.ui.directory_tree_dock": "DirectoryTreeDock",
        "app.ui.tab_single_data": "SingleDataTab",
        "app.ui.tab_interface_data": "InterfaceDataTab",
        "app.ui.tab_part_loads": "PartLoadsTab",
        "app.ui.tab_time_domain_represent": "TimeDomainRepresentTab",
        "app.ui.tab_compare_data": "CompareDataTab",
        "app.ui.tab_compare_part_loads": "ComparePartLoadsTab",
        "app.plotting.plotter": "Plotter",
        "app.controllers.action_handler": "ActionHandler",
    }

    for module_name, class_name in stub_modules.items():
        if module_name in sys.modules:
            continue
        module = ModuleType(module_name)
        setattr(module, class_name, type(class_name, (), {}))
        sys.modules[module_name] = module


def _install_analysis_stub() -> None:
    module_name = "app.analysis.data_processing"
    if module_name in sys.modules:
        return

    module = ModuleType(module_name)
    module.apply_data_section = lambda df, *args, **kwargs: df
    module.apply_tukey_window = lambda df, *args, **kwargs: df
    module.apply_low_pass_filter = lambda df, *args, **kwargs: df
    module.compute_time_step_series = lambda *args, **kwargs: pd.Series(dtype=float)
    module.compute_sampling_rate_series = lambda *args, **kwargs: pd.Series(dtype=float)
    module.build_series_by_folder = lambda *args, **kwargs: {}
    module.build_dt_by_folder = lambda *args, **kwargs: {}
    module.build_fs_by_folder = lambda *args, **kwargs: {}
    module.build_multi_series_for_single = lambda *args, **kwargs: pd.DataFrame()
    sys.modules[module_name] = module


_install_pyqt5_stub()
_install_plotly_stub()
_install_main_window_dependency_stubs()
_install_analysis_stub()

from app.controllers.plot_controller import PlotController
from app.main_window import MainWindow
from app.ui.tab_settings import SettingsTab
from app.units import ColumnUnitContext


class SettingsTabUnitControlsTests(unittest.TestCase):
    def test_configure_unit_controls_renders_expected_widgets(self) -> None:
        tab = SettingsTab()
        summary_text = "Detected source units by quantity family: Force: kN; Phase: deg."

        tab.configure_unit_controls(
            family_controls=[
                {
                    "family": "force",
                    "label": "Force",
                    "compatible_units": ("N", "kN"),
                    "selected_unit": "kN",
                    "source_units": ["kN"],
                },
                {
                    "family": "phase",
                    "label": "Phase",
                    "compatible_units": ("rad", "deg"),
                    "selected_unit": "deg",
                    "source_units": ["deg"],
                },
            ],
            summary_text=summary_text,
            export_unit_mode=SettingsTab.EXPORT_DISPLAY_UNITS,
        )

        self.assertEqual(tab.legend_font_size_selector.currentText(), "10")
        self.assertEqual(tab.default_font_size_selector.currentText(), "12")
        self.assertEqual(tab.opacity_spin.value(), 0.75)
        self.assertEqual(sorted(tab.display_unit_selectors_by_family), ["force", "phase"])
        self.assertEqual(tab.display_unit_selectors_by_family["force"].count(), 2)
        self.assertEqual(tab.display_unit_selectors_by_family["force"].itemText(0), "N")
        self.assertEqual(tab.display_unit_selectors_by_family["force"].itemText(1), "kN")
        self.assertEqual(tab.export_unit_selector.count(), 2)
        self.assertEqual(tab.export_unit_selector.itemText(0), SettingsTab.EXPORT_SOURCE_UNITS)
        self.assertEqual(tab.export_unit_selector.itemText(1), SettingsTab.EXPORT_DISPLAY_UNITS)
        self.assertEqual(tab.export_unit_selector.currentText(), SettingsTab.EXPORT_DISPLAY_UNITS)
        self.assertEqual(tab.unit_summary_label.text(), summary_text)
        self.assertIn("Full Data CSV uses the current display units", tab.export_unit_notice_label.text())
        self.assertIn("Source Units keeps detected file units", tab.export_unit_notice_label.text())
        self.assertIn("Display Units converts", tab.export_unit_notice_label.text())
        self.assertFalse(tab.display_unit_placeholder_label.isVisible())

    def test_unit_control_changes_emit_settings_changed(self) -> None:
        tab = SettingsTab()
        emitted = []
        tab.settings_changed.connect(lambda: emitted.append("changed"))

        tab.configure_unit_controls(
            family_controls=[
                {
                    "family": "force",
                    "label": "Force",
                    "compatible_units": ("N", "kN"),
                    "selected_unit": "kN",
                    "source_units": ["kN"],
                }
            ],
            summary_text="Detected source units by quantity family: Force: kN.",
            export_unit_mode=SettingsTab.EXPORT_SOURCE_UNITS,
        )

        tab.display_unit_selectors_by_family["force"].setCurrentText("N")
        tab.export_unit_selector.setCurrentText(SettingsTab.EXPORT_DISPLAY_UNITS)

        self.assertEqual(tab.get_display_unit_selections(), {"force": "N"})
        self.assertEqual(tab.get_export_unit_mode(), SettingsTab.EXPORT_DISPLAY_UNITS)
        self.assertGreaterEqual(len(emitted), 2)


class MainWindowUnitStateTests(unittest.TestCase):
    def _build_harness(self):
        recorded_controls = {}

        class SettingsTabSpy:
            def configure_unit_controls(self, family_controls, summary_text, export_unit_mode):
                recorded_controls["family_controls"] = family_controls
                recorded_controls["summary_text"] = summary_text
                recorded_controls["export_unit_mode"] = export_unit_mode

            def get_display_unit_selections(self):
                return {"force": "N", "phase": "rad", "frequency": "kHz"}

            def get_export_unit_mode(self):
                return SettingsTab.EXPORT_DISPLAY_UNITS

        harness = SimpleNamespace(
            raw_primary_df=None,
            raw_comparison_df=None,
            df=None,
            df_compare=None,
            raw_data_folder=None,
            unit_context={},
            comparison_unit_context={},
            raw_unit_context={},
            raw_comparison_unit_context={},
            active_display_units_by_family={},
            export_unit_mode=SettingsTab.EXPORT_SOURCE_UNITS,
            tab_settings=SettingsTabSpy(),
        )

        method_names = [
            "_derive_default_display_units",
            "_apply_display_units_to_context",
            "_rebuild_display_unit_contexts",
            "_build_unit_family_controls",
            "_build_unit_summary_text",
            "_refresh_settings_unit_controls",
            "_set_primary_dataset_state",
            "_set_comparison_dataset_state",
            "apply_unit_preferences",
            "apply_unit_preferences_from_settings",
        ]
        for method_name in method_names:
            setattr(harness, method_name, MethodType(getattr(MainWindow, method_name), harness))

        return harness, recorded_controls

    def test_main_window_tracks_raw_and_active_unit_state_separately(self) -> None:
        harness, recorded_controls = self._build_harness()

        primary_df = pd.DataFrame({"FREQ": [5.0], "Force_A": [10.0], "Phase_Force_A": [15.0]})
        comparison_df = pd.DataFrame({"FREQ": [5.0], "Force_A": [9.0], "Phase_Force_A": [14.0]})
        primary_context = {
            "FREQ": ColumnUnitContext.from_source_unit("FREQ", "Hz"),
            "Force_A": ColumnUnitContext.from_source_unit("Force_A", "kN"),
            "Phase_Force_A": ColumnUnitContext.from_source_unit("Phase_Force_A", "deg", family_hint="phase"),
        }
        comparison_context = {
            "FREQ": ColumnUnitContext.from_source_unit("FREQ", "Hz"),
            "Force_A": ColumnUnitContext.from_source_unit("Force_A", "kN"),
            "Phase_Force_A": ColumnUnitContext.from_source_unit("Phase_Force_A", "deg", family_hint="phase"),
        }

        harness._set_primary_dataset_state(primary_df, str(Path("sample")), primary_context)
        harness._set_comparison_dataset_state(comparison_df, comparison_context)

        self.assertIs(harness.df, primary_df)
        self.assertIs(harness.df_compare, comparison_df)
        self.assertIsNot(harness.raw_primary_df, primary_df)
        self.assertIsNot(harness.raw_comparison_df, comparison_df)
        pd.testing.assert_frame_equal(harness.raw_primary_df, primary_df)
        pd.testing.assert_frame_equal(harness.raw_comparison_df, comparison_df)
        self.assertEqual(
            harness.active_display_units_by_family,
            {"frequency": "Hz", "force": "kN", "phase": "deg"},
        )

        harness.apply_unit_preferences(
            {"force": "N", "phase": "rad", "frequency": "kHz"},
            SettingsTab.EXPORT_DISPLAY_UNITS,
        )
        harness._refresh_settings_unit_controls()

        self.assertEqual(harness.export_unit_mode, SettingsTab.EXPORT_DISPLAY_UNITS)
        self.assertEqual(harness.raw_unit_context["Force_A"].display_unit, "kN")
        self.assertEqual(harness.unit_context["Force_A"].display_unit, "N")
        self.assertEqual(harness.raw_comparison_unit_context["Phase_Force_A"].display_unit, "deg")
        self.assertEqual(harness.comparison_unit_context["Phase_Force_A"].display_unit, "rad")
        self.assertEqual(recorded_controls["export_unit_mode"], SettingsTab.EXPORT_DISPLAY_UNITS)
        self.assertEqual(
            {control["family"]: control["selected_unit"] for control in recorded_controls["family_controls"]},
            {"frequency": "kHz", "force": "N", "phase": "rad"},
        )
        self.assertIn("Detected source units by quantity family", recorded_controls["summary_text"])


class PlotControllerSettingsRefreshTests(unittest.TestCase):
    def test_update_all_plots_from_settings_uses_existing_settings_refresh_path(self) -> None:
        settings_tab = SettingsTab()
        settings_tab.configure_unit_controls(
            family_controls=[
                {
                    "family": "force",
                    "label": "Force",
                    "compatible_units": ("N", "kN"),
                    "selected_unit": "N",
                    "source_units": ["kN"],
                }
            ],
            summary_text="Detected source units by quantity family: Force: kN.",
            export_unit_mode=SettingsTab.EXPORT_DISPLAY_UNITS,
        )

        captured = {}
        main_window = SimpleNamespace(
            plotter=SimpleNamespace(
                legend_font_size=None,
                default_font_size=None,
                hover_font_size=None,
                hover_mode=None,
                trace_opacity=None,
            ),
            tab_settings=settings_tab,
            df=pd.DataFrame({"TIME": [0.0], "Signal_A": [1.0]}),
            df_compare=None,
            data_domain="TIME",
        )

        def apply_unit_preferences_from_settings():
            captured["display_units"] = settings_tab.get_display_unit_selections()
            captured["export_unit_mode"] = settings_tab.get_export_unit_mode()

        main_window.apply_unit_preferences_from_settings = apply_unit_preferences_from_settings

        controller = PlotController(main_window)
        called = []
        controller.update_single_data_plots = lambda: called.append("single")
        controller.update_interface_data_plots = lambda: called.append("interface")
        controller.update_part_loads_plots = lambda: called.append("part_loads")
        controller.update_time_domain_represent_plot = lambda: called.append("time_domain")
        controller.update_compare_data_plots = lambda: called.append("compare_data")
        controller.update_compare_part_loads_plots = lambda: called.append("compare_part_loads")

        controller.update_all_plots_from_settings()

        self.assertEqual(captured["display_units"], {"force": "N"})
        self.assertEqual(captured["export_unit_mode"], SettingsTab.EXPORT_DISPLAY_UNITS)
        self.assertEqual(
            called,
            [
                "single",
                "interface",
                "part_loads",
                "time_domain",
                "compare_data",
                "compare_part_loads",
            ],
        )
        self.assertEqual(main_window.plotter.legend_font_size, 10)
        self.assertEqual(main_window.plotter.default_font_size, 12)
        self.assertEqual(main_window.plotter.hover_font_size, 15)
        self.assertEqual(main_window.plotter.hover_mode, "closest")
        self.assertEqual(main_window.plotter.trace_opacity, 0.75)


if __name__ == "__main__":
    unittest.main()
