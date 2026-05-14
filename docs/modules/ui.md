# UI Modules Reference

## `directory_tree_dock.py`

`DirectoryTreeDock(QDockWidget)`

- Signal: `directories_selected(list)`.
- `set_root_path(path)` roots a `QFileSystemModel` near the loaded dataset and
  hides non-name columns.
- Selection changes collect selected directories and emit them for
  `MainWindow._on_directories_selected`.

## `tab_single_data.py`

`SingleDataTab(QWidget)`

- Signals: `plot_parameters_changed`, `spectrum_parameters_changed`.
- Key widgets: column selector, phase/spectrum/regular plot webviews,
  filter controls, section controls, spectrum type/colorscale/slice controls.
- Methods include `set_phase_plot_visibility(...)`,
  `set_spectrum_plot_visibility(...)`,
  `set_time_domain_features_visibility(...)`, and `display_*` methods.
- Computed `TIME` selections such as `Time Step (dt)` and
  `Sampling Rate (Hz)` hide incompatible filter/spectrum controls.

## `tab_interface_data.py`

`InterfaceDataTab(QWidget)`

- Signal: `plot_parameters_changed`.
- Widgets: grouped `CheckableComboBox` interface selector and side selector.
- `set_dataframe(df)` stores data for selector population.
- Interfaces can be multi-selected; side options rebuild under interface group
  headers while preserving still-valid checks.
- T/R plots overlay selected interface/side pairs.

## `tab_part_loads.py`

`PartLoadsTab(QWidget)`

- Signals: `plot_parameters_changed`, `export_to_ansys_requested`.
- Widgets: side multi-select, exclude toggle, `TIME` section/Tukey controls,
  T/R plots, ANSYS export button.
- `set_available_sides(...)` and `selected_sides()` manage side selection.
- Side/exclude changes also drive the `FREQ` Time Domain Representation plot
  through `MainWindow` signal wiring.

## `tab_time_domain_represent.py`

`TimeDomainRepresentTab(QWidget)`

- Signals: `plot_parameters_changed`, `extract_data_requested`,
  `steady_state_time_history_export_requested`,
  `steady_state_estimator_requested`.
- Widgets: frequency selector, interval selector, plot webview, extract button,
  steady-state export button, and estimator button.
- State: `current_plot_data` is populated by `PlotController` and used by export
  actions.

## `tab_compare_data.py`

`CompareDataTab(QWidget)`

- Signals: `plot_parameters_changed`, `select_compare_data_requested`.
- Widgets: compare column selector, comparison button, overlay plot, absolute
  difference plot, and relative difference plot.

## `tab_compare_part_loads.py`

`ComparePartLoadsTab(QWidget)`

- Signal: `plot_parameters_changed`.
- Widgets: side selector, exclude toggle, and T/R difference plots.

## `tab_settings.py`

`SettingsTab(QWidget)`

- Signal: `settings_changed`.
- Data Processing group: rolling min/max envelope, plot-as-bars, desired points.
- Graphical Settings: legend/default/hover font sizes, hover mode, trace
  opacity.
- Unit controls: display-unit selectors by quantity family and export-unit mode
  selector for Source Units vs Display Units.

## `steady_state_cycle_estimator_dialog.py`

`SteadyStateCycleEstimatorDialog(QDialog)`

- Inputs: damping ratio, excitation frequency, optional mode frequency, residual
  transient percentage.
- Shows common residual estimates and stores the latest conservative whole-cycle
  recommendation.

## `steady_state_time_history_export_dialog.py`

`SteadyStateTimeHistoryExportDialog(QDialog)`

- Inputs: whole cycles, soft-start toggle, ramp cycles, export unit selectors,
  and unknown-unit labels.
- Builds a preview of the repeated steady-state history.
- Applies soft start only to load/data columns before unit conversion and CSV
  header generation.

## `widgets/checkable_combo_box.py`

`CheckableComboBox(QWidget)`

- Signal: `selectionChanged()` after a 100 ms debounce and checked-set
  deduplication.
- Searchable multi-select dropdown with Select all/Clear actions.
- Supports flat items and grouped header/child rows.
- Used by Interface Data and Part Loads selectors.

## `tooltips.py`

Shared tooltip copy for spectrum, rolling envelope, Tukey, and export controls.
