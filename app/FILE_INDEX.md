# File Index

| Path | Lines | Kind | Description |
|------|-------|------|-------------|
| `main_window.py` | 311 | Qt Main Window | Builds the main shell, menu bar, dock, and tab widget; owns shared state and connects signals. |
| `data_manager.py` | 185 | Data service | Loads raw `.pld` data, validates folders, assembles pandas DataFrames, and emits Qt signals. |
| `config_manager.py` | 45 | Styling constants | Centralizes Qt style sheets for tree views, tab bars, group boxes, and buttons. |
| `tooltips.py` | 50 | UI copy | Stores reusable tooltip text for Tukey windows, spectrum slices, and rolling min-max envelopes. |
| `controllers/action_handler.py` | 215 | Controller | Handles multi-step actions (comparison file selection, CSV exports, Ansys template generation); scans for available ANSYS versions and presents version selection dialog. |
| `controllers/plot_controller.py` | 487 | Controller | Responds to tab signals, prepares plot-ready DataFrames, builds Plotly figures, and updates the views. |
| `analysis/data_processing.py` | 244 | Data helpers | Pure functions for slicing, filtering, computed metrics, and multi-folder DataFrame assembly. |
| `analysis/ansys_exporter.py` | 600 | Integration | Automates Ansys Mechanical to build harmonic or transient templates from processed loads; supports version-specific initialization via `mech.App(version=N)`. |
| `plotting/plotter.py` | 470 | Visualization service | Wraps Plotly figure creation, spectrum generation, rolling envelopes, and web view embedding. |
| `ui/directory_tree_dock.py` | 82 | Qt widget | Dockable tree view for selecting additional data folders; emits `directories_selected`. |
| `ui/tab_single_data.py` | 286 | Qt widget | Single-data tab with column selector, optional spectrum and phase plots, and time-domain controls. |
| `ui/tab_interface_data.py` | 83 | Qt widget | Interface tab displaying translational and rotational components for a selected interface and side. |
| `ui/tab_part_loads.py` | 117 | Qt widget | Part loads tab with side filtering, time-domain conditioning, and Ansys export trigger. |
| `ui/tab_time_domain_represent.py` | 56 | Qt widget | Time-domain representation tab for reconstructing angle-based loads at specific frequencies. |
| `ui/tab_compare_data.py` | 76 | Qt widget | Compare data tab with column selector, comparison plot, absolute and relative difference visuals. |
| `ui/tab_compare_part_loads.py` | 48 | Qt widget | Compare part loads tab for per-side difference plots across translational and rotational components. |
| `ui/tab_settings.py` | 110 | Qt widget | Global settings tab managing rolling envelope options and Plotly styling parameters. |
| `resources/icons/app_icon.ico` | — | Asset | Application window icon used by `MainWindow`. |
| `utils/helpers.py` | 8 | Utility module | Reserved for shared helpers (currently empty placeholder). |

See `ARCHITECTURE.md` for the conceptual relationships between these files.
