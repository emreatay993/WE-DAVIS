# Architecture

WE-DAVIS is a PyQt5 desktop application with Plotly-backed chart rendering. The
current structure is deliberately simple: `MainWindow` owns composition and
state, `DataManager` owns loading, controllers own slots, and analysis/unit
modules provide services.

## Directory Structure

```text
WE-DAVIS/
  main.py
  requirements.txt
  WE-DAVIS.spec
  app/
    analysis/
      ansys_exporter.py
      data_processing.py
      steady_state_estimator.py
      steady_state_time_history_export.py
      v0/resonance_steady_state_cycles_gui.py
    controllers/
      action_handler.py
      plot_controller.py
    plotting/
      plotter.py
    ui/
      directory_tree_dock.py
      steady_state_cycle_estimator_dialog.py
      steady_state_time_history_export_dialog.py
      tab_compare_data.py
      tab_compare_part_loads.py
      tab_interface_data.py
      tab_part_loads.py
      tab_settings.py
      tab_single_data.py
      tab_time_domain_represent.py
      widgets/checkable_combo_box.py
    units/
      catalog.py
      context.py
      conversion.py
      errors.py
    utils/
      helpers.py
    config_manager.py
    data_manager.py
    main_window.py
    tooltips.py
    version.py
  resources/
    icons/app_icon.ico
    sample_data/
  tests/
```

## Component Responsibilities

- `main.py`: starts Qt, creates `DataManager` and `MainWindow`, and schedules
  the initial folder dialog.
- `app/main_window.py`: composition root. Owns top-level state, raw/display unit
  contexts, menu actions, tabs, dock, selector population, tab visibility, and
  signal wiring.
- `app/data_manager.py`: loads PLD folders, matches `*full.pld` and `*max.pld`
  files, detects `TIME`/`FREQ`, builds `ColumnUnitContext` maps, and emits data
  signals.
- `app/controllers/plot_controller.py`: plot-refresh slot owner. Converts data
  to display units, builds plot-ready frames, computes comparisons, and updates
  tabs.
- `app/controllers/action_handler.py`: action workflow owner. Handles comparison
  selection, reconstructed CSV extraction, steady-state dialogs, part-load CSV
  export, ANSYS version/path selection, unit validation, and exporter calls.
- `app/analysis/data_processing.py`: pure DataFrame transforms for sectioning,
  Tukey windows, filters, computed time metrics, and plot builders.
- `app/analysis/ansys_exporter.py`: ANSYS Mechanical harmonic/transient template
  generation using validated `AnsysExportUnits`.
- `app/analysis/steady_state_estimator.py`: damping-based cycle/time estimates.
- `app/analysis/steady_state_time_history_export.py`: repeated-cycle time
  history frame generation, soft-start ramping, unit conversion, and CSV headers.
- `app/units/*`: unit aliases, family inference, display contexts, conversion,
  and unit errors.
- `app/plotting/plotter.py`: Plotly figure factories and `QWebEngineView`
  loading.
- `app/ui/*`: Qt widgets and dialogs. Tabs expose signals and display methods;
  they do not own data loading or export orchestration.

## Data Model

The combined primary DataFrame includes:

- `NO` when present.
- One domain column: `TIME` or `FREQ`.
- Measurement columns from PLD header labels.
- `Phase_...` columns for frequency-domain phase data.
- `DataFolder` to identify the source folder for merged runs.

The unit context map is keyed by column name. It stores source unit,
normalized unit, quantity family, compatible display units, active display unit,
and whether the source unit is native-only.

## Domain Behavior

- `FREQ`: phase plot support, Time Domain Representation tab, one-cycle
  reconstruction, steady-state repeated-cycle export, and harmonic ANSYS export.
- `TIME`: sectioning, low-pass filter, Tukey window, spectrum views, rolling
  min/max envelope, computed `Time Step (dt)` and `Sampling Rate (Hz)`, and
  transient ANSYS export.

## Signals and Ownership

- `DataManager -> MainWindow`: `dataLoaded`, `dataLoadFailed`,
  `comparisonDataLoaded`, and `loadingProgress`.
- `Tabs -> PlotController`: plot/settings change signals.
- `Tabs/MainWindow -> ActionHandler`: comparison selection, CSV extraction,
  steady-state dialogs, and ANSYS export.
- `MainWindow`: central signal wiring and tab refresh routing.

See `docs/DataFlow-and-Signals.md` and `app/SIGNAL_SLOT_REFERENCE.md` for the
full signal map.

## Verification

The current automated suite is under `tests/` and uses stdlib `unittest`:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```
