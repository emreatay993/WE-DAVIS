# WE-DAVIS

WE-DAVIS is a PyQt5 desktop application for inspecting WE Davis mechanical load
datasets. It ingests `.pld` exports, plots frequency-domain and time-domain
data with Plotly, compares runs, and prepares unit-aware CSV/ANSYS handoff
artifacts.

## Core Capabilities

- Load one or more folders containing one or more `*full.pld` data files plus a
  `*max.pld` header file. Suffix matching is case-insensitive.
- Detect `TIME` or `FREQ` data, reject mixed-domain folder selections, merge
  valid folders, and preserve provenance with a `DataFolder` column.
- Track source units from PLD headers, expose display-unit selectors, and let
  extraction/ANSYS workflows choose source-unit or display-unit export mode.
- Plot single channels, interface loads, part loads, comparison overlays,
  absolute/relative differences, spectra, and rolling min/max envelopes.
- Reconstruct one-cycle time histories from frequency data and export repeated
  steady-state histories with optional soft-start ramping.
- Generate ANSYS Mechanical harmonic or transient templates from selected part
  loads with validated force/moment/domain/phase units.

## Quick Start

Use the repository root for setup and execution.

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

The root `requirements.txt` is the pinned runnable/buildable environment. The
package-local `app/requirements.txt` is a looser runtime manifest and is not the
preferred install source for reproducible development.

On startup, choose a data folder whose filenames end with `full.pld` and
`max.pld`. Bundled repository samples live under `resources/sample_data/`; those
sample folders are not bundled by the current PyInstaller spec.

## Data Expectations

- Each selected folder must contain data with either a `TIME` or `FREQ` column.
- `DataManager` matches PLD files by suffix, so names such as
  `PLD_DATA_0_full.pld`, `PLD_DATA_1_FULL.pld`, and
  `PLD_HEADER_DATA_max.pld` are valid.
- The `max.pld` header provides channel labels and source units.
- Frequency-domain datasets use `Phase_...` columns for phase-aware plotting,
  comparison, reconstruction, and ANSYS export.
- Comparison data must match the primary dataset's domain.

## Project Layout

- `main.py`: application entry point.
- `app/main_window.py`: composition root, top-level state, unit preferences,
  menus, tabs, dock, and signal wiring.
- `app/data_manager.py`: PLD loading, domain validation, unit-context creation,
  and comparison loading.
- `app/controllers/plot_controller.py`: plot refresh slots and display-unit
  projection.
- `app/controllers/action_handler.py`: comparison selection, CSV extraction,
  steady-state dialogs, unit-aware part-load export, and ANSYS orchestration.
- `app/analysis/`: data-processing helpers, ANSYS exporter, steady-state cycle
  estimator, and steady-state time-history export helpers.
- `app/units/`: unit catalog, context model, conversion helpers, and errors.
- `app/ui/`: tab widgets, dialogs, directory dock, and reusable UI widgets.
- `app/plotting/plotter.py`: Plotly figure factories and webview loading.

See `FILE_INDEX.md`, `ARCHITECTURE.md`, and `SIGNAL_SLOT_REFERENCE.md` for the
detailed app-local references.

## Verification

Run the current automated test suite from the repository root:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

## Additional Resources

- `../docs/README.md`: documentation landing page.
- `../docs/Architecture.md`: public architecture summary.
- `../docs/DataFlow-and-Signals.md`: end-to-end data and Qt signal flow.
- `../docs/Developer-Guide.md`: setup, packaging, and verification notes.
- `../resources/sample_data/README.md`: bundled sample data summary.
