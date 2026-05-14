# Developer Guide

## Environment

- OS: Windows 10/11 recommended. ANSYS integration is Windows-centric.
- Python: 3.12.
- GUI stack: PyQt5 and PyQtWebEngine.
- Plotting/data stack: Plotly, pandas, numpy, scipy, endaq, natsort.
- Optional integration: `ansys-mechanical-core` for ANSYS Mechanical automation.

## Setup

Run from the repository root:

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

Use the root `requirements.txt` for reproducible development and packaging.
`app/requirements.txt` is a looser runtime manifest.

## Run

```powershell
python main.py
```

On startup, choose a dataset folder containing one or more files ending in
`full.pld` and one header file ending in `max.pld`. Matching is
case-insensitive. Repository samples live under `resources/sample_data/`.

## Test

The current automated suite uses stdlib `unittest`:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

The suite covers unit contracts, PLD metadata loading, plot unit projection,
settings unit controls, export unit modes, and steady-state time-history export
helpers. `scripts/test_dt.py` remains a diagnostic utility for time-step
experiments, not the main test suite.

## Packaging

Build from the maintained PyInstaller spec:

```powershell
python -m PyInstaller --noconfirm WE-DAVIS.spec
```

The spec builds from `main.py`, names the executable `WE-DAVIS`, hides the
console, includes `resources/icons/app_icon.ico`, and keeps `pkg_resources` as a
hidden import. The current spec does not include `resources/sample_data/`.

`setuptools` is pinned in the root requirements because PyInstaller and some
dependencies still expect `pkg_resources`.

## Coding Conventions

- Keep top-level wiring and state in `MainWindow`.
- Keep data loading and unit-context creation in `DataManager`.
- Keep plot-refresh behavior in `PlotController`.
- Keep cross-tab workflows and side effects in `ActionHandler`.
- Keep reusable transforms in `app/analysis/` and reusable unit logic in
  `app/units/`.
- Tabs should expose signals and `display_*` methods rather than performing data
  loading, export, or plotting orchestration themselves.
- Prefer explicit source/display/export unit handling when adding new workflows.

## Data Contracts

- `TIME` domain requires a `TIME` column. It enables sectioning, low-pass
  filtering, Tukey windows, spectrum views, time-step/sampling-rate computed
  selectors, and transient export.
- `FREQ` domain requires a `FREQ` column and uses matching `Phase_...` columns
  for phase plots, comparison math, reconstruction, and harmonic export.
- Combined frames include `DataFolder` for multi-folder grouping.
- Unit metadata is carried as `ColumnUnitContext` objects keyed by column name.

## Manual Smoke Checks

- Load `resources/sample_data/frequency_sample/`.
- Load `resources/sample_data/time_transient_sample/`.
- Verify Settings-tab display-unit selectors and export-unit mode.
- For `TIME`, verify sectioning/filtering/spectrum/rolling envelope controls.
- For `FREQ`, verify phase plot, Time Domain Representation, cycle estimator,
  and steady-state time-history export dialog.
- Compare two compatible datasets.
- On an ANSYS machine, verify harmonic and transient export paths.

## Troubleshooting

- QtWebEngine failures usually indicate PyQt5/PyQtWebEngine version mismatch.
- Missing phase behavior usually means the loaded frequency columns lack matching
  `Phase_...` columns.
- Unknown or native-only units can be displayed but cannot be converted until
  mapped to a supported quantity family.
- Large datasets can block the UI because loading and plotting are synchronous.
