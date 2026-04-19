from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Literal

from .errors import IncompatibleUnitConversionError

QuantityFamily = Literal[
    "time",
    "frequency",
    "phase",
    "force",
    "moment",
    "displacement",
    "velocity",
    "acceleration",
    "angular displacement",
    "angular velocity",
    "angular acceleration",
    "unknown",
]

QUANTITY_FAMILIES: tuple[QuantityFamily, ...] = (
    "time",
    "frequency",
    "phase",
    "force",
    "moment",
    "displacement",
    "velocity",
    "acceleration",
    "angular displacement",
    "angular velocity",
    "angular acceleration",
    "unknown",
)


@dataclass(frozen=True)
class UnitDefinition:
    canonical_name: str
    quantity_family: QuantityFamily
    scale_to_base: float
    aliases: tuple[str, ...] = ()


_UNIT_DEFINITIONS: tuple[UnitDefinition, ...] = (
    UnitDefinition("s", "time", 1.0, ("sec", "secs", "second", "seconds")),
    UnitDefinition("ms", "time", 1e-3, ("msec", "msecs", "millisecond", "milliseconds")),
    UnitDefinition("us", "time", 1e-6, ("usec", "usecs", "microsecond", "microseconds")),
    UnitDefinition("min", "time", 60.0, ("mins", "minute", "minutes")),
    UnitDefinition("h", "time", 3600.0, ("hr", "hrs", "hour", "hours")),
    UnitDefinition("Hz", "frequency", 1.0, ("hz",)),
    UnitDefinition("kHz", "frequency", 1e3, ("khz",)),
    UnitDefinition("rad", "phase", 1.0, ("radian", "radians")),
    UnitDefinition("deg", "phase", math.pi / 180.0, ("degree", "degrees")),
    UnitDefinition("N", "force", 1.0, ("newton", "newtons")),
    UnitDefinition("kN", "force", 1e3, ("kilonewton", "kilonewtons")),
    UnitDefinition("m", "displacement", 1.0, ("meter", "meters", "metre", "metres")),
    UnitDefinition("mm", "displacement", 1e-3, ("millimeter", "millimeters", "millimetre", "millimetres")),
    UnitDefinition("um", "displacement", 1e-6, ("micrometer", "micrometers", "micrometre", "micrometres")),
    UnitDefinition("in", "displacement", 0.0254, ("inch", "inches")),
    UnitDefinition("N*m", "moment", 1.0, ("n m", "newton meter", "newton meters", "newton metre", "newton metres")),
    UnitDefinition("kN*m", "moment", 1e3, ("kn m", "kilonewton meter", "kilonewton meters", "kilonewton metre", "kilonewton metres")),
    UnitDefinition("N*mm", "moment", 1e-3, ("n mm",)),
    UnitDefinition("kN*mm", "moment", 1.0, ("kn mm",)),
    UnitDefinition("m/s", "velocity", 1.0, ("m/sec",)),
    UnitDefinition("mm/s", "velocity", 1e-3, ("mm/sec",)),
    UnitDefinition("in/s", "velocity", 0.0254, ("in/sec",)),
    UnitDefinition("m/s^2", "acceleration", 1.0, ("m/s2", "m/sec^2", "m/sec2")),
    UnitDefinition("mm/s^2", "acceleration", 1e-3, ("mm/s2", "mm/sec^2", "mm/sec2")),
    UnitDefinition("in/s^2", "acceleration", 0.0254, ("in/s2", "in/sec^2", "in/sec2")),
    UnitDefinition("g", "acceleration", 9.80665, ()),
    UnitDefinition("rad", "angular displacement", 1.0, ("radian", "radians")),
    UnitDefinition("deg", "angular displacement", math.pi / 180.0, ("degree", "degrees")),
    UnitDefinition("rad/s", "angular velocity", 1.0, ("rad/sec",)),
    UnitDefinition("deg/s", "angular velocity", math.pi / 180.0, ("deg/sec", "degree/s", "degrees/s")),
    UnitDefinition("rpm", "angular velocity", (2.0 * math.pi) / 60.0, ("rev/min", "revolution/min", "revolutions/min")),
    UnitDefinition("rad/s^2", "angular acceleration", 1.0, ("rad/s2", "rad/sec^2", "rad/sec2")),
    UnitDefinition("deg/s^2", "angular acceleration", math.pi / 180.0, ("deg/s2", "deg/sec^2", "deg/sec2")),
)

_UNIT_DEFINITIONS_BY_FAMILY_AND_NAME: dict[tuple[QuantityFamily, str], UnitDefinition] = {
    (definition.quantity_family, definition.canonical_name): definition
    for definition in _UNIT_DEFINITIONS
}

_COMPATIBLE_UNITS_BY_FAMILY: dict[QuantityFamily, tuple[str, ...]] = {
    family: tuple(
        definition.canonical_name
        for definition in _UNIT_DEFINITIONS
        if definition.quantity_family == family
    )
    for family in QUANTITY_FAMILIES
    if family != "unknown"
}

_FAMILIES_BY_CANONICAL_UNIT: dict[str, tuple[QuantityFamily, ...]] = {}
for canonical_name in {definition.canonical_name for definition in _UNIT_DEFINITIONS}:
    _FAMILIES_BY_CANONICAL_UNIT[canonical_name] = tuple(
        definition.quantity_family
        for definition in _UNIT_DEFINITIONS
        if definition.canonical_name == canonical_name
    )

_DEFAULT_FAMILY_BY_CANONICAL_UNIT: dict[str, QuantityFamily] = {
    canonical_name: families[0]
    for canonical_name, families in _FAMILIES_BY_CANONICAL_UNIT.items()
}

_ALIAS_MAP: dict[str, str] = {}


def _cleanup_unit_text(unit: str) -> str:
    cleaned = unit.strip()
    cleaned = cleaned.replace("°", "deg")
    cleaned = cleaned.replace("µ", "u")
    cleaned = cleaned.replace("μ", "u")
    cleaned = cleaned.replace("²", "^2")
    cleaned = cleaned.replace("·", "*")
    cleaned = cleaned.replace("×", "*")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\s*([/*])\s*", r"\1", cleaned)
    return cleaned


def _alias_key(unit: str) -> str:
    key = _cleanup_unit_text(unit).lower()
    replacements = (
        (r"\bseconds?\b", "s"),
        (r"\bsecs?\b", "s"),
        (r"\bminutes?\b", "min"),
        (r"\bmins?\b", "min"),
        (r"\bhours?\b", "h"),
        (r"\bhrs?\b", "h"),
        (r"\bdegrees?\b", "deg"),
        (r"\bradians?\b", "rad"),
        (r"\bkilonewtons?\b", "kn"),
        (r"\bnewtons?\b", "n"),
        (r"\bmeters?\b", "m"),
        (r"\bmetres?\b", "m"),
        (r"\bmillimeters?\b", "mm"),
        (r"\bmillimetres?\b", "mm"),
        (r"\bmicrometers?\b", "um"),
        (r"\bmicrometres?\b", "um"),
        (r"\binches\b", "in"),
        (r"\binch\b", "in"),
        (r"\brevolutions?\b", "rev"),
    )
    for pattern, replacement in replacements:
        key = re.sub(pattern, replacement, key)
    key = key.replace("per", "/")
    key = re.sub(r"\s+", " ", key).strip()
    return key


for definition in _UNIT_DEFINITIONS:
    for candidate in (definition.canonical_name, *definition.aliases):
        _ALIAS_MAP[_alias_key(candidate)] = definition.canonical_name


def _validate_family_hint(quantity_family: QuantityFamily) -> None:
    if quantity_family not in QUANTITY_FAMILIES:
        raise ValueError(f"Unsupported quantity family: {quantity_family!r}")


def normalize_unit(unit: str | None) -> str | None:
    """Return the canonical unit name when known, otherwise a cleaned source string."""
    if unit is None:
        return None
    cleaned = _cleanup_unit_text(unit)
    if not cleaned:
        return None
    return _ALIAS_MAP.get(_alias_key(cleaned), cleaned)


def is_known_unit(unit: str | None) -> bool:
    normalized = normalize_unit(unit)
    return normalized in _FAMILIES_BY_CANONICAL_UNIT if normalized is not None else False


def infer_quantity_family(
    unit: str | None,
    family_hint: QuantityFamily | None = None,
) -> QuantityFamily:
    normalized = normalize_unit(unit)
    if normalized is None:
        return "unknown"

    families = _FAMILIES_BY_CANONICAL_UNIT.get(normalized)
    if not families:
        return "unknown"

    if family_hint is not None:
        _validate_family_hint(family_hint)
        if family_hint == "unknown":
            return "unknown"
        if family_hint not in families:
            raise IncompatibleUnitConversionError(
                f"Unit '{normalized}' is not compatible with quantity family '{family_hint}'."
            )
        return family_hint

    return _DEFAULT_FAMILY_BY_CANONICAL_UNIT[normalized]


def get_compatible_units(quantity_family: QuantityFamily) -> tuple[str, ...]:
    _validate_family_hint(quantity_family)
    if quantity_family == "unknown":
        return ()
    return _COMPATIBLE_UNITS_BY_FAMILY[quantity_family]


def get_unit_definition(
    unit: str | None,
    family_hint: QuantityFamily | None = None,
) -> UnitDefinition | None:
    normalized = normalize_unit(unit)
    if normalized is None:
        return None

    family = infer_quantity_family(normalized, family_hint=family_hint)
    if family == "unknown":
        return None

    return _UNIT_DEFINITIONS_BY_FAMILY_AND_NAME[(family, normalized)]
