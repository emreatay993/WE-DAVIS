# Controllers Module Reference

## PlotController (`app/controllers/plot_controller.py`)

`PlotController` translates tab/UI state into plot-ready data and Plotly
figures. It reads from `MainWindow` state, applies display-unit projection, calls
analysis helpers, then updates tab display methods.

### Key Labels

- `TIME_STEP_LABEL = "Time Step (dt)"`
- `FS_LABEL = "Sampling Rate (Hz)"`

### Main Slots

- `update_all_plots_from_settings()`
  - Applies Settings-tab style values to `Plotter`.
  - Applies display-unit preferences.
  - Refreshes currently relevant plots.
- `update_single_data_plots()`
  - Handles regular single-channel plots.
  - For `TIME`, supports sectioning/filtering plus computed time-step and
    sampling-rate selectors.
  - For single-folder `FREQ`, displays matching phase data when available.
  - Refreshes spectrum output when enabled.
- `update_spectrum_plot_only()`
  - Refreshes the spectrum view without rebuilding every tab.
- `update_interface_data_plots()`
  - Plots selected interface/side combinations as translational and rotational
    groups.
- `update_part_loads_plots()`
  - Plots selected part sides.
  - Applies `TIME` sectioning and Tukey options before building T/R groups.
- `update_time_domain_represent_plot()`
  - Reconstructs one-cycle time histories from selected `FREQ` magnitude and
    phase data.
  - Also listens to `PartLoadsTab.plot_parameters_changed` so reconstruction
    follows the selected part sides and exclusion rule.
  - Stores arrays in `TimeDomainRepresentTab.current_plot_data` for extraction
    and steady-state export dialogs.
- `update_compare_data_plots()`
  - Builds primary/comparison overlays plus absolute and relative differences.
  - Uses complex magnitude/phase arithmetic for `FREQ` where possible.
- `update_compare_part_loads_plots()`
  - Computes side-level T/R differences for selected part loads, with complex
    `FREQ` support where phase columns exist.

### Important Helpers

- `_get_plot_df(...)`: builds indexed plot frames for the active domain.
- `_filter_part_load_cols(...)`: filters selected side/component columns and
  excludes phase/unwanted component columns.
- `_calculate_differences(...)`: builds difference frames, including complex
  `FREQ` differences when phase data is present.

## ActionHandler (`app/controllers/action_handler.py`)

`ActionHandler` owns user workflows that span multiple subsystems or produce
side effects.

### Main Slots

- `handle_compare_data_selection()`
  - Calls `DataManager.load_comparison_data()` through `MainWindow`.
- `handle_time_domain_represent_export()`
  - Samples `TimeDomainRepresentTab.current_plot_data` across 0..360 degrees.
  - Converts values according to the Settings-tab export-unit mode.
  - Writes a labeled CSV.
- `handle_open_steady_state_cycle_estimator()`
  - Opens `SteadyStateCycleEstimatorDialog`.
  - Stores the latest conservative whole-cycle estimate on the time-domain
    representation tab.
- `handle_open_steady_state_time_history_export()`
  - Opens `SteadyStateTimeHistoryExportDialog` with the current one-cycle
    waveform, selected interval, selected frequency context, selected parts, and
    latest estimator snapshot.
- `handle_ansys_export()`
  - Opens the side/version selection dialog.
  - Applies Part Loads `TIME` section/Tukey options.
  - Builds unit-aware per-side CSVs and one combined CSV using Settings-tab
    export-unit mode.
  - Validates ANSYS quantity families and resolves `AnsysExportUnits`.
  - Calls `create_harmonic_template(..., export_units=...)` for `FREQ`.
  - Calls `create_transient_template(..., export_units=...)` for `TIME`.

### Unit and Export Notes

- The old fixed "multiply by 1000" export path has been replaced by unit-aware
  source/display export modes.
- Per-side CSVs are named with the export-mode slug, for example
  `extracted_data_for_<side>_in_source_units.csv`.
- The combined CSV is named
  `extracted_loads_of_all_selected_parts_in_<mode>.csv`.
- ANSYS export requires known domain, force, moment, and phase quantity families
  before template creation.
