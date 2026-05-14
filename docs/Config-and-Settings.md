# Configuration and Settings

## Style Configuration

`app/config_manager.py` centralizes QSS constants for:

- dock/tree styling;
- tab widget styling;
- group box styling;
- compare/action button styling;
- reusable `CheckableComboBox` styling.

`app/tooltips.py` stores shared tooltip copy used by plotting and export
controls.

## SettingsTab

`app/ui/tab_settings.py` emits `settings_changed` for plot-style, processing,
display-unit, and export-unit changes. `MainWindow` connects that signal to
`PlotController.update_all_plots_from_settings()`.

### Graphical Settings

- Legend font size.
- Default font size.
- Hover font size.
- Hover mode: closest, x, y, x unified, or y unified.
- Trace opacity.

These values are applied to the shared `Plotter` instance.

### TIME Processing Settings

- Rolling Min-Max Envelope.
- Desired number of points.
- Plot as bars.

The rolling envelope controls are enabled only for `TIME` data. When enabled,
Single Data plots route through `Plotter.create_rolling_envelope_figure(...)`.

### Display Units

After data load, `MainWindow` builds one selector per known quantity family from
the detected source-unit context. Display-unit choices affect plotted/displayed
values.

Unknown or native-only source units are reported in the Settings summary but are
not freely convertible.

### Export Units

The Settings-tab export-unit selector controls extracted time-domain CSV and
ANSYS part-load CSV/template workflows:

- Source Units: keep detected source units where possible.
- Display Units: use the currently selected display units.

The steady-state time-history export dialog has separate per-column unit
selectors and does not rely only on the Settings-tab export-unit mode.

## MainWindow Shortcuts

- `K`: cycle legend position.
- `L`: toggle legend visibility.

Both shortcuts trigger a plot refresh through `PlotController`.

## Export Behavior

- Full CSV writes the current combined `MainWindow.df` directly to a selected
  path.
- Reconstructed time-domain extraction samples `TimeDomainRepresentTab` plot
  data and labels columns with the selected export units.
- ANSYS export validates domain, force, moment, and phase unit families before
  calling `AnsysExporter`.
- Harmonic export uses `FREQ`, magnitude columns, and `Phase_...` columns.
- Transient export uses `TIME` data and partitions large load tables inside the
  exporter.
