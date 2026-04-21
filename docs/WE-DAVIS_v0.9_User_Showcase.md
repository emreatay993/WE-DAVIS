# WE-DAVIS v0.9 User Showcase

Change window: April 7-21, 2026.

WE-DAVIS v0.9 is a pre-1.0 beta ramp focused on making load review, unit handling, and FEA handoff clearer for users. The biggest change is that the app now carries unit context through loading, plotting, CSV export, and ANSYS export instead of relying on implicit assumptions.

## What Users Can Do Now

### Load and Compare More Reliably

- Load one or multiple `.pld` data folders with automatic `full.pld` and `max.pld` pairing.
- Use bundled frequency and transient sample datasets for first-run smoke tests.
- Work with capitalized `.PLD` filenames and multi-select load controls more predictably.
- Keep multi-folder provenance through the `DataFolder` column while comparing campaigns.

### See Data in the Units You Expect

- Configure display units from the Settings tab by detected quantity family.
- View plots in selected display units while preserving the raw/source data model.
- Choose whether export workflows use detected Source Units or selected Display Units.
- See clearer Settings-tab guidance about how CSV exports use those unit choices.

### Export CSV Files With Better Unit Clarity

- Export full combined data with a confirmation that it uses current display units.
- Export sampled time-domain interval CSVs with unit-aware values and unit-labeled headers such as `Theta [deg]`, `Force_A [kN]`, or `Force_A [N]`.
- Export ANSYS-ready CSV inputs with explicit source/display unit mode handling.

### Build Better Time-Domain and Steady-State Handoffs

- Reconstruct frequency-domain loads into theta-based time-domain representations.
- Estimate cycles to steady state before preparing a transient handoff.
- Export steady-state time histories with dedicated unit selectors, preview, and CSV headers.
- Add optional half-cosine soft-start smoothing to steady-state exports so loads ramp in cleanly before reaching steady state.
- Use a fullscreenable steady-state export dialog for larger previews and dense trace sets.

### Work Faster in Plotly Views

- Use `K` to cycle Plotly legend placement.
- Use `L` to toggle Plotly legend visibility.
- Use the same legend shortcuts in the steady-state export preview.
- Render steady-state estimator help as formatted HTML instead of plain text.

## Why It Matters

For users, v0.9 reduces the chance of exporting a file with unclear units or a transient load history with an abrupt start. It also gives a clearer path from raw `.pld` data to reviewed plots, sampled CSVs, steady-state time histories, and ANSYS Mechanical templates.

## Good First Workflow

1. Start WE-DAVIS and load one bundled sample dataset.
2. Open Settings and review detected display units and Export Units mode.
3. Check Single Data, Interface Data, and Part Loads plots.
4. For frequency-domain data, open Time-Domain Representation and export a sampled interval CSV.
5. Open the steady-state estimator, then export a steady-state time history with soft-start smoothing enabled.
6. Confirm exported CSV headers include the units you expect before handing files to downstream simulation work.

## Release Note

This is intentionally labeled `v0.9`, not `v1.0`. The app is feature-rich enough for beta evaluation and field feedback, while still leaving room for final polish, packaging metadata, installer/version resources, and broader smoke-test automation before a 1.0 release.
