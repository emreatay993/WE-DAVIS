from __future__ import annotations


class UnitError(ValueError):
    """Base error for unit catalog and conversion failures."""


class UnknownUnitError(UnitError):
    """Raised when a unit string cannot be resolved by the catalog."""


class IncompatibleUnitConversionError(UnitError):
    """Raised when conversion is requested across incompatible units."""
