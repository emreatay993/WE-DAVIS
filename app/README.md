# WE MechLoad Viewer

WE MechLoad Viewer is a PyQt5 desktop application for inspecting mechanical load datasets produced by WE Davis style test rigs. It ingests raw `.pld` exports, exposes rich visualizations with Plotly, compares multiple runs, and prepares data for FEA handoff.

## Core Capabilities
- Load one or more raw data folders containing `full.pld` and `max.pld` pairs and automatically stitch them into a single pandas DataFrame.
- Switch between frequency-domain and time-domain analysis with context-aware tooling (phase plots, spectrum views, Tukey windowing, sectioning, sampling-metric overlays).
- Browse dataset folders, plot individual signals, compare runs, and inspect part loads and interface forces through dedicated tabs.
- Export harmonized CSV files and generate Ansys Mechanical templates directly from the UI.
- Control global Plotly styling (fonts, legend placement, hover behavior, opacity) without touching code.

## Quick Start
1. Install dependencies: `pip install -r requirements.txt` (see `app/requirements.txt`).
2. Launch the app from the repo root: `python main.py`.
3. When prompted, pick the directory that contains one or more raw data folders. Each folder must include matching `full.pld` (data) and `max.pld` (header) files.
4. Use the left dock to add more folders at any time. Tabs will enable or disable automatically based on how many folders and which domain type were detected.

## Data Expectations
- Each selected folder should contain harmonized `.pld` exports with either a `FREQ` or `TIME` column.
- `max.pld` files supply channel labels. Frequency-domain loads also expect matching `Phase_` columns; these are constructed automatically.
- Mixed domain folders are rejected for safety; reload data if you need to switch between TIME and FREQ datasets.
- The app decorates every row with a `DataFolder` column to preserve provenance across merged runs.

## Project Layout
- `main.py` is the entry point; it wires the Qt application, constructs `DataManager`, and shows `MainWindow`.
- `app/data_manager.py` reads and validates raw data, emits pandas DataFrames, and handles comparison imports.
- `app/main_window.py` sets up the UI shell, menus, tabs, and connects signals to controllers.
- `app/controllers/plot_controller.py` centralizes Plotly figure creation logic and keeps all tabs in sync.
- `app/controllers/action_handler.py` handles workflow-style operations such as Ansys exports and CSV extraction.
- `app/analysis/` provides reusable data processing utilities and the Ansys exporter integration.
- `app/ui/` contains the QWidget subclasses that define each tab and the directory browser dock.
- `app/plotting/plotter.py` wraps Plotly figure assembly, spectrum generation, and HTML embedding.

See `app/FILE_INDEX.md` for a detailed inventory and `app/ARCHITECTURE.md` for the full architectural overview.

## Additional Resources
- `START_HERE.md`: onboarding checklist for new contributors.
- `DETAILED_USER_MANUAL.md`: end-user walkthrough of every tab and export.
- `SIGNAL_SLOT_REFERENCE.md`: mapping of all Qt signal connections.
- `REFACTORING_PROGRESS.md`: notes on current technical debt and potential improvements.

For questions or feature requests, contact the maintainer listed in the Settings tab footer.
