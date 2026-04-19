from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from .catalog import QuantityFamily, get_compatible_units, infer_quantity_family, is_known_unit, normalize_unit
from .errors import IncompatibleUnitConversionError


@dataclass(frozen=True)
class ColumnUnitContext:
    column_name: str
    source_unit: str | None
    normalized_unit: str | None
    quantity_family: QuantityFamily
    compatible_display_units: tuple[str, ...]
    display_unit: str | None
    native_only: bool

    @classmethod
    def from_source_unit(
        cls,
        column_name: str,
        source_unit: str | None,
        display_unit: str | None = None,
        family_hint: QuantityFamily | None = None,
    ) -> "ColumnUnitContext":
        normalized_unit = normalize_unit(source_unit)
        quantity_family = infer_quantity_family(normalized_unit, family_hint=family_hint)

        if normalized_unit is None:
            return cls(
                column_name=column_name,
                source_unit=source_unit,
                normalized_unit=None,
                quantity_family="unknown",
                compatible_display_units=(),
                display_unit=None,
                native_only=True,
            )

        if not is_known_unit(normalized_unit):
            selected_display_unit = normalize_unit(display_unit) if display_unit is not None else normalized_unit
            if selected_display_unit != normalized_unit:
                raise IncompatibleUnitConversionError(
                    f"Column '{column_name}' is native-only and cannot switch display units."
                )
            return cls(
                column_name=column_name,
                source_unit=source_unit,
                normalized_unit=normalized_unit,
                quantity_family="unknown",
                compatible_display_units=(normalized_unit,),
                display_unit=normalized_unit,
                native_only=True,
            )

        compatible_display_units = get_compatible_units(quantity_family)
        selected_display_unit = normalize_unit(display_unit) if display_unit is not None else normalized_unit
        if selected_display_unit not in compatible_display_units:
            raise IncompatibleUnitConversionError(
                f"Display unit '{selected_display_unit}' is not compatible with '{normalized_unit}'."
            )

        return cls(
            column_name=column_name,
            source_unit=source_unit,
            normalized_unit=normalized_unit,
            quantity_family=quantity_family,
            compatible_display_units=compatible_display_units,
            display_unit=selected_display_unit,
            native_only=False,
        )

    def with_display_unit(self, display_unit: str | None) -> "ColumnUnitContext":
        if display_unit is None:
            return replace(self, display_unit=self.normalized_unit)

        normalized_display_unit = normalize_unit(display_unit)
        if self.native_only:
            if normalized_display_unit != self.display_unit:
                raise IncompatibleUnitConversionError(
                    f"Column '{self.column_name}' is native-only and cannot switch display units."
                )
            return self

        if normalized_display_unit not in self.compatible_display_units:
            raise IncompatibleUnitConversionError(
                f"Display unit '{display_unit}' is not compatible with family '{self.quantity_family}'."
            )

        return replace(self, display_unit=normalized_display_unit)


UnitContextMap = dict[str, ColumnUnitContext]


def build_unit_contexts(
    source_units_by_column: Mapping[str, str | None],
    display_units_by_column: Mapping[str, str] | None = None,
    family_hints_by_column: Mapping[str, QuantityFamily] | None = None,
) -> UnitContextMap:
    contexts: UnitContextMap = {}
    for column_name, source_unit in source_units_by_column.items():
        display_unit = None if display_units_by_column is None else display_units_by_column.get(column_name)
        family_hint = None if family_hints_by_column is None else family_hints_by_column.get(column_name)
        contexts[column_name] = ColumnUnitContext.from_source_unit(
            column_name=column_name,
            source_unit=source_unit,
            display_unit=display_unit,
            family_hint=family_hint,
        )
    return contexts
