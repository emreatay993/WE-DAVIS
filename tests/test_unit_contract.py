from __future__ import annotations

import unittest

import pandas as pd

from app.units import (
    ColumnUnitContext,
    ConversionSpec,
    IncompatibleUnitConversionError,
    UnknownUnitError,
    build_unit_contexts,
    convert_dataframe_copy,
    convert_scalar,
    convert_series,
    get_compatible_units,
    infer_quantity_family,
    normalize_unit,
)


class UnitContractSmokeTests(unittest.TestCase):
    def test_normalize_common_moment_aliases(self) -> None:
        self.assertEqual(normalize_unit("kN m"), "kN*m")
        self.assertEqual(normalize_unit("N*m"), "N*m")
        self.assertEqual(normalize_unit(" N m "), "N*m")

    def test_builds_native_only_context_for_unknown_units(self) -> None:
        context = ColumnUnitContext.from_source_unit("CustomChannel", "psi")

        self.assertTrue(context.native_only)
        self.assertEqual(context.quantity_family, "unknown")
        self.assertEqual(context.display_unit, "psi")
        self.assertEqual(context.compatible_display_units, ("psi",))

    def test_rejects_incompatible_conversion_requests(self) -> None:
        with self.assertRaises(IncompatibleUnitConversionError):
            convert_scalar(1.0, "N", "s")


class UnitNormalizationTests(unittest.TestCase):
    def test_normalizes_angular_spellings(self) -> None:
        self.assertEqual(normalize_unit("deg / sec"), "deg/s")
        self.assertEqual(normalize_unit("deg/sec^2"), "deg/s^2")
        self.assertEqual(normalize_unit("°"), "deg")

    def test_normalizes_unknown_units_without_guessing(self) -> None:
        self.assertEqual(normalize_unit(" psi "), "psi")
        self.assertEqual(normalize_unit("custom unit"), "custom unit")


class QuantityFamilyInferenceTests(unittest.TestCase):
    def test_infers_expected_families_for_supported_units(self) -> None:
        expectations = {
            "s": "time",
            "Hz": "frequency",
            "kN": "force",
            "kN m": "moment",
            "m/s": "velocity",
            "mm/s^2": "acceleration",
            "rpm": "angular velocity",
            "deg/s^2": "angular acceleration",
        }

        for unit, expected_family in expectations.items():
            with self.subTest(unit=unit):
                self.assertEqual(infer_quantity_family(unit), expected_family)

    def test_uses_family_hint_for_ambiguous_angle_units(self) -> None:
        self.assertEqual(infer_quantity_family("deg"), "phase")
        self.assertEqual(infer_quantity_family("deg", family_hint="angular displacement"), "angular displacement")

    def test_returns_unknown_for_unmapped_units(self) -> None:
        self.assertEqual(infer_quantity_family("psi"), "unknown")


class UnitContextTests(unittest.TestCase):
    def test_builds_context_map_with_display_selection(self) -> None:
        contexts = build_unit_contexts(
            {"Force_A": "kN", "Phase_A": "deg", "Raw_A": "psi"},
            display_units_by_column={"Force_A": "N", "Phase_A": "rad"},
            family_hints_by_column={"Phase_A": "phase"},
        )

        self.assertEqual(contexts["Force_A"].quantity_family, "force")
        self.assertEqual(contexts["Force_A"].display_unit, "N")
        self.assertEqual(contexts["Force_A"].compatible_display_units, get_compatible_units("force"))

        self.assertEqual(contexts["Phase_A"].quantity_family, "phase")
        self.assertEqual(contexts["Phase_A"].display_unit, "rad")

        self.assertTrue(contexts["Raw_A"].native_only)
        self.assertEqual(contexts["Raw_A"].display_unit, "psi")

    def test_rejects_invalid_display_selection(self) -> None:
        with self.assertRaises(IncompatibleUnitConversionError):
            ColumnUnitContext.from_source_unit("Force_A", "N", display_unit="s")


class ConversionHelperTests(unittest.TestCase):
    def test_converts_scalars_and_series_without_mutating_source(self) -> None:
        source_series = pd.Series([1000.0, 2500.0], name="Force_A")
        source_series_snapshot = source_series.copy(deep=True)

        converted_value = convert_scalar(1000.0, "N", "kN")
        converted_series = convert_series(source_series, "N", "kN")

        self.assertEqual(converted_value, 1.0)
        pd.testing.assert_series_equal(
            converted_series,
            pd.Series([1.0, 2.5], name="Force_A"),
        )
        pd.testing.assert_series_equal(source_series, source_series_snapshot)

    def test_converts_dataframe_copies_without_mutating_source_frame(self) -> None:
        source_frame = pd.DataFrame(
            {
                "Force_A": [1000.0, 2500.0],
                "Disp_A": [10.0, 15.0],
            }
        )
        source_snapshot = source_frame.copy(deep=True)
        source_view = source_frame[["Force_A", "Disp_A"]]

        converted_view = convert_dataframe_copy(
            source_view,
            {
                "Force_A": ConversionSpec("N", "kN"),
                "Disp_A": ConversionSpec("mm", "m"),
            },
        )

        expected_view = pd.DataFrame(
            {
                "Force_A": [1.0, 2.5],
                "Disp_A": [0.01, 0.015],
            }
        )

        pd.testing.assert_frame_equal(converted_view, expected_view)
        pd.testing.assert_frame_equal(source_frame, source_snapshot)
        pd.testing.assert_frame_equal(source_view, source_snapshot[["Force_A", "Disp_A"]])

    def test_rejects_unknown_units(self) -> None:
        with self.assertRaises(UnknownUnitError):
            convert_scalar(1.0, "psi", "kN")


if __name__ == "__main__":
    unittest.main()
