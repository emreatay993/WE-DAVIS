Developer Guide

Environment

- OS: Windows 10/11 recommended (ANSYS integration is Windows-centric)
- Python: 3.12 (matches venv in repo)
- GUI: PyQt5 + PyQtWebEngine; plotting via Plotly

Setup

1. Create venv and install dependencies
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt

2. Run the app
   python main.py

3. First-run data selection
   - A dialog will ask for a dataset folder containing files whose names end with full.pld and max.pld
   - Bundled samples are available under resources/sample_data/

Coding Conventions

- Prefer explicit, descriptive names for UI widgets and options
- Keep domain logic in analysis/ and orchestration in controllers/
- Plot-ready DataFrames must have index set to TIME or FREQ with human-friendly index name
- Avoid catching broad exceptions unless presenting user feedback; return safe defaults (empty DataFrame/figure) when appropriate

Data Contracts

- TIME domain: 'TIME' column present; sectioning, low-pass, Tukey available
- FREQ domain: 'FREQ' column present; corresponding 'Phase_' columns expected for magnitude columns
- Combined df includes 'DataFolder' to separate multi-folder series

Adding New Tabs or Plots

- Create a new widget under app/ui/
- Expose a plot_parameters_changed signal when options change
- Add display_* methods to load Plotly figures via load_fig_to_webview
- Extend PlotController with snapshot and update_* methods; wire signals in MainWindow._connect_signals

Packaging and Distribution

- Build from the maintained spec:
  .venv\Scripts\python -m PyInstaller --noconfirm WE-DAVIS.spec

- If you use a basic one-file exe command instead of the spec (no ANSYS), keep the hidden import:
  .venv\Scripts\python -m PyInstaller --noconfirm --onefile --windowed --hidden-import pkg_resources --name WE-MechLoad-Viewer main.py

- setuptools must stay below 81 because PyInstaller 6.11 and some dependencies still expect pkg_resources.

- For ANSYS-enabled workflows, ensure ansys-mechanical-core is installed on target and licensed; avoid bundling proprietary DLLs

Testing Notes

- Use scripts/test_dt.py to verify robust Δt computation on TIME datasets
- Manual smoke tests:
  - Load one of the bundled sample folders under resources/sample_data/
  - Load single TIME folder → verify computed selections, spectrum, envelope
  - Load single FREQ folder → verify phase plot and Time Domain Represent
  - Load additional folders from dock → verify multi-folder selectors and legends
  - Comparison flows for both domains
  - ANSYS export (on a machine with ANSYS)

Troubleshooting

- QtWebEngine issues: ensure PyQtWebEngine matches PyQt5 version in requirements
- Missing Phase_ columns: confirm max.pld contains headers; DataManager creates Phase_ labels only for FREQ
- Large datasets: use Rolling Min-Max envelope and limit points to keep UI responsive
















