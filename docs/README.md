# WE-DAVIS Documentation

WE-DAVIS is a PyQt5 desktop application for exploring WE Davis mechanical load
`.pld` exports, comparing runs, reconstructing frequency-domain loads into
time histories, and preparing unit-aware CSV/ANSYS handoff data.

## Quickstart

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

On first launch, select a folder containing one or more `*full.pld` data files
and a `*max.pld` header file. Suffix matching is case-insensitive. Repository
samples are available under `resources/sample_data/`.

## Key Features

- Load single-folder or multi-folder `TIME`/`FREQ` datasets.
- Preserve `DataFolder` provenance across merged folders.
- Track source units from headers, choose display units in Settings, and choose
  source-unit or display-unit export mode for extracted/ANSYS CSV workflows.
- Plot single channels, interfaces, part loads, comparisons, spectra, rolling
  envelopes, and frequency-to-time reconstructions.
- Export full data, sampled reconstructed cycles, repeated steady-state
  histories with optional soft start, and ANSYS Mechanical templates.

## High-Level Workflow

1. `DataManager` validates PLD folders, builds the combined DataFrame and unit
   context map, then emits `dataLoaded(df, domain, first_folder, unit_context)`.
2. `MainWindow` stores raw/display state, populates selectors, adjusts tab
   availability, refreshes unit controls, and delegates plot refreshes.
3. `PlotController` builds plot-ready frames in display units and passes figures
   to `Plotter`/tab display methods.
4. `ActionHandler` coordinates comparison loading, reconstructed CSV extraction,
   steady-state dialogs, and ANSYS export.

## Documentation Map

- `docs/Architecture.md`: code structure and component responsibilities.
- `docs/DataFlow-and-Signals.md`: data path and Qt signal/slot map.
- `docs/Developer-Guide.md`: environment, run, test, and packaging commands.
- `docs/UI-Guide.md`: user-facing tab behavior.
- `docs/Config-and-Settings.md`: settings and export-unit behavior.
- `docs/Plotting.md`: Plotly rendering service notes.
- `docs/modules/*.md`: focused module references.
- `app/ARCHITECTURE.md`, `app/FILE_INDEX.md`, `app/SIGNAL_SLOT_REFERENCE.md`:
  app-local implementation references.
