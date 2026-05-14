# Detailed User Manual

This guide covers the main WE-DAVIS workflow from setup through plotting,
comparison, and export.

## 1. System Requirements

- Windows 10/11.
- Python 3.12.
- PyQt5 and PyQtWebEngine from the pinned root requirements.
- Optional: licensed ANSYS Mechanical plus `ansys-mechanical-core` for template
  generation.

## 2. Installation

From the repository root:

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

## 3. Launch

```powershell
python main.py
```

On startup, select a folder containing one or more data files ending in
`full.pld` and a header file ending in `max.pld`. Suffix matching is
case-insensitive. Bundled samples are under `resources/sample_data/`.

The app detects `TIME` or `FREQ`, rejects mixed-domain selections, builds source
unit metadata from headers, and enables the relevant tabs.

## 4. Main Window

- File > Open New Data: choose a replacement dataset.
- File > Export Full Data as CSV: write the current combined DataFrame.
- View menu: show or hide the directory dock.
- Directory dock: select one or more folders after a primary dataset is loaded.
- `K`: cycle legend position.
- `L`: toggle legend visibility.

## 5. Tabs

### Single Data

- Select one non-phase channel.
- For `TIME`, optional controls include Section Data, Low-Pass Filter, Spectrum,
  `Time Step (dt)`, and `Sampling Rate (Hz)`.
- For single-folder `FREQ`, a matching phase plot appears when phase data exists.

### Interface Data

- Select one or more interfaces and one or more sides.
- Translational and rotational plots show selected interface/side pairs.

### Part Loads

- Select one or more part sides.
- Exclude secondary components where needed.
- For `TIME`, apply Section Data or Tukey Window before plotting/export.
- Export Part Loads as FEA Input opens the unit-aware ANSYS export workflow.

### Time Domain Representation

Available for `FREQ` data.

- Select a frequency and interval.
- The app reconstructs one-cycle time histories from magnitude and phase data.
- Extract Data writes sampled one-cycle data to CSV.
- Estimate Cycles to Steady State opens the damping/residual estimator.
- Export Steady-State Time History opens a repeated-cycle export dialog with
  unit selectors and optional soft-start ramp.

### Compare Data

- Select comparison data from a compatible secondary folder.
- Choose a common column.
- Review overlay, absolute difference, and relative difference plots.

### Compare Part Loads

- Select side and exclusion options.
- Review translational and rotational part-load differences. For `FREQ`, phase
  data is used for complex difference calculations where available.

### Settings

- Configure rolling min/max envelope behavior for `TIME` data.
- Configure Plotly font sizes, hover mode, and trace opacity.
- Select display units by detected quantity family.
- Select export-unit mode:
  - Source Units keeps detected source units where possible.
  - Display Units uses the current display-unit selections.

## 6. Export Workflows

### Full Data CSV

File > Export Full Data as CSV writes the current combined DataFrame, including
`DataFolder`, to the chosen path.

### Reconstructed Time-Domain CSV

In Time Domain Representation, select a frequency and interval, then Extract
Data. Values are exported according to the Settings-tab export-unit mode.

### Steady-State Time History CSV

In Time Domain Representation, open Export Steady-State Time History. Choose
whole cycles, soft-start settings, and export units. Soft Start applies a
one-sided half-cosine ramp to load/data columns only; the time column is not
ramped.

### ANSYS Mechanical Templates

1. Load the dataset and open Part Loads.
2. Select sides and optional `TIME` conditioning.
3. Click Export Part Loads as FEA Input.
4. Choose sides and ANSYS version/path options.
5. Confirm.

The app writes unit-aware per-side CSV files plus a combined CSV, validates
ANSYS quantity families, then creates:

- harmonic templates for `FREQ`;
- transient templates for `TIME`.

## 7. Troubleshooting

- Startup cancel closes the app: relaunch and select a valid folder.
- Tabs disabled: many analysis tabs require exactly one loaded folder.
- Blank plot: verify the selected channel exists and contains numeric data.
- Comparison rejected: primary and comparison data must share the same domain.
- Unit conversion unavailable: the source unit may be unknown or native-only.
- ANSYS export fails: verify ANSYS installation, licensing,
  `ansys-mechanical-core`, selected version/path, and unit validation errors.
- Large datasets feel slow: use rolling envelopes and limit expensive plot
  rebuilds where possible.
