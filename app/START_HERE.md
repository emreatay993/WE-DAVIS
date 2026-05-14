# Start Here

Use this checklist to get productive with WE-DAVIS quickly.

## 1. Understand the Product

- Read `README.md` for the app overview and quick start.
- Read `DETAILED_USER_MANUAL.md` for user workflows and tab vocabulary.
- Read `ARCHITECTURE.md` for the runtime structure.
- Keep `FILE_INDEX.md` and `SIGNAL_SLOT_REFERENCE.md` open while navigating.

## 2. Prepare Your Environment

Recommended stack:

- Windows 10/11.
- Python 3.12.
- PyQt5/PyQtWebEngine desktop environment.
- Optional licensed ANSYS Mechanical plus `ansys-mechanical-core` for template
  export workflows.

From the repository root:

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

Use the root `requirements.txt` for pinned development/build installs. The
package-local `app/requirements.txt` is only a looser runtime manifest.

## 3. Run the Application

```powershell
python main.py
```

On startup, select a folder containing one or more `*full.pld` data files and a
`*max.pld` header file. Matching is case-insensitive. Bundled sample folders
live under `resources/sample_data/`.

## 4. Verify the Baseline

Run automated tests:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Manual smoke checks:

- Load `resources/sample_data/frequency_sample/`.
- Load `resources/sample_data/time_transient_sample/`.
- Exercise Settings-tab display/export unit controls.
- For `FREQ`, verify phase plots, Time Domain Representation, the estimator,
  and steady-state export dialog.
- For `TIME`, verify sectioning, filtering, spectrum, rolling envelope, and
  transient export behavior.

## 5. Contribute Safely

- Put top-level wiring/state in `MainWindow`.
- Put data loading and unit-context creation in `DataManager`.
- Put plot refreshes in `PlotController`.
- Put cross-tab workflows and exports in `ActionHandler`.
- Put reusable transforms in `app/analysis/` and unit behavior in `app/units/`.
- Update docs and tests when behavior changes.
