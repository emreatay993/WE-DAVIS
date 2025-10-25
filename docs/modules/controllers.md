Controllers Module Reference

PlotController (app/controllers/plot_controller.py)

Purpose

- Central mediator translating tab UI state into plot-ready DataFrames and Plotly figures via Plotter.

Key Constants

- TIME_STEP_LABEL = 'Time Step (Δt)'
- FS_LABEL = 'Sampling Rate (Hz)'

Important Methods

- update_all_plots_from_settings()
  - Applies SettingsTab values to Plotter (legend/default/hover fonts, hover mode, trace opacity)
  - Refreshes all plots across tabs

- update_single_data_plots()
  - Builds dfs_for_plot via data_processing builders:
    - TIME + Δt → build_dt_by_folder
    - TIME + Fs → build_fs_by_folder
    - Otherwise → build_series_by_folder with optional sectioning/filter
  - Displays phase plot in FREQ when a matching Phase_ column exists and data is single-folder
  - In TIME and when spectrum is enabled (single-folder), calls update_spectrum_plot_only

- update_interface_data_plots()
  - Finds columns by interface prefix and side; groups Translational (T1/T2/T3/T2/T3) and Rotational (R1/R2/R3/R2/R3)
  - Uses build_multi_series_for_single without sectioning

- update_part_loads_plots()
  - Applies optional sectioning and Tukey (TIME) to a working copy, then builds T* and R* groups using _filter_part_load_cols

- update_time_domain_represent_plot()
  - FREQ only; reconstructs time-domain cosinusoidal data at a selected frequency for a selected side
  - Stores raw arrays in tab.current_plot_data for extraction

- update_compare_data_plots()
  - Overlays selected column for primary vs comparison; computes Δ and % differences; uses complex math for FREQ when Phase_ exists

- update_compare_part_loads_plots()
  - Computes Δ for all T*/R* columns of a side; uses complex differences in FREQ when possible

Helpers

- _get_plot_df(cols, source_df=None): sets index to domain with proper labels
- _filter_part_load_cols(all_columns, side, required_components, exclude): filters by side and component; excludes Phase_ and optionally T2/T3/R2/R3 (preserves resultants)
- _calculate_differences(columns): returns DataFrame of absolute differences; complex-aware for FREQ

ActionHandler (app/controllers/action_handler.py)

Purpose

- Orchestrates actions initiated by the user that span multiple subsystems: comparison selection, time-domain CSV extraction, and ANSYS export.

Key Methods

- handle_compare_data_selection()
  - Triggers DataManager.load_comparison_data via main_window.data_manager

- handle_time_domain_represent_export()
  - Validates interval selection and presence of tab.current_plot_data
  - Samples y(θ) at specified interval across 0..360; writes CSV

- handle_ansys_export()
  - Validates presence of df and collects selected sides via a dialog
  - Builds per-side subsets; writes two CSVs per side: original units and multiplied by 1000
  - Concatenates converted per-side subsets (drops duplicate domain col) into extracted_loads_of_all_selected_parts_in_converted_units.csv
  - For FREQ: AnsysExporter.create_harmonic_template(df_processed, 'FREQ')
  - For TIME: calculates sample_rate from df['TIME'] diffs and calls create_transient_template

Dialogs and UX

- _get_sides_for_export(): modal dialog with multi-select list seeded from current side; returns list[str] or None

Notes

- Units: CSV multiplication by 1000 aligns with ANSYS Quantity usage (kN/kN·m)
- TIME preprocessing (section/Tukey) applies before export when enabled










