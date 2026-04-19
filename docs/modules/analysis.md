Analysis Module Reference

app/analysis/data_processing.py

- `apply_data_section(df, t_min_str, t_max_str) -> DataFrame`
  - TIME only: returns `df[(TIME >= t_min) & (TIME <= t_max)]` if inputs are valid; otherwise returns the original frame.

- `apply_tukey_window(df, alpha) -> DataFrame`
  - TIME only: multiplies all data columns except `TIME`, `FREQ`, `NO`, and `DataFolder` by `scipy.signal.windows.tukey`.

- `apply_low_pass_filter(df, column, cutoff, order) -> DataFrame`
  - TIME only: computes sampling frequency from index spacing, applies a Butterworth low-pass filter to the selected column, and returns the original frame on error.

- `compute_time_step_series(df) -> DataFrame`
  - Requires `TIME`; sorts by `TIME`, computes robust delta-time values, and names the index `Time [s]`.

- `compute_sampling_rate_series(df) -> DataFrame`
  - Returns `1 / delta_t` aligned to `compute_time_step_series`.

- `build_series_by_folder(df, selected_col, data_domain, section_enabled=False, t_min_text='', t_max_text='', filter_enabled=False, cutoff_text='', filter_order=2) -> dict[str, DataFrame]`
  - Groups by `DataFolder` when present, prepares per-folder frames indexed by `TIME` or `FREQ`, and optionally applies sectioning or low-pass filtering for TIME data.

- `build_dt_by_folder(df, section_enabled=False, t_min_text='', t_max_text='') -> dict[str, DataFrame]`
  - Builds per-folder delta-time series.

- `build_fs_by_folder(df, section_enabled=False, t_min_text='', t_max_text='') -> dict[str, DataFrame]`
  - Builds per-folder sampling-rate series.

- `build_series_for_single(df, selected_col, data_domain, ...) -> DataFrame`
  - Single-folder helper to build one selected column with the correct index and optional filtering.

- `build_multi_series_for_single(df, columns, data_domain, section_enabled=False, t_min_text='', t_max_text='', tukey_enabled=False, tukey_alpha=0.1) -> DataFrame`
  - Multi-column single-folder helper with optional sectioning and Tukey windowing for TIME data.

app/analysis/ansys_exporter.py

- `AnsysExporter`
  - `_init_ansys_session()` and `_close_ansys_session()`: lifecycle of the `ansys.mechanical.core` app and global handles (`Model`, `ExtAPI`, `DataModel`, `Quantity`, `Ansys`).

  - `create_harmonic_template(df_export, data_domain, export_units=None)`
    - Expects `FREQ`.
    - Builds per-interface loads for `T1-T3` and `R1-R3` plus their `Phase_` columns.
    - Creates APDL tables for real and imaginary components through `_create_APDL_table`.
    - Adds `RemoteForce` and optional moment loads to the Harmonic analysis, then saves `WE_Loading_Template_Harmonic.mechdat`.

  - `create_transient_template(df_export, data_domain, export_units=None, sample_rate=None)`
    - Expects `TIME`.
    - Builds per-interface transient load tables over `TIME`.
    - Partitions large inputs into segments of about 50k rows and assigns them to Transient analysis loads.
    - Runs a Python post hook to clean the working directory, then saves `WE_Loading_Template_Transient.mechdat`.

  - `_create_APDL_table(result_df, table_name, data_domain) -> list[str]`
    - Generates `*DIM` and `*SET` commands for APDL tables.

  - `_partition_dataframe_for_load_input(df, partition_size) -> list[DataFrame]`
    - Partitions frames with inserted zero rows and a zeroed copy of the previous last row to preserve continuity.

Notes and Units

- Unit metadata enters the analysis and export stack from `max.pld`. `DataManager` parses channel `UNIT` values plus domain or phase headers such as `FREQ(Hz)`, `TIME(s)`, and `PHASE(deg)` into column unit contexts before the plotting and export layers run.
- Display-unit projection is a UI concern. `MainWindow` keeps the raw detected unit context, `SettingsTab` exposes one display-unit selector per detected quantity family, and `PlotController` projects plotted data on demand from the preserved raw frames.
- Export behavior is explicit. `ActionHandler` builds either a source-unit export frame or a display-unit export frame based on the `SettingsTab` `Export Units` selector, and it converts time-domain reconstruction output back to source units when the user chooses `Source Units`.
- ANSYS export validation still requires the selected export frame to resolve cleanly to the expected domain, force, moment, and phase families. Unknown or unsupported units remain native-only and are rejected instead of being guessed.
- Domain support is unchanged: harmonic template export is FREQ-only and requires `Phase_` columns; transient template export is TIME-only. The unit-aware closeout still covers `.pld` datasets only, and `.log` input support remains deferred for later work.
