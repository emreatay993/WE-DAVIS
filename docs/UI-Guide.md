# UI Guide

## Main Window

- File menu: Open New Data, Export Full Data as CSV.
- View menu: toggle the directory dock.
- Dock: `DirectoryTreeDock` shows folders rooted near the first loaded data
  folder. Multi-selection emits `directories_selected(list)`.
- Tabs: Single Data, Interface Data, Part Loads, Compare Data, Compare Data
  (Part Loads), Settings, and Time Domain Representation when `FREQ` data is
  loaded.

## Single Data Tab

- Column selector lists non-phase columns.
- For `TIME`, computed selectors include `Time Step (dt)` and
  `Sampling Rate (Hz)`.
- `TIME` controls include sectioning, low-pass filter, and spectrum.
- `FREQ` single-folder data can show a matching phase plot.
- Spectrum controls include plot type, colorscale, and slice count.

## Interface Data Tab

- Interface selector is a searchable multi-select built with
  `CheckableComboBox`.
- Side selector is grouped under the selected interfaces and preserves still
  valid checked sides when interfaces change.
- Plots show translational and rotational components for selected
  interface/side pairs.

## Part Loads Tab

- Side selector is a searchable multi-select.
- Exclude toggle removes direct secondary components while preserving resultants
  where applicable.
- `TIME` controls include Section Data and Tukey Window.
- Export Part Loads as FEA Input emits `export_to_ansys_requested` and opens the
  ANSYS export workflow.
- Side/exclude changes also refresh the Time Domain Representation plot for
  `FREQ` data.

## Time Domain Representation Tab

Available for `FREQ` data.

- Frequency selector is populated from unique `FREQ` values.
- Interval selector uses divisors of 360 degrees for sampling.
- Extract Data writes sampled one-cycle reconstructed data to CSV.
- Estimate Cycles to Steady State opens the damping/residual estimator.
- Export Steady-State Time History opens the repeated-cycle export dialog.
- Soft Start in the export dialog applies a one-sided half-cosine ramp to
  load/data columns only. It smooths load introduction but does not prove fewer
  physical cycles are needed.
- Reconstruction uses magnitude and phase data to build one-cycle traces.

## Compare Data Tab

- Column selector lists common regular columns after comparison data is loaded.
- Select Data for Comparison opens a secondary dataset folder picker.
- Plots show primary/comparison overlay, absolute difference, and relative
  difference percentage.

## Compare Part Loads Tab

- Side selector and exclude toggle follow the same component-selection intent as
  Part Loads.
- Difference plots use complex magnitude/phase arithmetic for `FREQ` when phase
  columns are available.

## Settings Tab

- Data Processing controls for `TIME`: Rolling Min-Max Envelope, desired number
  of points, and plot-as-bars toggle.
- Graphical controls: legend/default/hover font sizes, hover mode, and trace
  opacity.
- Display-unit selectors are generated from detected source-unit families.
- Export Units chooses Source Units or Display Units for extracted time-domain
  CSV and ANSYS part-load CSV/template workflows.
- Changes emit `settings_changed` and refresh plots through `PlotController`.

## Keyboard Shortcuts

- `K`: cycle legend position.
- `L`: toggle legend visibility.
