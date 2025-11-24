UI Modules Reference

directory_tree_dock.py

- DirectoryTreeDock(QDockWidget)
  - directories_selected = pyqtSignal(list)
  - set_root_path(path): roots QFileSystemModel at parent of path; hides size/type/date columns
  - _on_selection_changed: collects selected directories and emits directories_selected

tab_single_data.py

- SingleDataTab(QWidget)
  - Signals: plot_parameters_changed, spectrum_parameters_changed
  - Key widgets: column_selector; spectrum controls (plot_type, colorscale, slices); filter controls (cutoff, order); section controls (min/max time)
  - Methods:
    - set_phase_plot_visibility(visible), set_spectrum_plot_visibility(visible), set_time_domain_features_visibility(visible)
    - display_regular_plot(fig), display_phase_plot(fig), display_spectrum_plot(fig)
  - Behavior:
    - Computed selections ('Time Step (Δt)', 'Sampling Rate (Hz)') force-hide filter/spectrum controls

tab_interface_data.py

- InterfaceDataTab(QWidget)
  - Signal: plot_parameters_changed
  - set_dataframe(df): stored for side population
  - Widgets: interface_selector, side_selector; two QWebEngineView plots
  - Behavior: on interface change, populates sides via regex against column names
  - Methods: display_t_series_plot(fig), display_r_series_plot(fig)

tab_part_loads.py

- PartLoadsTab(QWidget)
  - Signals: plot_parameters_changed, export_to_ansys_requested
  - Widgets: side_filter_selector; exclude checkbox; TIME-only options (Tukey, Section Data); plots; extract buttons
  - Methods: set_time_domain_features_visibility(visible); display_t_series_plot(fig); display_r_series_plot(fig)

tab_compare_data.py

- CompareDataTab(QWidget)
  - Signals: plot_parameters_changed, select_compare_data_requested
  - Widgets: compare_column_selector; three plots (overlay, absolute, relative); button styled via COMPARE_BUTTON_STYLE
  - Methods: display_comparison_plot(fig); display_absolute_diff_plot(fig); display_relative_diff_plot(fig)

tab_compare_part_loads.py

- ComparePartLoadsTab(QWidget)
  - Signal: plot_parameters_changed
  - Widgets: side_filter_selector; exclude checkbox; two plots
  - Methods: display_t_series_plot(fig); display_r_series_plot(fig)

tab_time_domain_represent.py

TimeDomainRepresentTab (QWidget)
  - Signals: plot_parameters_changed, extract_data_requested
  - Widgets: frequency selector; interval selector (divisors of 360); plot; extract button
  - Methods: display_plot(fig)
  - State: current_plot_data dict populated by PlotController for extraction

tab_settings.py

- SettingsTab(QWidget)
  - Signal: settings_changed
  - Widgets:
    - Data Processing Group (TIME): rolling_min_max_checkbox, plot_as_bars_checkbox, desired_num_points_input
    - Graphical Settings: legend/default/hover font sizes, hover mode, opacity_spin
  - Behavior: toggles dependent control visibility; broadcasts settings_changed for any change

Tooltips

- tooltips.py: SPECTRUM_SLICES HTML tooltip used by SingleDataTab.num_slices_input
















