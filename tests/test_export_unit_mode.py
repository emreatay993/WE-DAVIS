from __future__ import annotations

import math
import sys
import unittest
from types import ModuleType
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd


def _install_pyqt5_stub() -> None:
    if "PyQt5" in sys.modules:
        return

    pyqt5_module = ModuleType("PyQt5")
    qtcore_module = ModuleType("PyQt5.QtCore")
    qtwidgets_module = ModuleType("PyQt5.QtWidgets")

    class QObject:
        def __init__(self, parent=None) -> None:
            self.parent = parent

    class QCoreApplication:
        _instance = None

        def __init__(self, *args, **kwargs) -> None:
            QCoreApplication._instance = self

        @staticmethod
        def instance():
            return QCoreApplication._instance

    class _Widget:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

        def exec_(self):
            return 0

    class QDialog(_Widget):
        Accepted = 1

    class QVBoxLayout(_Widget):
        def addWidget(self, *args, **kwargs) -> None:
            return None

        def addLayout(self, *args, **kwargs) -> None:
            return None

    class QHBoxLayout(QVBoxLayout):
        pass

    class QListWidget(_Widget):
        def setSelectionMode(self, *args, **kwargs) -> None:
            return None

        def addItem(self, *args, **kwargs) -> None:
            return None

        def selectedItems(self):
            return []

    class QListWidgetItem(_Widget):
        def setSelected(self, *args, **kwargs) -> None:
            return None

        def text(self):
            return ""

    class QPushButton(_Widget):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.clicked = SimpleNamespace(connect=lambda *a, **k: None)

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
        def getSaveFileName(*args, **kwargs):
            return "", ""

    class QComboBox(_Widget):
        def currentData(self):
            return None

    class QLabel(_Widget):
        pass

    class QGroupBox(_Widget):
        def setLayout(self, *args, **kwargs) -> None:
            return None

    class QAbstractItemView:
        ExtendedSelection = 1

    def pyqtSlot(*args, **kwargs):
        def decorator(function):
            return function

        return decorator

    qtcore_module.QObject = QObject
    qtcore_module.QCoreApplication = QCoreApplication
    qtcore_module.pyqtSlot = pyqtSlot

    qtwidgets_module.QDialog = QDialog
    qtwidgets_module.QVBoxLayout = QVBoxLayout
    qtwidgets_module.QHBoxLayout = QHBoxLayout
    qtwidgets_module.QListWidget = QListWidget
    qtwidgets_module.QAbstractItemView = QAbstractItemView
    qtwidgets_module.QListWidgetItem = QListWidgetItem
    qtwidgets_module.QPushButton = QPushButton
    qtwidgets_module.QMessageBox = QMessageBox
    qtwidgets_module.QFileDialog = QFileDialog
    qtwidgets_module.QComboBox = QComboBox
    qtwidgets_module.QLabel = QLabel
    qtwidgets_module.QGroupBox = QGroupBox

    pyqt5_module.QtCore = qtcore_module
    pyqt5_module.QtWidgets = qtwidgets_module

    sys.modules["PyQt5"] = pyqt5_module
    sys.modules["PyQt5.QtCore"] = qtcore_module
    sys.modules["PyQt5.QtWidgets"] = qtwidgets_module


try:
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QFileDialog, QMessageBox
except ModuleNotFoundError:
    _install_pyqt5_stub()
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QFileDialog, QMessageBox


def _install_scipy_stub() -> None:
    if "scipy.signal.windows" in sys.modules:
        return

    scipy_module = ModuleType("scipy")
    signal_module = ModuleType("scipy.signal")
    windows_module = ModuleType("scipy.signal.windows")
    windows_module.tukey = lambda *args, **kwargs: []
    signal_module.butter = lambda *args, **kwargs: ([], [])
    signal_module.filtfilt = lambda *args, **kwargs: []
    scipy_module.signal = signal_module
    signal_module.windows = windows_module
    sys.modules["scipy"] = scipy_module
    sys.modules["scipy.signal"] = signal_module
    sys.modules["scipy.signal.windows"] = windows_module


try:
    from scipy.signal.windows import tukey as _unused_tukey
except ModuleNotFoundError:
    _install_scipy_stub()


def _install_settings_tab_stub() -> None:
    module_name = "app.ui.tab_settings"
    if module_name in sys.modules:
        return

    module = ModuleType(module_name)

    class SettingsTab:
        EXPORT_SOURCE_UNITS = "Source Units"
        EXPORT_DISPLAY_UNITS = "Display Units"

    module.SettingsTab = SettingsTab
    sys.modules[module_name] = module


_install_settings_tab_stub()

from app.analysis.ansys_exporter import AnsysExportUnits, AnsysExporter
from app.controllers.action_handler import ActionHandler
from app.ui.tab_settings import SettingsTab
from app.units import ColumnUnitContext


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


class _Selector:
    def __init__(self, text: str) -> None:
        self._text = text

    def currentText(self) -> str:
        return self._text


class ExportUnitModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.qt_app = QtCore.QCoreApplication.instance() or QtCore.QCoreApplication([])

    def _build_handler(
        self,
        df: pd.DataFrame,
        raw_unit_context,
        *,
        data_domain: str,
        export_mode: str,
        display_units=None,
    ):
        display_units = dict(display_units or {})
        projected_context = _apply_display_units(raw_unit_context, display_units)
        main_window = SimpleNamespace(
            df=df.copy(deep=True),
            raw_primary_df=df.copy(deep=True),
            data_domain=data_domain,
            raw_unit_context=raw_unit_context,
            unit_context=projected_context,
            export_unit_mode=export_mode,
            active_display_units_by_family=display_units,
            tab_time_domain_represent=SimpleNamespace(
                interval_selector=_Selector("180"),
                current_plot_data={},
            ),
        )
        return ActionHandler(main_window, data_manager=SimpleNamespace()), main_window

    def test_ansys_export_uses_display_units_for_csv_and_template_inputs(self) -> None:
        df = pd.DataFrame(
            {
                "FREQ": [1000.0, 2000.0],
                "Mount STBD T1": [1.0, 2.0],
                "Mount STBD R1": [0.5, 1.0],
                "Phase_Mount STBD T1": [90.0, 180.0],
                "Phase_Mount STBD R1": [0.0, 45.0],
            }
        )
        raw_unit_context = {
            "FREQ": ColumnUnitContext.from_source_unit("FREQ", "Hz"),
            "Mount STBD T1": ColumnUnitContext.from_source_unit("Mount STBD T1", "kN"),
            "Mount STBD R1": ColumnUnitContext.from_source_unit("Mount STBD R1", "kN*m"),
            "Phase_Mount STBD T1": ColumnUnitContext.from_source_unit(
                "Phase_Mount STBD T1",
                "deg",
                family_hint="phase",
            ),
            "Phase_Mount STBD R1": ColumnUnitContext.from_source_unit(
                "Phase_Mount STBD R1",
                "deg",
                family_hint="phase",
            ),
        }
        handler, _ = self._build_handler(
            df,
            raw_unit_context,
            data_domain="FREQ",
            export_mode=SettingsTab.EXPORT_DISPLAY_UNITS,
            display_units={
                "frequency": "kHz",
                "force": "N",
                "moment": "N*mm",
                "phase": "rad",
            },
        )

        captured_exports = {}

        def _capture_to_csv(frame, path, *args, **kwargs):
            captured_exports[path] = frame.copy(deep=True)
            return None

        with patch.object(ActionHandler, "_get_sides_for_export", return_value=(["STBD"], (232, r"C:\ANSYS"))), \
                patch("app.controllers.action_handler.AnsysExporter") as exporter_cls, \
                patch.object(pd.DataFrame, "to_csv", autospec=True, side_effect=_capture_to_csv):
            handler.handle_ansys_export()

        exporter = exporter_cls.return_value
        exporter.create_harmonic_template.assert_called_once()
        exported_frame, exported_domain = exporter.create_harmonic_template.call_args.args[:2]
        exported_units = exporter.create_harmonic_template.call_args.kwargs["export_units"]

        self.assertEqual(exported_domain, "FREQ")
        self.assertEqual(
            exported_units,
            AnsysExportUnits(
                domain_unit="kHz",
                force_unit="N",
                moment_unit="N*mm",
                phase_unit="rad",
            ),
        )
        self.assertAlmostEqual(exported_frame["FREQ"].iloc[0], 1.0, places=6)
        self.assertAlmostEqual(exported_frame["Mount STBD T1"].iloc[0], 1000.0, places=6)
        self.assertAlmostEqual(exported_frame["Mount STBD R1"].iloc[0], 500000.0, places=6)
        self.assertAlmostEqual(exported_frame["Phase_Mount STBD T1"].iloc[0], math.pi / 2, places=6)
        self.assertIn("extracted_data_for_STBD_in_display_units.csv", captured_exports)
        self.assertIn("extracted_loads_of_all_selected_parts_in_display_units.csv", captured_exports)
        self.assertFalse(any("multiplied" in export_path for export_path in captured_exports))

    def test_time_domain_export_converts_displayed_plot_back_to_source_units(self) -> None:
        df = pd.DataFrame({"FREQ": [1000.0]})
        raw_unit_context = {
            "Force_A": ColumnUnitContext.from_source_unit("Force_A", "kN"),
        }
        handler, main_window = self._build_handler(
            df,
            raw_unit_context,
            data_domain="FREQ",
            export_mode=SettingsTab.EXPORT_SOURCE_UNITS,
            display_units={"force": "N", "phase": "rad"},
        )
        theta_radians = [math.radians(value) for value in range(361)]
        force_display_values = [float(value * 1000) for value in range(361)]
        main_window.tab_time_domain_represent.current_plot_data = {
            "Force_A": {
                "theta": theta_radians,
                "y_data": force_display_values,
            }
        }

        captured_exports = {}

        def _capture_to_csv(frame, path, *args, **kwargs):
            captured_exports[path] = frame.copy(deep=True)
            return None

        with patch.object(QFileDialog, "getSaveFileName", return_value=("time_export.csv", "CSV Files (*.csv)")), \
                patch.object(pd.DataFrame, "to_csv", autospec=True, side_effect=_capture_to_csv), \
                patch.object(QMessageBox, "information", return_value=None), \
                patch("app.controllers.action_handler.os.startfile", return_value=None):
            handler.handle_time_domain_represent_export()

        self.assertIn("time_export.csv", captured_exports)
        exported_frame = captured_exports["time_export.csv"]
        self.assertEqual(exported_frame["Theta"].tolist(), [0.0, 180.0, 360.0])
        self.assertEqual(exported_frame["Force_A"].tolist(), [0.0, 180.0, 360.0])

    def test_ansys_export_rejects_unsupported_quantity_family_before_template_creation(self) -> None:
        df = pd.DataFrame(
            {
                "FREQ": [1000.0],
                "Mount STBD T1": [0.25],
            }
        )
        raw_unit_context = {
            "FREQ": ColumnUnitContext.from_source_unit("FREQ", "Hz"),
            "Mount STBD T1": ColumnUnitContext.from_source_unit("Mount STBD T1", "m"),
        }
        handler, _ = self._build_handler(
            df,
            raw_unit_context,
            data_domain="FREQ",
            export_mode=SettingsTab.EXPORT_SOURCE_UNITS,
            display_units={"displacement": "mm"},
        )

        with patch.object(ActionHandler, "_get_sides_for_export", return_value=(["STBD"], (232, r"C:\ANSYS"))), \
                patch("app.controllers.action_handler.AnsysExporter") as exporter_cls, \
                patch.object(QMessageBox, "warning", return_value=None) as warning_box, \
                patch.object(pd.DataFrame, "to_csv", autospec=True) as to_csv:
            handler.handle_ansys_export()

        exporter_cls.assert_not_called()
        to_csv.assert_not_called()
        warning_box.assert_called_once()
        warning_text = warning_box.call_args.args[2]
        self.assertIn("expects 'force'", warning_text)
        self.assertIn("displacement", warning_text)

    def test_exporter_helper_converts_solver_tables_with_unit_service(self) -> None:
        source_table = pd.DataFrame({"Real_R1": [1500.0, 3000.0]})
        converted = AnsysExporter._convert_dataframe_to_unit(
            source_table,
            source_unit="N*mm",
            target_unit="N*m",
            family_hint="moment",
        )

        self.assertAlmostEqual(converted["Real_R1"].iloc[0], 1.5, places=6)
        self.assertAlmostEqual(converted["Real_R1"].iloc[1], 3.0, places=6)


if __name__ == "__main__":
    unittest.main()
