# Final Project State

## Codebase

- Source architecture is organized around `main.py`, `MainWindow`,
  `DataManager`, controllers, analysis services, plotting, units, and UI
  widgets.
- Unit-aware loading, display-unit selection, source/display export modes,
  steady-state time-history export, and ANSYS export are reflected in the docs.
- Automated `unittest` coverage exists under `tests/`.

## Documentation

- App-local references have been refreshed:
  `README.md`, `ARCHITECTURE.md`, `FILE_INDEX.md`,
  `SIGNAL_SLOT_REFERENCE.md`, and supporting guides.
- Public docs under `docs/` have been aligned with the same current facts.
- Historical implementation plans and presentation notes remain outside this
  refresh scope.

## Outstanding Items

- Replace first-load cancel exit with a soft failure path.
- Add focused Qt signal/wiring tests.
- Evaluate async loading and plot caching for large datasets.
- Keep ANSYS export behavior validated on licensed ANSYS hosts.
