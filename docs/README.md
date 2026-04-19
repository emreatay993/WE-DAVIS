WE MechLoad Viewer

Overview

- Desktop application to explore and export mechanical load data from `.pld` files.
- Built with PyQt5 for UI and Plotly for interactive plots.
- Supports frequency-domain (`FREQ`) and time-domain (`TIME`) datasets, comparison workflows, and ANSYS Mechanical export.
- Current unit-aware input support is limited to `.pld` folders. `.log` input remains deferred.

Key Features

- Load one or multiple data folders containing `full.pld` and `max.pld`.
- Automatic domain detection (`FREQ` or `TIME`), header mapping from `max.pld`, and source-unit detection from `max.pld` metadata.
- Tabs for Single Data, Interface Data, Part Loads, Time-Domain Representation (`FREQ` only), Comparison, and Settings.
- Settings exposes one display-unit selector per detected quantity family plus an export mode toggle for `Source Units` vs `Display Units`.
- Optional time-domain tools: sectioning, low-pass filtering, Tukey window, rolling min-max envelope.
- Export full combined dataset to CSV and export part loads to ANSYS templates (harmonic or transient).

Quickstart

1. Install Python 3.12 on Windows.
2. Create and activate a virtual environment.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Run the app:
   `python main.py`
5. On first launch, select a dataset folder whose filenames end with `full.pld` and `max.pld`. Bundled samples are available under `resources/sample_data/`.

Data Requirements

- Each selected folder must include:
  - a file ending with `full.pld`: numeric data (`TIME` or `FREQ` column present).
  - a file ending with `max.pld`: header file used to derive interface or channel names and source units.

Unit-Aware Notes

- Source units are detected automatically from `max.pld` channel `UNIT` entries and domain or phase headers such as `FREQ(Hz)`, `TIME(s)`, or `PHASE(deg)`.
- Quantity families come from the parsed unit strings. Unsupported units stay native-only and are surfaced in the Settings summary instead of being guessed.
- Export behavior is explicit: `Source Units` writes the detected raw units, while `Display Units` writes the current projected units shown in the UI.
- The current closeout does not add `.log` ingestion. Future `.log` work should extend the same unit-context contract rather than adding a separate manual override path.

High-Level Workflow

- `DataManager` loads and validates folders, then emits `dataLoaded(df, domain, folder, unit_context)`.
- `MainWindow` receives data, preserves the raw unit context, wires Settings controls, and delegates plotting to `PlotController`.
- `PlotController` builds DataFrames for `Plotter` and applies display-unit projection on demand from the preserved raw frames.
- `ActionHandler` coordinates comparison data selection, time-domain CSV extraction, and ANSYS export while honoring the selected `Source Units` or `Display Units` mode.

Where To Go Next

- Architecture: `docs/Architecture.md`
- Data flow and signals: `docs/DataFlow-and-Signals.md`
- UI guide: `docs/UI-Guide.md`
- Plotting API: `docs/Plotting.md`
- Modules reference: `docs/modules/*.md`
