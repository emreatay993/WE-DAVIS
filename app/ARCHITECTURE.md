# Architecture Overview

WE-DAVIS is a desktop application built on PyQt5 for the shell and Plotly for rendering interactive charts. The codebase follows a Model-View-Controller pattern with a thin data layer, tab-specific views, shared controllers, and reusable analysis helpers.

## Layered Structure

| Layer | Modules | Responsibilities |
|-------|---------|------------------|
| Presentation | `app/main_window.py`, `app/ui/*`, `resources/icons/app_icon.ico`, `app/config_manager.py`, `app/tooltips.py` | Define the Qt widgets, styling, and user interactions for menus, docks, and tabs. |
| Controller | `app/controllers/plot_controller.py`, `app/controllers/action_handler.py` | React to UI signals, orchestrate data retrieval and manipulation, and hand figures or side effects back to widgets. |
| Data & Services | `app/data_manager.py`, `app/analysis/data_processing.py`, `app/analysis/ansys_exporter.py`, `app/plotting/plotter.py` | Load and combine raw files, provide reusable data transforms, assemble Plotly figures, and integrate with Ansys Mechanical. |
| Entry Point | `main.py` | Creates the `QApplication`, wires core objects, and kicks off the initial data load prompt. |

## High-Level Flow
1. `main.py` creates `QApplication`, instantiates `DataManager` and `MainWindow`, and starts the event loop.
2. On startup `DataManager.load_data_from_directory()` prompts the user for a raw data folder and calls `load_data_from_paths()`.
3. `DataManager` parses `full.pld` and `max.pld`, constructs a harmonized pandas DataFrame, deduces the domain (`TIME` or `FREQ`), and emits `dataLoaded`.
4. `MainWindow.on_data_loaded()` caches the DataFrame, coordinates tab state (enabling, selector population, dynamic tab insertion), and calls `PlotController.update_all_plots_from_settings()`.
5. Each tab (`SingleDataTab`, `InterfaceDataTab`, etc.) emits signals when the user changes controls. Those signals are connected to methods on `PlotController` or `ActionHandler`.
6. `PlotController` pulls from the cached DataFrames, delegates to `analysis.data_processing` utilities, builds Plotly figures through `Plotter`, and returns the HTML-embedded results to the tabs.
7. Export actions (CSV extraction, Ansys template generation) route through `ActionHandler`, which combines tab state, DataFrames, and helper functions to perform the workflow.

## UI Composition
- **Main Window (`MainWindow`)**: Hosts a menu bar, a directory tree dock (for multi-folder selection), and a `QTabWidget` containing the feature tabs.
- **Directory Tree Dock**: `DirectoryTreeDock` wraps a `QTreeView` with a filesystem model to let users add or replace raw data folders; selections emit `directories_selected`.
- **Tabs**:
  - `SingleDataTab`: Column selector, optional spectrum plot, and optional phase plot for single-folder frequency data.
  - `InterfaceDataTab`: Displays translational and rotational components for a chosen interface and side.
  - `PartLoadsTab`: Focused on side-specific loads with time-domain conditioning (sectioning, Tukey window) and export controls.
  - `TimeDomainRepresentTab`: Available only for frequency-domain data; reconstructs time histories at a selected frequency using amplitude and phase.
  - `CompareDataTab`: Compares a single channel between primary and secondary datasets, including absolute and percent differences.
  - `ComparePartLoadsTab`: Visualizes per-side differences across translational and rotational channels.
  - `SettingsTab`: Adjusts plotting styles and time-domain visualization options.

Tabs do not access data directly; they expose signals and receive ready-to-render figures or commands from controllers.

## Controllers and Services
- **DataManager**
  - Validates folder contents (`full.pld` and `max.pld` pairs), enforces a single domain type across selections, and synthesizes labeled DataFrames.
  - Emits `dataLoaded` with `(DataFrame, domain, primary_folder)` and `comparisonDataLoaded` for secondary datasets.
  - Adds a `DataFolder` column to differentiate multiple runs and sorts by domain for smooth plotting.
- **PlotController**
  - Central registry for domain-specific logic and view updates.
  - Snapshot helpers capture current tab configuration (selectors, toggles) before computing figures.
  - Delegates heavy lifting to `analysis.data_processing` for slicing, filtering, and computed metrics (Δt and sampling rate).
  - Uses `Plotter` to build Plotly figures, ensuring consistent styling via the `SettingsTab`.
  - Maintains derived UI state: enabling/disabling phase plots, adding computed selections, and caching data for time-domain reconstruction.
- **ActionHandler**
  - Handles workflow actions that span multiple tabs or require dialogs (comparison file selection, Ansys export, time-domain CSV extraction).
  - Manages the Ansys export dialog which presents two sections: part selection and ANSYS version selection.
  - Scans `C:\Program Files\ANSYS Inc` for available ANSYS versions (folders starting with 'v') and populates a dropdown sorted by version (latest first).
  - Passes the selected ANSYS version to `AnsysExporter` for template generation using the specific version.
  - Applies the same processing helpers as `PlotController` to keep exported data aligned with what the user sees.
- **Plotter**
  - Provides figure factories (`create_standard_figure`, `create_spectrum_figure`, comparison and difference charts, rolling envelopes).
  - Maintains global styling attributes (font sizes, legend placement, hover mode, opacity) set by the `SettingsTab`.
  - Uses Plotly's HTML output to feed `QWebEngineView` widgets; cleans up temporary files per widget.
- **Analysis Helpers**
  - `analysis/data_processing.py` offers pure functions for sectioning, Tukey windowing, Butterworth filtering, computed metrics, and multi-folder dataset assembly.
  - `analysis/ansys_exporter.py` encapsulates all interaction with `ansys.mechanical.core`, building harmonic or transient templates from selected loads using a specific ANSYS version when provided, or defaulting to the latest available version.

## Data Model
- Primary DataFrame columns include:
  - `NO` (row index from the source),
  - `FREQ` or `TIME` (domain axis),
  - Interface channels (e.g., `I1A - SideName (T1)`) plus optional `Phase_` counterparts for frequency data,
  - `DataFolder` to indicate origin.
- Phase columns are auto-inserted for frequency runs; computed metrics (`Time Step (Δt)`, `Sampling Rate (Hz)`) are generated on demand within the UI.
- Comparison datasets must match the domain of the primary dataset; column name mismatches are gracefully skipped during difference calculations.

## External Dependencies
- **PyQt5 / PyQtWebEngine** for the desktop UI and embedded web views.
- **pandas, numpy, scipy** for data manipulation, filtering, and signal processing.
- **plotly** for interactive visualizations.
- **endaq-calc / endaq-plot** for spectrum and rolling envelope utilities.
- **natsort** for human-friendly selector ordering.
- **ansys-mechanical-core** (optional) for direct Ansys Mechanical automation.

## Extensibility Guidelines
- Keep tab widgets declarative; extend behavior via new signals and controller methods.
- Share data transforms through `analysis/data_processing.py` so that plotting and export logic stay consistent.
- When adding new exports or batch jobs, route the workflow through `ActionHandler` to centralize dialogs and long-running operations.
- For new plots, create a helper on `Plotter` so that styling adjustments remain in one place.

## Known Limitations and Opportunities
- No automated tests; manual verification is required for both TIME and FREQ datasets.
- `AnsysExporter` is tightly coupled to Ansys Mechanical APIs and can be brittle if the external package version changes.
- ANSYS version detection assumes a standard installation path (`C:\Program Files\ANSYS Inc`) and may not detect custom installations.
- `DataManager.load_data_from_directory()` exits the application when the user cancels during the first open; consider soft-failure behavior.
- Re-rendering on every control change can be expensive with very large datasets; caching or decimation strategies could improve responsiveness.
