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
  - Widgets: interface_selector (CheckableComboBox), side_selector (CheckableComboBox); two QWebEngineView plots
  - Behavior:
    - interface_selector lets the user check multiple interfaces; the collapsed trigger shows a count summary (e.g. "3 interfaces selected")
    - side_selector is rebuilt whenever the checked interfaces change via _rebuild_side_selector_from_checked_interfaces; each checked interface becomes a disabled group-header row followed by its native part sides (populated via regex against column names). Previously-checked sides that still exist under the new set of interfaces stay checked.
    - T and R plots overlay one curve per (interface, side) pair with a stable per-pair color; legend labels combine interface id and side name.
  - Methods:
    - refresh_selectors(preserve_selection=True); selected_interfaces(); selected_sides()
    - display_t_series_plot(fig), display_r_series_plot(fig)

tab_part_loads.py

- PartLoadsTab(QWidget)
  - Signals: plot_parameters_changed, export_to_ansys_requested
  - Widgets: side_filter_selector (CheckableComboBox); exclude checkbox; TIME-only options (Tukey, Section Data); plots; extract buttons
  - Behavior:
    - side_filter_selector lets the user check multiple part sides; the T and R plots render one curve per checked side
    - The ANSYS export dialog (invoked via export_to_ansys_requested) pre-checks the set of sides currently checked in the tab, while still letting the user adjust the selection inside the dialog
  - Methods:
    - set_available_sides(sides, preserve_selection=True); selected_sides()
    - set_time_domain_features_visibility(visible); display_t_series_plot(fig); display_r_series_plot(fig)

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
  - Behavior: user-facing behavior is unchanged; when the Part Loads side_filter_selector has multiple sides checked, the snapshot taken for this tab uses the first selected side

tab_settings.py

- SettingsTab(QWidget)
  - Signal: settings_changed
  - Widgets:
    - Data Processing Group (TIME): rolling_min_max_checkbox, plot_as_bars_checkbox, desired_num_points_input
    - Graphical Settings: legend/default/hover font sizes, hover mode, opacity_spin
  - Behavior: toggles dependent control visibility; broadcasts settings_changed for any change

widgets/checkable_combo_box.py

- CheckableComboBox(QWidget)
  - Signal: selectionChanged (debounced ~100 ms; re-emits only when the checked set actually changes)
  - Qt-only (no QtWebEngine) styled multi-select dropdown with search box and Select all / Clear footer; styling pulled from config_manager.CHECKABLE_COMBO_STYLE
  - Population modes:
    - set_items(items, preserve_selection=True): flat list of checkable rows
    - set_grouped_items(groups, preserve_selection=True): groups is a sequence of (header, children) tuples; each header renders as a disabled header row followed by its indented children
  - Configuration: set_placeholder(text); set_noun(singular, plural) drives the collapsed trigger summary (e.g. "3 interfaces selected")
  - Accessors: selected_items() -> list[str] returns the checked child values (headers excluded)
  - Used by InterfaceDataTab (interface_selector, side_selector) and PartLoadsTab (side_filter_selector)

Tooltips

- tooltips.py: SPECTRUM_SLICES HTML tooltip used by SingleDataTab.num_slices_input
















