# Signal / Slot Reference

`MainWindow._connect_signals()` is the application wiring hub. Tabs expose
signals and display methods; `PlotController` and `ActionHandler` provide most
slots.

Signatures below are simplified but reflect the current payloads.

## Data Loading Signals

| Emitter | Signal | Receiver slot | Purpose |
| --- | --- | --- | --- |
| `DataManager` | `dataLoaded(pd.DataFrame, str, str, object)` | `MainWindow.on_data_loaded` | Delivers combined data, detected domain, first valid folder, and unit context map. |
| `DataManager` | `dataLoadFailed(str)` | `MainWindow.on_data_load_failed` | Restores window title after a failed load. |
| `DataManager` | `comparisonDataLoaded(pd.DataFrame, object)` | `MainWindow.on_comparison_data_loaded` | Delivers secondary comparison data and its unit context map. |
| `DataManager` | `loadingProgress(int, int, str)` | `MainWindow.on_loading_progress` | Updates the title while multiple folders load. |
| `DirectoryTreeDock` | `directories_selected(list[str])` | `MainWindow._on_directories_selected` | Requests loading of selected dock folders after a primary dataset exists. |
| `MainWindow.open_action` | `triggered()` | `DataManager.load_data_from_directory` | Opens a folder picker for a replacement primary dataset. |

## Plot Update Signals

| Emitter | Signal | Receiver slot | Purpose |
| --- | --- | --- | --- |
| `SingleDataTab` | `plot_parameters_changed` | `PlotController.update_single_data_plots` | Rebuilds regular and phase plots after selector/filter/section changes. |
| `SingleDataTab` | `spectrum_parameters_changed` | `PlotController.update_spectrum_plot_only` | Refreshes the spectrum subplot only. |
| `InterfaceDataTab` | `plot_parameters_changed` | `PlotController.update_interface_data_plots` | Updates interface translational and rotational plots. |
| `PartLoadsTab` | `plot_parameters_changed` | `PlotController.update_part_loads_plots` | Updates part-load translational and rotational plots. |
| `PartLoadsTab` | `plot_parameters_changed` | `PlotController.update_time_domain_represent_plot` | Keeps frequency-to-time reconstruction aligned with selected part sides/exclusions. |
| `TimeDomainRepresentTab` | `plot_parameters_changed` | `PlotController.update_time_domain_represent_plot` | Reconstructs one-cycle time histories at the selected frequency. |
| `CompareDataTab` | `plot_parameters_changed` | `PlotController.update_compare_data_plots` | Updates comparison overlay, absolute difference, and relative difference plots. |
| `ComparePartLoadsTab` | `plot_parameters_changed` | `PlotController.update_compare_part_loads_plots` | Updates part-load difference plots. |
| `SettingsTab` | `settings_changed` | `PlotController.update_all_plots_from_settings` | Applies plot style, rolling envelope, display-unit, and export-mode changes. |
| `MainWindow.tab_widget` | `currentChanged(int)` | `MainWindow._on_tab_changed` | Refreshes the newly active tab. |

## Action Signals

| Emitter | Signal | Receiver slot | Purpose |
| --- | --- | --- | --- |
| `MainWindow.export_full_csv_action` | `triggered()` | `MainWindow._export_full_data_csv` | Writes the current combined `df` to a user-selected CSV path. |
| `CompareDataTab` | `select_compare_data_requested` | `ActionHandler.handle_compare_data_selection` | Opens comparison-folder selection through `DataManager.load_comparison_data()`. |
| `PartLoadsTab` | `export_to_ansys_requested` | `ActionHandler.handle_ansys_export` | Exports selected part loads as unit-aware CSV and creates an ANSYS template. |
| `TimeDomainRepresentTab` | `extract_data_requested` | `ActionHandler.handle_time_domain_represent_export` | Exports sampled reconstructed one-cycle data to CSV. |
| `TimeDomainRepresentTab` | `steady_state_time_history_export_requested` | `ActionHandler.handle_open_steady_state_time_history_export` | Opens repeated-cycle steady-state time-history export dialog. |
| `TimeDomainRepresentTab` | `steady_state_estimator_requested` | `ActionHandler.handle_open_steady_state_cycle_estimator` | Opens the damping-based steady-state cycle estimator dialog. |

## Reusable Widget Signals

| Emitter | Signal | Notes |
| --- | --- | --- |
| `CheckableComboBox` | `selectionChanged()` | Emitted after a 100 ms debounce and only when the checked set actually changes. Used by interface and part-load selectors. |

## Ownership Notes

- `MainWindow` owns wiring, top-level state, tab enablement, selector
  population, and unit preference application.
- `DataManager` owns data ingestion and unit-context creation, not plot logic.
- `PlotController` owns plot refresh slots and display-unit projection.
- `ActionHandler` owns cross-tab actions and export dialogs.
- `Plotter`, `config_manager`, `app/units`, and most `app/analysis` modules are
  service/helper layers rather than application-level signal owners.
