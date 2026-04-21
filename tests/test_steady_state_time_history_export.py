from __future__ import annotations

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
