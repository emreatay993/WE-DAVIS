from __future__ import annotations

from collections import OrderedDict
import sys
from types import ModuleType
import unittest

import pandas as pd

from app.analysis.steady_state_time_history_export import (
    apply_half_cosine_soft_start,
    build_seconds_time_history_frame,
    build_time_history_csv_headers,
    convert_time_history_frame_for_export,
    resolve_frequency_to_hz,
)
from app.units import ColumnUnitContext


def _install_dialog_dependency_stubs() -> None:
    pyqt5_module = sys.modules.get("PyQt5", ModuleType("PyQt5"))
    qtcore_module = sys.modules.get("PyQt5.QtCore", ModuleType("PyQt5.QtCore"))
    qtgui_module = sys.modules.get("PyQt5.QtGui", ModuleType("PyQt5.QtGui"))
    qtwebengine_module = sys.modules.get(
        "PyQt5.QtWebEngineWidgets",
        ModuleType("PyQt5.QtWebEngineWidgets"),
    )
    qtwidgets_module = sys.modules.get("PyQt5.QtWidgets", ModuleType("PyQt5.QtWidgets"))

    class _Signal:
        def connect(self, *args, **kwargs) -> None:
            return None

    class _Widget:
        def __init__(self, *args, **kwargs) -> None:
            self.clicked = _Signal()
            self.currentIndexChanged = _Signal()
            self.textChanged = _Signal()
            self.toggled = _Signal()
            self.valueChanged = _Signal()
            self.activated = _Signal()

        def __getattr__(self, name):
            def _method(*args, **kwargs):
                return None

            return _method

    class _Layout(_Widget):
        def addRow(self, *args, **kwargs) -> None:
            return None

        def addWidget(self, *args, **kwargs) -> None:
            return None

        def addLayout(self, *args, **kwargs) -> None:
            return None

    class _QtNamespace:
        NoContextMenu = 0
        WindowMinimizeButtonHint = 1
        WindowMaximizeButtonHint = 2
        WidgetWithChildrenShortcut = 3

    qtcore_module.Qt = getattr(qtcore_module, "Qt", _QtNamespace)
    qtgui_module.QIntValidator = getattr(qtgui_module, "QIntValidator", _Widget)
    qtgui_module.QKeySequence = getattr(qtgui_module, "QKeySequence", _Widget)

    for class_name in (
        "QCheckBox",
        "QComboBox",
        "QDialog",
        "QDoubleSpinBox",
        "QFileDialog",
        "QGroupBox",
        "QLabel",
        "QLineEdit",
        "QMessageBox",
        "QPushButton",
        "QShortcut",
    ):
        setattr(qtwidgets_module, class_name, getattr(qtwidgets_module, class_name, _Widget))
    for class_name in ("QFormLayout", "QGridLayout", "QHBoxLayout", "QVBoxLayout"):
        setattr(qtwidgets_module, class_name, getattr(qtwidgets_module, class_name, _Layout))
    qtwebengine_module.QWebEngineView = getattr(qtwebengine_module, "QWebEngineView", _Widget)

    pyqt5_module.QtCore = qtcore_module
    pyqt5_module.QtGui = qtgui_module
    pyqt5_module.QtWebEngineWidgets = qtwebengine_module
    pyqt5_module.QtWidgets = qtwidgets_module

    sys.modules["PyQt5"] = pyqt5_module
    sys.modules["PyQt5.QtCore"] = qtcore_module
    sys.modules["PyQt5.QtGui"] = qtgui_module
    sys.modules["PyQt5.QtWebEngineWidgets"] = qtwebengine_module
    sys.modules["PyQt5.QtWidgets"] = qtwidgets_module

    plotter_module = sys.modules.get(
        "app.plotting.plotter",
        ModuleType("app.plotting.plotter"),
    )
    plotter_module.Plotter = getattr(plotter_module, "Plotter", type("Plotter", (), {}))
    plotter_module.load_fig_to_webview = getattr(
        plotter_module,
        "load_fig_to_webview",
        lambda *args, **kwargs: None,
    )
    sys.modules["app.plotting.plotter"] = plotter_module


_install_dialog_dependency_stubs()

from app.ui.steady_state_time_history_export_dialog import SteadyStateTimeHistoryExportDialog


class _TextInput:
    def __init__(self, text: str) -> None:
        self._text = text

    def text(self) -> str:
        return self._text


class _Selector:
    def __init__(self, text: str) -> None:
        self._text = text

    def currentText(self) -> str:
        return self._text


class _CheckedOption:
    def __init__(self, checked: bool) -> None:
        self._checked = checked

    def isChecked(self) -> bool:
        return self._checked


class _ValueControl:
    def __init__(self, value: float) -> None:
        self._value = value

    def value(self) -> float:
        return self._value


class _Label:
    def __init__(self) -> None:
        self._text = ""

    def setText(self, text: str) -> None:
        self._text = text

    def text(self) -> str:
        return self._text


class _Button:
    def __init__(self) -> None:
        self._enabled = True

    def setEnabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def isEnabled(self) -> bool:
        return self._enabled


class _Plotter:
    def create_standard_figure(self, *args, **kwargs):
        return None


class _ShortcutPlotter(_Plotter):
    def __init__(self) -> None:
        self.cycle_count = 0
        self.toggle_count = 0

    def cycle_legend_position(self) -> None:
        self.cycle_count += 1

    def toggle_legend_visibility(self) -> None:
        self.toggle_count += 1


class _WindowControlProbe:
    def __init__(self) -> None:
        self._flags = 4
        self.size_grip_enabled = None

    def windowFlags(self):
        return self._flags

    def setWindowFlags(self, flags) -> None:
        self._flags = flags

    def setSizeGripEnabled(self, enabled: bool) -> None:
        self.size_grip_enabled = enabled


class SteadyStateTimeHistoryExportTests(unittest.TestCase):
    def _build_dialog_proxy(
        self,
        *,
        cycles: int = 2,
        frequency_hz: float = 1.0,
        soft_start_enabled: bool = True,
        ramp_cycles: float = 1.0,
    ):
        dialog = SteadyStateTimeHistoryExportDialog.__new__(SteadyStateTimeHistoryExportDialog)
        dialog._current_plot_data = OrderedDict(
            {
                "Force_A": {
                    "y_data": [10.0] * 360,
                }
            }
        )
        dialog._interval_degrees = 90
        dialog._selected_frequency_value = frequency_hz
        dialog._selected_frequency_context = None
        dialog._trace_contexts = OrderedDict(
            {
                "Force_A": ColumnUnitContext.from_source_unit("Force_A", "N"),
            }
        )
        dialog._family_selectors = OrderedDict(
            {
                "time": _Selector("s"),
                "force": _Selector("N"),
            }
        )
        dialog._unknown_label_inputs = OrderedDict()
        dialog.cycles_input = _TextInput(str(cycles))
        dialog.soft_start_checkbox = _CheckedOption(soft_start_enabled)
        dialog.ramp_cycles_spin = _ValueControl(ramp_cycles)
        return dialog

    def _attach_preview_fakes(self, dialog) -> None:
        dialog.preview_status_label = _Label()
        dialog.export_button = _Button()
        dialog.preview_plot = object()
        dialog._plotter = _Plotter()

    def test_dialog_enables_fullscreen_window_controls(self):
        probe = _WindowControlProbe()

        SteadyStateTimeHistoryExportDialog._enable_fullscreen_window_controls(probe)

        self.assertTrue(probe._flags & 1)
        self.assertTrue(probe._flags & 2)
        self.assertTrue(probe.size_grip_enabled)

    def test_dialog_preview_shortcuts_reuse_plotter_legend_actions(self):
        dialog = self._build_dialog_proxy()
        dialog._plotter = _ShortcutPlotter()
        refresh_calls = []
        dialog._refresh_preview = lambda: refresh_calls.append("refresh")

        dialog._cycle_preview_legend_position()
        dialog._toggle_preview_legend_visibility()

        self.assertEqual(dialog._plotter.cycle_count, 1)
        self.assertEqual(dialog._plotter.toggle_count, 1)
        self.assertEqual(refresh_calls, ["refresh", "refresh"])

    def test_build_seconds_time_history_frame_uses_cycles_interval_and_inclusive_endpoint(self):
        one_cycle_plot_data = {
            "Force_A": {
                "y_data": list(range(360)) + [0],
            }
        }

        frame = build_seconds_time_history_frame(
            one_cycle_plot_data,
            interval_degrees=90,
            cycles=3,
            frequency_hz=2.0,
        )

        self.assertEqual(len(frame.index), 13)
        self.assertEqual(frame["Force_A"].tolist(), [0, 90, 180, 270, 0, 90, 180, 270, 0, 90, 180, 270, 0])
        self.assertAlmostEqual(frame["Time"].iloc[-1], 1.5, places=9)
        self.assertEqual(frame["Time"].is_unique, True)

    def test_apply_half_cosine_soft_start_zero_ramp_returns_defensive_copy(self):
        frame = pd.DataFrame(
            {
                "Time": [0.0, 0.5, 1.0],
                "Force_A": [10.0, 20.0, 30.0],
            },
            index=["start", "middle", "end"],
        )

        smoothed = apply_half_cosine_soft_start(
            frame,
            ramp_cycles=0.0,
            frequency_hz=1.0,
        )

        self.assertIsNot(smoothed, frame)
        pd.testing.assert_frame_equal(smoothed, frame)

        smoothed.loc["start", "Force_A"] = -99.0
        self.assertEqual(frame.loc["start", "Force_A"], 10.0)

    def test_apply_half_cosine_soft_start_preserves_time_boundary_and_schema(self):
        frame = pd.DataFrame(
            {
                "Time": [0.0, 0.5, 1.0, 1.5],
                "Force_A": [10.0, 10.0, 10.0, 10.0],
                "Moment_B": [2.0, 2.0, 2.0, 2.0],
            },
            index=["a", "b", "c", "d"],
        )

        smoothed = apply_half_cosine_soft_start(
            frame,
            ramp_cycles=1.0,
            frequency_hz=1.0,
        )

        self.assertEqual(smoothed.index.tolist(), frame.index.tolist())
        self.assertEqual(smoothed.columns.tolist(), ["Time", "Force_A", "Moment_B"])
        self.assertEqual(smoothed["Time"].tolist(), frame["Time"].tolist())
        self.assertEqual(len(smoothed.index), len(frame.index))
        self.assertAlmostEqual(smoothed["Force_A"].iloc[0], 0.0, places=12)
        self.assertAlmostEqual(smoothed["Force_A"].iloc[1], 5.0, places=12)
        self.assertAlmostEqual(smoothed["Force_A"].iloc[2], 10.0, places=12)
        self.assertAlmostEqual(smoothed["Force_A"].iloc[3], 10.0, places=12)
        self.assertAlmostEqual(smoothed["Moment_B"].iloc[0], 0.0, places=12)
        self.assertAlmostEqual(smoothed["Moment_B"].iloc[1], 1.0, places=12)
        self.assertAlmostEqual(smoothed["Moment_B"].iloc[2], 2.0, places=12)
        self.assertAlmostEqual(smoothed["Moment_B"].iloc[3], 2.0, places=12)

    def test_apply_half_cosine_soft_start_preserves_conversion_and_header_flow(self):
        frame = pd.DataFrame(
            {
                "Time": [0.0, 0.5, 1.0, 1.5],
                "Force_A": [1000.0, 1000.0, 1000.0, 1000.0],
            }
        )
        trace_contexts = {
            "Force_A": ColumnUnitContext.from_source_unit("Force_A", "N"),
        }

        smoothed = apply_half_cosine_soft_start(
            frame,
            ramp_cycles=1.0,
            frequency_hz=1.0,
        )
        converted = convert_time_history_frame_for_export(
            smoothed,
            trace_contexts=trace_contexts,
            family_units={"force": "kN", "time": "s"},
        )
        headers = build_time_history_csv_headers(
            converted.columns.tolist(),
            trace_contexts=trace_contexts,
            family_units={"force": "kN", "time": "s"},
        )

        self.assertEqual(converted["Time"].tolist(), frame["Time"].tolist())
        self.assertAlmostEqual(converted["Force_A"].iloc[0], 0.0, places=12)
        self.assertAlmostEqual(converted["Force_A"].iloc[1], 0.5, places=12)
        self.assertAlmostEqual(converted["Force_A"].iloc[2], 1.0, places=12)
        self.assertAlmostEqual(converted["Force_A"].iloc[3], 1.0, places=12)
        self.assertEqual(headers, ["Time [s]", "Force_A [kN]"])

    def test_dialog_preview_frame_applies_enabled_soft_start(self):
        dialog = self._build_dialog_proxy(
            cycles=2,
            frequency_hz=1.0,
            soft_start_enabled=True,
            ramp_cycles=1.0,
        )

        frame, cycles, frequency_hz = dialog._build_preview_frame()

        self.assertEqual(cycles, 2)
        self.assertEqual(frequency_hz, 1.0)
        self.assertEqual(frame.columns.tolist(), ["Time [s]", "Force_A [N]"])
        self.assertAlmostEqual(frame["Force_A [N]"].iloc[0], 0.0, places=12)
        self.assertAlmostEqual(frame["Force_A [N]"].iloc[2], 5.0, places=12)
        self.assertAlmostEqual(frame["Force_A [N]"].iloc[4], 10.0, places=12)

    def test_dialog_preview_frame_skips_disabled_soft_start_even_when_ramp_exceeds_cycles(self):
        dialog = self._build_dialog_proxy(
            cycles=1,
            frequency_hz=1.0,
            soft_start_enabled=False,
            ramp_cycles=2.0,
        )

        frame, _, _ = dialog._build_preview_frame()

        self.assertEqual(frame["Force_A [N]"].tolist(), [10.0, 10.0, 10.0, 10.0, 10.0])

    def test_dialog_preview_frame_rejects_enabled_ramp_longer_than_export(self):
        dialog = self._build_dialog_proxy(
            cycles=1,
            frequency_hz=1.0,
            soft_start_enabled=True,
            ramp_cycles=2.0,
        )

        with self.assertRaisesRegex(ValueError, "total exported cycles"):
            dialog._build_preview_frame()

    def test_dialog_preview_error_path_disables_export_for_invalid_ramp(self):
        dialog = self._build_dialog_proxy(
            cycles=1,
            frequency_hz=1.0,
            soft_start_enabled=True,
            ramp_cycles=2.0,
        )
        self._attach_preview_fakes(dialog)

        dialog._refresh_preview()

        self.assertFalse(dialog.export_button.isEnabled())
        self.assertIn("total exported cycles", dialog.preview_status_label.text())

    def test_dialog_preview_status_includes_enabled_ramp_duration(self):
        dialog = self._build_dialog_proxy(
            frequency_hz=1000.0,
            soft_start_enabled=True,
            ramp_cycles=2.0,
        )

        status_text = dialog._build_preview_status_text(
            row_count=9,
            end_time=0.002,
            cycles=2,
            frequency_hz=1000.0,
        )

        self.assertIn("Soft start: 2 cycles / 0.002 s", status_text)

    def test_apply_half_cosine_soft_start_rejects_invalid_inputs(self):
        frame = pd.DataFrame(
            {
                "Time": [0.0, 0.5, 1.0],
                "Force_A": [10.0, 20.0, 30.0],
            }
        )

        with self.assertRaisesRegex(ValueError, "non-negative"):
            apply_half_cosine_soft_start(frame, ramp_cycles=-0.5, frequency_hz=1.0)
        with self.assertRaisesRegex(ValueError, "positive"):
            apply_half_cosine_soft_start(frame, ramp_cycles=0.5, frequency_hz=0.0)
        with self.assertRaisesRegex(ValueError, "total exported cycles"):
            apply_half_cosine_soft_start(frame, ramp_cycles=1.5, frequency_hz=1.0)

    def test_resolve_frequency_to_hz_converts_known_frequency_context(self):
        frequency_context = ColumnUnitContext.from_source_unit("FREQ", "kHz")
        self.assertAlmostEqual(resolve_frequency_to_hz(1.25, frequency_context), 1250.0, places=9)
        self.assertAlmostEqual(resolve_frequency_to_hz(50.0, None), 50.0, places=9)

    def test_convert_time_history_frame_for_export_applies_selected_units_only_to_known_families(self):
        frame = pd.DataFrame(
            {
                "Time": [0.0, 0.5],
                "Force_A": [1000.0, 2000.0],
                "Custom_B": [7.0, 8.0],
            }
        )
        trace_contexts = {
            "Force_A": ColumnUnitContext.from_source_unit("Force_A", "kN", display_unit="N"),
            "Custom_B": ColumnUnitContext.from_source_unit("Custom_B", "widget"),
        }

        converted = convert_time_history_frame_for_export(
            frame,
            trace_contexts=trace_contexts,
            family_units={"force": "kN", "time": "s"},
        )

        self.assertEqual(frame["Force_A"].tolist(), [1000.0, 2000.0])
        self.assertEqual(converted["Force_A"].tolist(), [1.0, 2.0])
        self.assertEqual(converted["Custom_B"].tolist(), [7.0, 8.0])

    def test_build_time_history_csv_headers_formats_known_and_manual_unknown_units(self):
        trace_contexts = {
            "Force_A": ColumnUnitContext.from_source_unit("Force_A", "kN", display_unit="N"),
            "Custom_B": ColumnUnitContext.from_source_unit("Custom_B", "widget"),
        }

        headers = build_time_history_csv_headers(
            ["Time", "Force_A", "Custom_B"],
            trace_contexts=trace_contexts,
            family_units={"force": "kN", "time": "s"},
            manual_unknown_labels={"Custom_B": "custom unit"},
        )

        self.assertEqual(headers, ["Time [s]", "Force_A [kN]", "Custom_B [custom unit]"])


if __name__ == "__main__":
    unittest.main()
