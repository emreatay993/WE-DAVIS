Analysis Module Reference

app/analysis/data_processing.py

- apply_data_section(df, t_min_str, t_max_str) → DataFrame
  - TIME only: returns df[(TIME >= t_min) & (TIME <= t_max)] if inputs valid; otherwise original df

- apply_tukey_window(df, alpha) → DataFrame
  - TIME only: multiplies all data columns (excluding TIME/FREQ/NO/DataFolder) by scipy.signal.windows.tukey window

- apply_low_pass_filter(df, column, cutoff, order) → DataFrame
  - TIME only: computes fs from index spacing; applies Butterworth low-pass to the selected column; returns original df on error

- compute_time_step_series(df) → DataFrame
  - Requires TIME; sorts by TIME, computes Δt with robustness to zero/near-zero steps; index named "Time [s]"

- compute_sampling_rate_series(df) → DataFrame
  - 1 / Δt; aligns index with compute_time_step_series

- build_series_by_folder(df, selected_col, data_domain, section_enabled=False, t_min_text='', t_max_text='', filter_enabled=False, cutoff_text='', filter_order=2) → dict[str, DataFrame]
  - Groups by DataFolder (if present); prepares per-folder frames indexed by TIME or FREQ; optional sectioning and low-pass filter for TIME

- build_dt_by_folder(df, section_enabled=False, t_min_text='', t_max_text='') → dict[str, DataFrame]
  - Per-folder Δt series

- build_fs_by_folder(df, section_enabled=False, t_min_text='', t_max_text='') → dict[str, DataFrame]
  - Per-folder sampling rate series

- build_series_for_single(df, selected_col, data_domain, ... ) → DataFrame
  - Single-folder helper to build one column with proper index and optional filter

- build_multi_series_for_single(df, columns, data_domain, section_enabled=False, t_min_text='', t_max_text='', tukey_enabled=False, tukey_alpha=0.1) → DataFrame
  - Multi-column single-folder builder with optional sectioning and Tukey (TIME)

app/analysis/steady_state_estimator.py

- estimate_cycles_to_steady_state(damping_ratio, excitation_frequency_hz, mode_frequency_hz=None, residual_fraction=0.01) → SteadyStateEstimate
  - Estimates startup-transient decay using the damped modal envelope q_tr(t) ~ exp(-zeta * omega_n * t)
  - General estimate: t_required = ln(1 / r) / (zeta * omega_n), then N_cycles = f_exc * t_required
  - Exact-resonance shorthand: N = ln(1 / r) / (2*pi*zeta)
  - Example: zeta = 0.02 and r = 0.01 gives N = 36.65, rounded up to 37 whole cycles
  - The estimate remains conservative; soft-start smoothing can help load introduction and convergence but is not a guaranteed cycle-count reducer

- build_estimate_table(...) → list[SteadyStateEstimate]
  - Builds common residual-fraction rows for the estimator dialog

app/analysis/steady_state_time_history_export.py

- build_seconds_time_history_frame(one_cycle_plot_data, interval_degrees, cycles, frequency_hz) → DataFrame
  - Repeats the selected steady-state one-cycle waveform into a seconds-based transient load history with an inclusive endpoint

- apply_half_cosine_soft_start(frame, ramp_cycles, frequency_hz, time_column="Time") → DataFrame
  - Applies m(t) = 0.5 * (1 - cos(pi * t / T_ramp)) for 0 <= t < T_ramp, then 1.0
  - Multiplies load/data columns only and never the time column
  - Runs before unit conversion and CSV header generation in the export dialog
  - Prevents a steady-state waveform from being introduced as an artificial initial load step when the downstream transient model starts from zero state
  - Uses a one-sided half-cosine ramp instead of the existing full Tukey window because this export needs to end at full steady-state amplitude; the Tukey window remains the two-sided taper for extracted TIME sections and signal-processing boundary control

- convert_time_history_frame_for_export(...) → DataFrame
  - Converts non-time columns to the selected export units where unit context is known

- build_time_history_csv_headers(...) → list[str]
  - Adds selected unit labels to CSV headers without adding metadata rows

References used by this implementation: ANSYS Help: Harmonic Response; ANSYS Help: Mode-Superposition Transient Dynamic Analysis; SciPy Documentation: scipy.signal.windows.tukey.

app/analysis/ansys_exporter.py

- AnsysExporter
  - _init_ansys_session()/_close_ansys_session(): lifecycle of ansys.mechanical.core App and globals (Model, ExtAPI, DataModel, Quantity, Ansys)

  - create_harmonic_template(df_export, data_domain)
    - Expects FREQ; builds per-interface loads: forces (T1–T3) and moments (R1–R3) with phase columns (Phase_T1…)
    - Creates APDL tables for real/imag components via _create_APDL_table
    - Adds RemoteForce and (optionally) Moment to Harmonic analysis; cleans temp files; saves WE_Loading_Template_Harmonic.mechdat

  - create_transient_template(df_export, data_domain, sample_rate)
    - Expects TIME; builds per-interface force/moment tables over TIME
    - Partitions large inputs into segments of ~50k rows; assigns to Transient analysis loads
    - Python post hook to clean working directory; saves WE_Loading_Template_Transient.mechdat

  - _create_APDL_table(result_df, table_name, data_domain) → list[str]
    - Generates *DIM and *SET commands for APDL tables

  - _partition_dataframe_for_load_input(df, partition_size) → list[DataFrame]
    - Partitions with inserted zero rows and previous last-row zero to ensure continuity

Notes and Units

- Scaling: exporter uses kN and kN·m by assembling Quantity objects; data is multiplied by 1000 where needed before writing CSVs by ActionHandler
- Domain: harmonic template only for FREQ (requires Phase_); transient only for TIME; the ActionHandler selects which to call










