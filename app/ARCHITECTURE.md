# Architecture Overview

WE-DAVIS is a Windows-focused PyQt5 desktop application for loading WE Davis
`.pld` mechanical load exports, inspecting them with Plotly charts, comparing
datasets, and preparing load histories for FEA/ANSYS workflows.

## Runtime Shape

| Layer | Primary files | Responsibility |
| --- | --- | --- |
| Entry point | `main.py` | Creates the `QApplication`, constructs `DataManager` and `MainWindow`, shows the window, and opens the first data-folder prompt on the Qt event loop. |
| Shell and state | `app/main_window.py` | Owns the loaded DataFrames, raw/display unit contexts, tab widgets, dock, menus, and all cross-component signal wiring. |
| Data loading | `app/data_manager.py` | Loads one or more PLD folders, matches `*full.pld` data files with a `*max.pld` header, detects `TIME` or `FREQ`, builds unit metadata, and emits Qt data signals. |
| UI widgets | `app/ui/*`, `app/ui/widgets/*` | Define tab controls, dialogs, the directory dock, and reusable widgets such as `CheckableComboBox`. |
| Controllers | `app/controllers/plot_controller.py`, `app/controllers/action_handler.py` | Implement slots for plot refreshes, comparison loading, CSV extraction, steady-state dialogs, and ANSYS export. |
| Analysis services | `app/analysis/*` | Provide data processing, ANSYS template generation, steady-state cycle estimates, and steady-state time-history export helpers. |
| Units | `app/units/*` | Normalize source units, infer quantity families, manage display-unit context, and convert values for plotting/export. |
| Rendering | `app/plotting/plotter.py` | Builds Plotly figures and loads generated HTML into `QWebEngineView` widgets. |

## Startup and Loading Flow

1. `main.py` creates the Qt application, a `DataManager`, and a `MainWindow`.
2. `MainWindow` creates all tabs, controllers, the plotter, menu actions, and dock widget, then connects signals in `_connect_signals()`.
3. A `QTimer.singleShot(...)` startup callback calls `DataManager.load_data_from_directory()`.
4. `DataManager.load_data_from_paths(...)` validates each selected folder, loads case-insensitive `*full.pld` and `*max.pld` files, rejects mixed `TIME`/`FREQ` domains, merges valid folders, aligns unit contexts to columns, and emits `dataLoaded(final_df, domain, first_folder, unit_context)`.
5. `MainWindow.on_data_loaded(...)` stores raw/display state, derives display units, refreshes unit controls, populates tab selectors, adjusts tab availability, and asks `PlotController` to refresh all plots.

## Unit Model

Source unit metadata is created while loading PLD headers. `DataManager` stores
that metadata as `ColumnUnitContext` objects from `app/units/context.py`.
`MainWindow` keeps both raw and active display contexts:

- `raw_primary_df` / `raw_comparison_df`: source values as loaded.
- `df` / `df_compare`: currently displayed values.
- `raw_unit_context` / `raw_comparison_unit_context`: detected source metadata.
- `unit_context` / `comparison_unit_context`: source metadata plus active display-unit choices.
- `active_display_units_by_family`: one selected display unit per quantity family.
- `export_unit_mode`: Settings-tab choice between source units and display units for extracted/ANSYS CSV exports.

Plots are rendered in display units. Time-domain extraction and ANSYS part-load
CSV exports use the Settings-tab export-unit mode. The steady-state time-history
export dialog has its own per-column unit selectors.

## UI Composition

- `DirectoryTreeDock`: lets the user select one or more folders after an initial dataset has loaded.
- `SingleDataTab`: single-channel plots, optional phase plot for `FREQ`, optional spectrum/filter/section controls for `TIME`, and computed `Time Step (dt)` / `Sampling Rate (Hz)` selectors.
- `InterfaceDataTab`: grouped multi-select interface and side controls with translational and rotational plots.
- `PartLoadsTab`: part-side multi-select, optional `TIME` sectioning/Tukey controls, and ANSYS export trigger.
- `TimeDomainRepresentTab`: visible for `FREQ`; reconstructs one-cycle time-domain loads at a selected frequency and opens extraction, steady-state time-history export, and steady-state cycle-estimator workflows.
- `CompareDataTab`: loads a secondary dataset and plots overlay, absolute difference, and relative difference charts for one column.
- `ComparePartLoadsTab`: plots side-specific translational and rotational differences.
- `SettingsTab`: controls plot styling, rolling min/max envelope behavior, display-unit selectors, and export-unit mode.

## Controllers and Services

`MainWindow` is the connection hub. Tab widgets emit signals and expose state;
controllers read that state, perform the requested work, and hand figures or
side effects back to the UI.

- `PlotController` owns plot-refresh slots. It snapshots current tab settings,
  converts values to display units, calls `analysis.data_processing` helpers,
  creates figures through `Plotter`, and calls each tab's `display_*` method.
- `ActionHandler` owns workflow slots: comparison selection, reconstructed
  time-domain CSV extraction, steady-state dialogs, and ANSYS export. For
  ANSYS export it validates unit families and passes an `AnsysExportUnits`
  object to `AnsysExporter`.
- `Plotter` owns figure factories and `QWebEngineView` HTML loading.
- `analysis.data_processing` contains pure transforms for sectioning, Tukey
  windows, low-pass filtering, and computed time-step/sampling-rate series.
- `analysis.ansys_exporter` creates harmonic or transient ANSYS Mechanical
  templates from processed, unit-aware export frames.
- `analysis.steady_state_estimator` and
  `analysis.steady_state_time_history_export` support the steady-state helper
  dialogs and CSV export path.

## Data Model

The combined primary DataFrame contains:

- `NO` when present in the source.
- One domain column, either `TIME` or `FREQ`.
- Measurement columns named from the PLD header metadata, such as part/interface
  channels ending in component suffixes like `T1`, `T2`, `T3`, `R1`, `R2`, or
  `R3`.
- `Phase_...` columns for frequency-domain phase data.
- `DataFolder`, the basename of the source folder, used for multi-folder
  grouping and legends.

Comparison data must match the primary domain. Comparison plots skip columns
that are not common to both datasets.

## Domain Behavior

- `FREQ`: phase plots are available for single-folder data, the Time Domain
  Representation tab is shown, frequency-to-angle reconstruction is available,
  and ANSYS export creates harmonic templates using magnitude and phase.
- `TIME`: sectioning, low-pass filtering, Tukey windows, spectrum views,
  time-step/sampling-rate computed selectors, and rolling min/max envelopes are
  available. ANSYS export creates transient templates and partitions large load
  tables.

## Tests and Verification

The repository includes a stdlib `unittest` suite under `tests/` covering unit
contracts, PLD metadata loading, display-unit projection, settings unit controls,
export-unit behavior, and steady-state time-history export helpers.

Run from the repository root:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

## Known Limits

- The first startup folder dialog still exits the application when canceled.
- Loading and plotting large datasets are synchronous and can block the UI.
- ANSYS automation depends on local ANSYS Mechanical installation paths,
  licensing, and `ansys-mechanical-core` compatibility.
- `Export Full Data as CSV` writes the current combined `MainWindow.df` directly;
  keep its displayed-unit message aligned with future implementation changes.
