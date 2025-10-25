Configuration and Settings

Style Configuration (QSS)

- config_manager.py defines application styles:
  - TREEVIEW_STYLE: dock tree view background, selection colors
  - TABWIDGET_STYLE: tab colors, rounded corners, pane borders
  - GROUPBOX_STYLE: group colors and border radius in Settings tab
  - COMPARE_BUTTON_STYLE: primary button used in CompareDataTab

Runtime Settings (SettingsTab)

- Graphical Settings
  - Legend Font Size: updates Plotter.legend_font_size
  - Default Font Size: updates Plotter.default_font_size
  - Hover Font Size: updates Plotter.hover_font_size
  - Hover Mode: closest/x/y/x unified/y unified → Plotter.hover_mode
  - Trace Opacity: global opacity for all traces → Plotter.trace_opacity

- Data Processing Tools (TIME domain)
  - Rolling Min-Max Envelope (beta):
    - When enabled in TIME domain, Single Data plots render via Plotter.create_rolling_envelope_figure
    - Depends on Desired Number of Points and Plot as Bars toggle
  - Visibility of dependent controls is managed by SettingsTab._on_rolling_min_max_toggled

Keyboard Shortcuts (MainWindow)

- K: cycle legend position across presets (default/top-left/top-right/bottom-right/bottom-left)
- L: toggle legend visibility
Both trigger PlotController.update_all_plots_from_settings to refresh figures.

Domain-Specific UI Toggles

- TIME domain:
  - SingleDataTab exposes: Section Data, Low-Pass Filter, Spectrum controls
  - PartLoadsTab exposes: Section Data, Tukey Window, Tukey α
  - SettingsTab: Rolling Min-Max envelope enabled

- FREQ domain:
  - TimeDomainRepresent tab is shown; SingleData phase plot enabled for single-folder
  - Time-domain-only controls are hidden

Export Configuration

- Export Full CSV (MainWindow): writes current combined df (including DataFolder) to user-chosen path
- ANSYS Export (ActionHandler → AnsysExporter):
  - FREQ → create_harmonic_template: uses magnitudes and Phase_ columns; scales to kN / kN·m; generates APDL tables
  - TIME → create_transient_template: partitions large tables; sets analysis settings from inferred sample rate



