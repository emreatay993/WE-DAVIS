from __future__ import annotations

import math
from typing import Mapping

import pandas as pd

from ..units import ColumnUnitContext, convert_scalar, convert_series


def resolve_frequency_to_hz(
    selected_frequency_value: float,
    frequency_context: ColumnUnitContext | None,
) -> float:
    if selected_frequency_value <= 0.0:
        raise ValueError("Selected frequency must be positive.")
    if (
        frequency_context is None
        or frequency_context.normalized_unit is None
        or frequency_context.quantity_family != "frequency"
    ):
        return float(selected_frequency_value)

    source_unit = frequency_context.normalized_unit
    if source_unit == "Hz":
        return float(selected_frequency_value)

    return float(
        convert_scalar(
            selected_frequency_value,
            source_unit=source_unit,
            target_unit="Hz",
            family_hint="frequency",
        )
    )


def build_seconds_time_history_frame(
    one_cycle_plot_data: Mapping[str, Mapping[str, object]],
    interval_degrees: int,
    cycles: int,
    frequency_hz: float,
) -> pd.DataFrame:
    if not one_cycle_plot_data:
        raise ValueError("No one-cycle plot data is available.")
    if interval_degrees <= 0 or 360 % interval_degrees != 0:
        raise ValueError("Interval must be a positive divisor of 360 degrees.")
    if cycles <= 0:
        raise ValueError("Cycles must be a positive whole number.")
    if frequency_hz <= 0.0:
        raise ValueError("Frequency in Hz must be positive.")

    samples_per_cycle = 360 // interval_degrees
    total_samples = cycles * samples_per_cycle + 1
    time_step_s = (interval_degrees / 360.0) / frequency_hz

    export_columns = {
        "Time": [sample_index * time_step_s for sample_index in range(total_samples)]
    }

    for trace_name, plot_data in one_cycle_plot_data.items():
        y_data = plot_data.get("y_data")
        if y_data is None:
            raise ValueError(f"Trace '{trace_name}' is missing waveform data.")
        if len(y_data) < 360:
            raise ValueError(
                f"Trace '{trace_name}' does not contain the expected one-cycle waveform samples."
            )

        export_columns[trace_name] = [
            y_data[(sample_index * interval_degrees) % 360]
            for sample_index in range(total_samples)
        ]

    return pd.DataFrame(export_columns)


def apply_half_cosine_soft_start(
    frame: pd.DataFrame,
    ramp_cycles: float,
    frequency_hz: float,
    time_column: str = "Time",
) -> pd.DataFrame:
    if ramp_cycles < 0.0:
        raise ValueError("Ramp cycles must be non-negative.")
    if frequency_hz <= 0.0:
        raise ValueError("Frequency in Hz must be positive.")

    smoothed = frame.copy(deep=True)
    if ramp_cycles == 0.0:
        return smoothed

    if time_column not in smoothed.columns:
        raise ValueError(f"Time column '{time_column}' is missing.")
    if smoothed.empty:
        raise ValueError("Cannot apply soft start to an empty time-history frame.")

    final_time_s = float(smoothed[time_column].iloc[-1])
    total_exported_cycles = final_time_s * frequency_hz
    if ramp_cycles - total_exported_cycles > 1.0e-12:
        raise ValueError(
            "Ramp cycles must not exceed total exported cycles "
            f"({ramp_cycles:g} > {total_exported_cycles:g})."
        )

    ramp_duration_s = ramp_cycles / frequency_hz
    multipliers = smoothed[time_column].map(
        lambda time_s: (
            0.5 * (1.0 - math.cos(math.pi * float(time_s) / ramp_duration_s))
            if float(time_s) < ramp_duration_s
            else 1.0
        )
    )

    for column_name in smoothed.columns:
        if column_name == time_column:
            continue
        smoothed[column_name] = smoothed[column_name] * multipliers

    return smoothed


def convert_time_history_frame_for_export(
    frame: pd.DataFrame,
    trace_contexts: Mapping[str, ColumnUnitContext | None],
    family_units: Mapping[str, str],
) -> pd.DataFrame:
    converted = frame.copy(deep=True)

    for column_name in converted.columns:
        if column_name == "Time":
            continue

        context = trace_contexts.get(column_name)
        if (
            context is None
            or context.quantity_family == "unknown"
            or context.native_only
        ):
            continue

        current_unit = context.display_unit or context.normalized_unit
        target_unit = family_units.get(context.quantity_family, current_unit)
        if (
            current_unit is None
            or target_unit is None
            or current_unit == target_unit
        ):
            continue

        converted[column_name] = convert_series(
            converted[column_name],
            source_unit=current_unit,
            target_unit=target_unit,
            family_hint=context.quantity_family,
        )

    return converted


def build_time_history_csv_headers(
    frame_columns: list[str] | tuple[str, ...],
    trace_contexts: Mapping[str, ColumnUnitContext | None],
    family_units: Mapping[str, str],
    manual_unknown_labels: Mapping[str, str] | None = None,
) -> list[str]:
    manual_unknown_labels = manual_unknown_labels or {}
    headers: list[str] = []

    for column_name in frame_columns:
        if column_name == "Time":
            headers.append("Time [s]")
            continue

        context = trace_contexts.get(column_name)
        if (
            context is not None
            and context.quantity_family != "unknown"
            and not context.native_only
        ):
            selected_unit = family_units.get(
                context.quantity_family,
                context.display_unit or context.normalized_unit,
            )
            headers.append(
                f"{column_name} [{selected_unit}]" if selected_unit else column_name
            )
            continue

        manual_label = str(manual_unknown_labels.get(column_name, "")).strip()
        headers.append(
            f"{column_name} [{manual_label}]" if manual_label else column_name
        )

    return headers
