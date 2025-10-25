WE MechLoad Viewer

Overview

- Desktop application to explore and export mechanical load data from .pld files.
- Built with PyQt5 for UI and Plotly for interactive plots.
- Supports frequency-domain (FREQ) and time-domain (TIME) datasets; comparison workflows; ANSYS Mechanical export.

Key Features

- Load one or multiple data folders containing full.pld and max.pld.
- Automatic domain detection (FREQ or TIME) and header mapping from max.pld.
- Tabs for Single Data, Interface Data, Part Loads, Time-Domain Representation (FREQ only), Comparison, and Settings.
- Optional time-domain tools: sectioning, low-pass filtering, Tukey window, rolling min-max envelope.
- Export full combined dataset to CSV; export part loads to ANSYS templates (harmonic/transient).

Quickstart

1. Install Python 3.12 on Windows.
2. Create and activate a virtual environment.
3. Install dependencies:
   pip install -r requirements.txt
4. Run the app:
   python main.py
5. On first launch, select a folder that contains both full.pld and max.pld.

Data Requirements

- Each selected folder must include:
  - full.pld: numeric data (TIME or FREQ column present).
  - max.pld: header file used to derive interface/channel names.

High-Level Workflow

- DataManager loads and validates folders → emits dataLoaded(df, domain, folder).
- MainWindow receives data, wires UI state, and delegates plotting to PlotController.
- PlotController builds DataFrames for Plotter, which returns Plotly figures.
- ActionHandler coordinates comparison data selection, time-domain CSV extraction, and ANSYS export.

Where To Go Next

- Architecture: docs/Architecture.md
- Data flow and signals: docs/DataFlow-and-Signals.md
- UI guide: docs/UI-Guide.md
- Plotting API: docs/Plotting.md
- Modules reference: docs/modules/*.md



