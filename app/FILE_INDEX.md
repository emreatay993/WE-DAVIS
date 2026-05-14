# File Index

Line counts were refreshed against the current `app/` tree with
`[System.IO.File]::ReadAllLines(...).Count`.

## Root Entrypoints

| Path | Lines | Kind | Responsibility |
| --- | ---: | --- | --- |
| `../main.py` | - | Entry point | Creates `QApplication`, wires `DataManager` and `MainWindow`, shows the window, and opens the initial folder picker. |
| `../requirements.txt` | - | Pinned environment | Full pinned install/build environment, including PyQt, Plotly, scipy, endaq, ANSYS packages, PyInstaller, and setuptools pin. |
| `../WE-DAVIS.spec` | - | Packaging | PyInstaller spec for the `WE-DAVIS` executable. |

## App Package

| Path | Lines | Kind | Responsibility |
| --- | ---: | --- | --- |
| `main_window.py` | 520 | Qt shell | Main window, menus, dock, tabs, application state, unit preferences, and cross-component signal wiring. |
| `data_manager.py` | 287 | Data service | Loads PLD folders, parses `*full.pld` and `*max.pld`, detects domain, builds unit metadata, and emits data signals. |
| `config_manager.py` | 206 | Styling constants | Shared QSS strings for tabs, docks, group boxes, buttons, and reusable widgets. |
| `tooltips.py` | 82 | UI copy | Shared tooltip text for spectrum, rolling envelope, Tukey, and export controls. |
| `version.py` | 6 | Metadata | Defines `WE-DAVIS` application name and version label. |
| `requirements.txt` | - | Runtime manifest | Looser runtime dependency list kept beside the package. Use root `requirements.txt` for pinned installs/builds. |

## Controllers

| Path | Lines | Kind | Responsibility |
| --- | ---: | --- | --- |
| `controllers/plot_controller.py` | 1160 | Plot controller | Slot owner for plot refreshes, display-unit projection, comparison differences, part/interface filtering, and frequency-to-time reconstruction. |
| `controllers/action_handler.py` | 632 | Action controller | Comparison selection, reconstructed CSV extraction, steady-state dialogs, unit-aware part-load CSV export, and ANSYS template orchestration. |

## Analysis

| Path | Lines | Kind | Responsibility |
| --- | ---: | --- | --- |
| `analysis/data_processing.py` | 244 | Data helpers | Sectioning, Tukey windowing, low-pass filtering, time-step/sampling-rate series, and plot-ready DataFrame builders. |
| `analysis/ansys_exporter.py` | 828 | ANSYS integration | Harmonic and transient Mechanical template creation with unit-aware `AnsysExportUnits`. |
| `analysis/steady_state_estimator.py` | 103 | Estimator service | Damping-based steady-state cycle/time estimates for the estimator dialog. |
| `analysis/steady_state_time_history_export.py` | 195 | Export service | Repeated-cycle time-history frame generation, soft-start ramping, unit conversion, and CSV header labels. |
| `analysis/v0/resonance_steady_state_cycles_gui.py` | 623 | Legacy tool | Standalone legacy steady-state estimator GUI kept for reference. |

## Plotting

| Path | Lines | Kind | Responsibility |
| --- | ---: | --- | --- |
| `plotting/plotter.py` | 275 | Visualization service | Plotly figure factories, rolling envelope rendering, global plot styling, and webview HTML loading. |

## UI

| Path | Lines | Kind | Responsibility |
| --- | ---: | --- | --- |
| `ui/directory_tree_dock.py` | 55 | Dock widget | Filesystem tree rooted near the loaded folder; emits selected directories. |
| `ui/tab_single_data.py` | 286 | Tab widget | Single-channel plotting, phase/spectrum display, filter/section controls, and computed selectors. |
| `ui/tab_interface_data.py` | 138 | Tab widget | Grouped interface/side multi-select controls and translational/rotational plots. |
| `ui/tab_part_loads.py` | 128 | Tab widget | Part-side multi-select plots, `TIME` conditioning controls, and ANSYS export request. |
| `ui/tab_time_domain_represent.py` | 69 | Tab widget | Frequency reconstruction controls and extraction/steady-state action signals. |
| `ui/tab_compare_data.py` | 81 | Tab widget | Comparison dataset selection and overlay/absolute/relative difference plots. |
| `ui/tab_compare_part_loads.py` | 58 | Tab widget | Part-load difference controls and translational/rotational difference plots. |
| `ui/tab_settings.py` | 206 | Tab widget | Plot styling, rolling envelope controls, display-unit selectors, and export-unit mode. |
| `ui/steady_state_cycle_estimator_dialog.py` | 473 | Dialog | Damping/residual-input estimator with result table and help content. |
| `ui/steady_state_time_history_export_dialog.py` | 450 | Dialog | Repeated-cycle preview/export dialog with soft-start and export-unit controls. |
| `ui/widgets/checkable_combo_box.py` | 703 | Reusable widget | Searchable grouped multi-select with debounced `selectionChanged`. |
| `ui/widgets/__init__.py` | 1 | Package marker | Widget package marker. |

## Units and Utilities

| Path | Lines | Kind | Responsibility |
| --- | ---: | --- | --- |
| `units/catalog.py` | 228 | Unit catalog | Unit aliases, compatible units, and quantity-family inference. |
| `units/context.py` | 113 | Unit context | `ColumnUnitContext` model and context-map builder. |
| `units/conversion.py` | 99 | Unit conversion | Scalar, series, and DataFrame conversion helpers. |
| `units/errors.py` | 13 | Exceptions | Unit conversion exception types. |
| `units/__init__.py` | 43 | Public API | Re-exports unit package API. |
| `utils/helpers.py` | 66 | Parsing helpers | PLD label helpers for interface, part side, and component suffix extraction. |

## Assets

| Path | Kind | Responsibility |
| --- | --- | --- |
| `resources/icon.ico` | Asset | App-local icon asset. |
| `../resources/icons/app_icon.ico` | Asset | Runtime icon used by `MainWindow` and PyInstaller. |

See `ARCHITECTURE.md` for conceptual relationships and
`SIGNAL_SLOT_REFERENCE.md` for Qt wiring.
