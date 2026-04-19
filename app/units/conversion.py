from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd

from .catalog import QuantityFamily, get_unit_definition, normalize_unit
from .errors import IncompatibleUnitConversionError, UnknownUnitError


@dataclass(frozen=True)
class ConversionSpec:
    source_unit: str
    target_unit: str
    family_hint: QuantityFamily | None = None


def get_conversion_factor(
    source_unit: str,
    target_unit: str,
    family_hint: QuantityFamily | None = None,
) -> float:
    source_definition = get_unit_definition(source_unit, family_hint=family_hint)
    target_definition = get_unit_definition(target_unit, family_hint=family_hint)

    normalized_source = normalize_unit(source_unit)
    normalized_target = normalize_unit(target_unit)

    if source_definition is None:
        raise UnknownUnitError(f"Unknown source unit: {normalized_source!r}")
    if target_definition is None:
        raise UnknownUnitError(f"Unknown target unit: {normalized_target!r}")
    if source_definition.quantity_family != target_definition.quantity_family:
        raise IncompatibleUnitConversionError(
            f"Cannot convert '{source_definition.canonical_name}' "
            f"({source_definition.quantity_family}) to '{target_definition.canonical_name}' "
            f"({target_definition.quantity_family})."
        )

    return source_definition.scale_to_base / target_definition.scale_to_base


def convert_scalar(
    value: float | int,
    source_unit: str,
    target_unit: str,
    family_hint: QuantityFamily | None = None,
) -> float | int:
    factor = get_conversion_factor(source_unit, target_unit, family_hint=family_hint)
    return value * factor


def convert_series(
    series: pd.Series,
    source_unit: str,
    target_unit: str,
    family_hint: QuantityFamily | None = None,
) -> pd.Series:
    factor = get_conversion_factor(source_unit, target_unit, family_hint=family_hint)
    converted = series.copy(deep=True)
    return converted * factor


def convert_dataframe_copy(
    frame: pd.DataFrame,
    conversions_by_column: Mapping[str, ConversionSpec],
) -> pd.DataFrame:
    converted = frame.copy(deep=True)
    for column_name, conversion in conversions_by_column.items():
        if column_name not in converted.columns:
            raise KeyError(f"Column '{column_name}' is not present in the provided frame.")
        converted.loc[:, column_name] = convert_series(
            converted.loc[:, column_name],
            source_unit=conversion.source_unit,
            target_unit=conversion.target_unit,
            family_hint=conversion.family_hint,
        )
    return converted


def convert_dataframe_columns(
    frame: pd.DataFrame,
    columns: list[str] | tuple[str, ...],
    source_unit: str,
    target_unit: str,
    family_hint: QuantityFamily | None = None,
) -> pd.DataFrame:
    return convert_dataframe_copy(
        frame,
        {
            column_name: ConversionSpec(
                source_unit=source_unit,
                target_unit=target_unit,
                family_hint=family_hint,
            )
            for column_name in columns
        },
    )
