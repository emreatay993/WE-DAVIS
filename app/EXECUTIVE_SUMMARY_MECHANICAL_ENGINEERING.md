# Executive Summary for Mechanical Engineering

WE-DAVIS supports drivetrain and structural analysts who need a fast path from
test-bench PLD exports to review plots and simulation-ready load inputs.

- **Rapid load validation**: Load one or more PLD folders, preserve source
  folder provenance, and inspect individual channels, interfaces, and part
  loads without writing scripts.
- **Frequency and time-domain support**: Review harmonic magnitude/phase data or
  time histories. Time-domain tooling includes sectioning, low-pass filtering,
  Tukey windows, time-step diagnostics, sampling-rate diagnostics, and rolling
  envelopes.
- **Unit-aware review**: Track source units from headers, switch display units
  by quantity family, and choose source-unit or display-unit export behavior.
- **Comparison workflows**: Overlay primary and comparison data, quantify
  absolute/relative deltas, and use phase-aware complex differences for
  frequency-domain load comparisons where phase columns are available.
- **Simulation handoff**: Export unit-aware CSV files, repeated steady-state
  time histories with optional soft start, and ANSYS Mechanical harmonic or
  transient templates.

The current architecture keeps loading, plotting, unit handling, export actions,
and UI widgets separated so engineering workflows can evolve without forcing a
full rewrite.
