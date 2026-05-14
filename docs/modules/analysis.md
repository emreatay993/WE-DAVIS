# Analysis Module Reference

## `app/analysis/data_processing.py`

- `apply_data_section(df, t_min_str, t_max_str) -> DataFrame`
  - For `TIME`, returns rows between min and max time when inputs are valid.
- `apply_tukey_window(df, alpha) -> DataFrame`
  - For `TIME`, applies a Tukey window to data columns while preserving domain,
    `NO`, and `DataFolder` columns.
- `apply_low_pass_filter(df, column, cutoff, order) -> DataFrame`
  - For `TIME`, estimates sampling frequency from index spacing and applies a
    Butterworth low-pass filter.
- `compute_time_step_series(df) -> DataFrame`
  - Computes robust time-step values from sorted `TIME` data.
- `compute_sampling_rate_series(df) -> DataFrame`
  - Computes sampling rate from time-step values.
- `build_series_by_folder(...) -> dict[str, DataFrame]`
  - Builds one plot frame per `DataFolder`, with optional `TIME` sectioning and
    filtering.
- `build_dt_by_folder(...)` and `build_fs_by_folder(...)`
  - Build per-folder computed `Time Step (dt)` and `Sampling Rate (Hz)` frames.
- `build_series_for_single(...) -> DataFrame`
  - Builds one indexed frame for a single selected column.
- `build_multi_series_for_single(...) -> DataFrame`
  - Builds a multi-column single-folder frame with optional `TIME` sectioning and
    Tukey windowing.

## `app/analysis/steady_state_estimator.py`

- `estimate_cycles_to_steady_state(...) -> SteadyStateEstimate`
  - Estimates startup-transient decay from damping ratio, excitation frequency,
    optional dominant mode frequency, and residual fraction.
  - The exact-resonance shorthand is `N = ln(1 / r) / (2 * pi * zeta)`.
- `build_estimate_table(...) -> list[SteadyStateEstimate]`
  - Builds common residual-fraction rows for the estimator dialog.

The estimator is advisory. Soft-start smoothing improves load introduction but
does not prove that fewer physical cycles are needed.

## `app/analysis/steady_state_time_history_export.py`

- `build_seconds_time_history_frame(...) -> DataFrame`
  - Repeats a selected one-cycle waveform into a seconds-based transient load
    history.
- `apply_half_cosine_soft_start(...) -> DataFrame`
  - Applies a one-sided half-cosine ramp to load/data columns only.
  - Runs before unit conversion and CSV header generation.
- `convert_time_history_frame_for_export(...) -> DataFrame`
  - Converts export columns to selected dialog units where unit context is
    available.
- `build_time_history_csv_headers(...) -> list[str]`
  - Adds selected unit labels to CSV headers without extra metadata rows.

## `app/analysis/ansys_exporter.py`

`AnsysExporter` encapsulates ANSYS Mechanical automation. It can be created with
an explicit ANSYS version/base path or use its default session discovery path.

### Unit Model

- `AnsysExportUnits` carries `domain_unit`, `force_unit`, `moment_unit`, and
  `phase_unit`.
- `_coerce_export_units(...)` accepts `None`, an `AnsysExportUnits` instance, or
  a dict-like value and supplies domain defaults (`Hz` for `FREQ`, `s` for
  `TIME`).
- Quantity strings are normalized for ANSYS Mechanical through internal
  `_to_quantity_unit(...)` handling.

### Harmonic Export

- `create_harmonic_template(df_export, data_domain, export_units=None)`
  - Requires `FREQ`.
  - Uses magnitude columns plus matching `Phase_...` columns.
  - Builds real/imaginary APDL tables for force and moment components.
  - Saves `WE_Loading_Template_Harmonic.mechdat`.

### Transient Export

- `create_transient_template(df_export, data_domain, export_units=None)`
  - Requires `TIME`.
  - Uses the selected time/domain unit from `export_units`.
  - Partitions large load tables for Mechanical load input.
  - Saves `WE_Loading_Template_Transient.mechdat`.

### APDL and Partition Helpers

- `_create_APDL_table(...) -> list[str]`
  - Generates APDL table commands.
- `_partition_dataframe_for_load_input(...) -> list[DataFrame]`
  - Splits large transient tables and inserts continuity rows where needed.

## Unit-Aware Export Behavior

`ActionHandler` now prepares export frames and validates unit families before
calling `AnsysExporter`. The old documentation that described fixed kN/kN-m
scaling or explicit `sample_rate` arguments is stale; current calls pass
`export_units` and let the exporter use the resolved domain unit.
