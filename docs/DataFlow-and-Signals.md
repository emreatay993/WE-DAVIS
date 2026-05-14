# Data Flow and Qt Signals

## Primary Data Load

1. `main.py` starts Qt, creates `DataManager` and `MainWindow`, then schedules
   the initial folder prompt.
2. The user selects one or more data folders through the startup dialog, File
   menu, or directory dock.
3. `DataManager.load_data_from_paths(...)`:
   - finds files with case-insensitive `full.pld` and `max.pld` suffixes;
   - loads one or more full data files and a header file;
   - detects the domain from `FREQ` or `TIME`;
   - builds header labels, phase labels, and source-unit metadata;
   - rejects folders whose domain differs from the first valid folder;
   - adds `DataFolder` and concatenates valid frames;
   - emits `loadingProgress(...)` during multi-folder loads;
   - emits `dataLoaded(final_df, data_domain, first_valid_folder, unit_context)`.
4. `MainWindow.on_data_loaded(...)`:
   - stores raw and display DataFrames/contexts;
   - derives default display units by quantity family;
   - updates Settings-tab display/export unit controls;
   - populates selectors for every tab;
   - enables single-folder-only tabs when exactly one folder is loaded;
   - shows the Time Domain Representation tab only for `FREQ`;
   - enables rolling min/max envelope only for `TIME`;
   - calls `PlotController.update_all_plots_from_settings()`.

## Plot Update Path

1. A tab emits `plot_parameters_changed`, `spectrum_parameters_changed`, or
   `settings_changed`.
2. `PlotController` snapshots current tab state from `MainWindow`, converts data
   to display units where appropriate, and calls `analysis.data_processing`
   helpers.
3. `Plotter` creates the Plotly figure.
4. The target tab receives the figure through a `display_*` method and loads it
   into a `QWebEngineView`.

`PartLoadsTab.plot_parameters_changed` also refreshes
`TimeDomainRepresentTab`, because the frequency-to-time reconstruction uses the
current part-side selection and exclusion setting.

## Comparison Flow

1. `CompareDataTab.select_compare_data_requested` reaches
   `ActionHandler.handle_compare_data_selection()`.
2. `ActionHandler` calls `DataManager.load_comparison_data()`.
3. `DataManager` applies the same PLD and unit-context loading rules and emits
   `comparisonDataLoaded(df_compare, unit_context_compare)`.
4. `MainWindow.on_comparison_data_loaded(...)` validates domain alignment,
   stores raw/display comparison state, updates common-column selectors, and
   asks `PlotController` to refresh comparison plots.
5. `PlotController` computes overlay, absolute difference, and relative
   difference plots. For `FREQ`, it uses complex magnitude/phase arithmetic when
   matching `Phase_...` columns are available.

## Export and Dialog Flow

- Full CSV: `MainWindow._export_full_data_csv()` writes the current combined
  `df` directly to the selected path.
- Time Domain Representation extraction:
  `ActionHandler.handle_time_domain_represent_export()` samples
  `tab.current_plot_data`, converts values according to Settings-tab export
  mode, and writes CSV.
- Steady-state time-history export:
  `ActionHandler.handle_open_steady_state_time_history_export()` opens
  `SteadyStateTimeHistoryExportDialog`, which repeats the selected one-cycle
  waveform, optionally applies soft start, applies dialog-specific export-unit
  selections, and writes CSV.
- Steady-state cycle estimator:
  `ActionHandler.handle_open_steady_state_cycle_estimator()` opens
  `SteadyStateCycleEstimatorDialog` and stores the latest conservative
  whole-cycle estimate for the export dialog.
- ANSYS export:
  `ActionHandler.handle_ansys_export()` builds selected side frames, applies
  `TIME` section/Tukey options, converts/labels CSV output according to the
  Settings-tab export-unit mode, validates ANSYS quantity families, and calls
  `AnsysExporter.create_harmonic_template(..., export_units=...)` for `FREQ` or
  `create_transient_template(..., export_units=...)` for `TIME`.

## Signal Overview

### DataManager

- `dataLoaded(pd.DataFrame, str, str, object)`
- `dataLoadFailed(str)`
- `comparisonDataLoaded(pd.DataFrame, object)`
- `loadingProgress(int, int, str)`

### Directory Dock and Menu

- `DirectoryTreeDock.directories_selected(list[str]) ->
  MainWindow._on_directories_selected -> DataManager.load_data_from_paths`
- `MainWindow.open_action.triggered -> DataManager.load_data_from_directory`
- `MainWindow.export_full_csv_action.triggered -> MainWindow._export_full_data_csv`

### Tabs to PlotController

- `SingleDataTab.plot_parameters_changed -> update_single_data_plots`
- `SingleDataTab.spectrum_parameters_changed -> update_spectrum_plot_only`
- `InterfaceDataTab.plot_parameters_changed -> update_interface_data_plots`
- `PartLoadsTab.plot_parameters_changed -> update_part_loads_plots`
- `PartLoadsTab.plot_parameters_changed -> update_time_domain_represent_plot`
- `TimeDomainRepresentTab.plot_parameters_changed -> update_time_domain_represent_plot`
- `CompareDataTab.plot_parameters_changed -> update_compare_data_plots`
- `ComparePartLoadsTab.plot_parameters_changed -> update_compare_part_loads_plots`
- `SettingsTab.settings_changed -> update_all_plots_from_settings`

### Tabs to ActionHandler

- `CompareDataTab.select_compare_data_requested -> handle_compare_data_selection`
- `PartLoadsTab.export_to_ansys_requested -> handle_ansys_export`
- `TimeDomainRepresentTab.extract_data_requested -> handle_time_domain_represent_export`
- `TimeDomainRepresentTab.steady_state_time_history_export_requested ->
  handle_open_steady_state_time_history_export`
- `TimeDomainRepresentTab.steady_state_estimator_requested ->
  handle_open_steady_state_cycle_estimator`

## Guards and Error Handling

- Missing PLD files, invalid folders, and mixed domains are skipped or reported.
- `dataLoadFailed` fires when no valid data can be loaded.
- Comparison data requires a primary dataset and matching domain.
- Unknown/native-only units are shown but cannot be converted unless a compatible
  family is known.
- ANSYS export validates that domain, force, moment, and phase columns resolve to
  supported unit families before template creation.
