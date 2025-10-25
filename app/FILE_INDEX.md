# File Index

| Path | Kind | Description |
|------|------|-------------|
| `main_window.py` | Qt Main Window | Builds the main shell, menu bar, dock, and tab widget; owns shared state and connects signals. |
| `data_manager.py` | Data service | Loads raw `.pld` data, validates folders, assembles pandas DataFrames, and emits Qt signals. |
| `config_manager.py` | Styling constants | Centralizes Qt style sheets for tree views, tab bars, group boxes, and buttons. |
| `tooltips.py` | UI copy | Stores reusable tooltip text (currently for spectrum slice guidance). |
| `controllers/action_handler.py` | Controller | Handles multi-step actions (comparison file selection, CSV exports, Ansys template generation). |
| `controllers/plot_controller.py` | Controller | Responds to tab signals, prepares plot-ready DataFrames, builds Plotly figures, and updates the views. |
| `analysis/data_processing.py` | Data helpers | Pure functions for slicing, filtering, computed metrics, and multi-folder DataFrame assembly. |
| `analysis/ansys_exporter.py` | Integration | Automates Ansys Mechanical to build harmonic or transient templates from processed loads. |
| `plotting/plotter.py` | Visualization service | Wraps Plotly figure creation, spectrum generation, rolling envelopes, and web view embedding. |
| `ui/directory_tree_dock.py` | Qt widget | Dockable tree view for selecting additional data folders; emits `directories_selected`. |
| `ui/tab_single_data.py` | Qt widget | Single-data tab with column selector, optional spectrum and phase plots, and time-domain controls. |
| `ui/tab_interface_data.py` | Qt widget | Interface tab displaying translational and rotational components for a selected interface and side. |
| `ui/tab_part_loads.py` | Qt widget | Part loads tab with side filtering, time-domain conditioning, data extraction, and Ansys export triggers. |
| `ui/tab_time_domain_represent.py` | Qt widget | Time-domain representation tab for reconstructing angle-based loads at specific frequencies. |
| `ui/tab_compare_data.py` | Qt widget | Compare data tab with column selector, comparison plot, absolute and relative difference visuals. |
| `ui/tab_compare_part_loads.py` | Qt widget | Compare part loads tab for per-side difference plots across translational and rotational components. |
| `ui/tab_settings.py` | Qt widget | Global settings tab managing rolling envelope options and Plotly styling parameters. |
| `resources/icon.ico` | Asset | Application window icon used by `MainWindow`. |
| `utils/helpers.py` | Utility module | Reserved for shared helpers (currently empty placeholder). |

See `ARCHITECTURE.md` for the conceptual relationships between these files.
