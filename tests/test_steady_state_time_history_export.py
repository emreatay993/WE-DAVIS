from __future__ import annotations

import unittest

import pandas as pd

from app.analysis.steady_state_time_history_export import (
    build_seconds_time_history_frame,
    build_time_history_csv_headers,
    convert_time_history_frame_for_export,
    resolve_frequency_to_hz,
)
from app.units import ColumnUnitContext


class SteadyStateTimeHistoryExportTests(unittest.TestCase):
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
