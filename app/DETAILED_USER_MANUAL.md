# Detailed User Manual

This guide walks through the complete workflow for WE MechLoad Viewer, from installing prerequisites to exporting analysis artifacts for downstream mechanical work.

## 1. System Requirements
- Windows 10+ (PyQt5 with QtWebEngine requires a desktop environment).
- Python 3.10 or newer.
- Optional: Ansys Mechanical with the `ansys-mechanical-core` Python package for template export workflows.

## 2. Installation
1. Ensure Python is on your PATH.
2. Install dependencies: `pip install -r app/requirements.txt`.
3. (Optional) Install `ansys-mechanical-core` via your licensed distribution if you plan to use the Ansys export button.

## 3. Launching the Application
1. From the repository root run `python main.py`.
2. When the file dialog appears, select the directory that contains the raw data folders. Each folder must include:
   - `full.pld`: primary numeric data.
   - `max.pld`: header definitions and interface labels.
3. The application will merge all selected folders, detect whether the data is in the frequency (`FREQ`) or time (`TIME`) domain, and enable the relevant tabs.
4. Use the dock on the left to bring in additional folders at any time. Selecting a new set replaces the current dataset.

## 4. Layout Overview
- **Menu Bar**
  - *File → Open New Data*: launches the folder picker again.
  - *File → Export Full Data as CSV*: saves the merged DataFrame (including `DataFolder`) to disk.
  - *View → Data Folders*: show or hide the directory dock.
- **Directory Dock**: browse and select multiple data folders from the filesystem. Selections trigger a reload.
- **Tabs**: each tab focuses on a specific analysis workflow (details below).
- **Keyboard Shortcuts**
  - `K`: cycle the legend position across predefined corners.
  - `L`: toggle legend visibility.

## 5. Working with Tabs

### 5.1 Single Data Tab
- Choose a channel from the column selector; only applicable channels for the current domain are listed.
- For time-domain data:
  - Enable *Section Data* to limit the plot to a min/max time window.
  - Use *Apply Low-Pass Filter* to smooth the selected channel (Butterworth filter).
  - Toggle *Show Spectrum Plot* for short-time FFT visualizations; pick the plot type and colorscale.
- For frequency-domain data:
  - A phase plot appears automatically if phase information exists and only one folder is loaded.
- Computed options:
  - `Time Step (Δt)` and `Sampling Rate (Hz)` appear when you load time-domain data; both are derived from the raw samples.

### 5.2 Interface Data Tab
- Select an interface (e.g., `I1A`) and a side (extracted from channel names).
- View translational (T1/T2/T3) and rotational (R1/R2/R3) components stacked vertically.
- Use this tab to check symmetry or correlation across channels without comparison data.

### 5.3 Part Loads Tab
- Pick the side of interest.
- Choose whether to exclude secondary components (T2/T3/R2/R3) while keeping resultant channels like `T2/T3`.
- Time-domain extras:
  - *Section Data* to clip the time range.
  - *Apply Tukey Window* (with alpha control) to taper edges before exports.
- *Extract Data*: saves the plotted subset to CSV.
- *Extract Part Loads as FEA Input (ANSYS)*: launches the Ansys export workflow (details in Section 6).

### 5.4 Time Domain Representation Tab
- Appears only for frequency-domain datasets.
- Select a frequency from the drop-down; the app reconstructs time-domain traces using amplitude and phase information.
- Use the interval selector to choose angular increments and export sampled points to CSV.

### 5.5 Compare Data Tab
- Click *Select Data for Comparison* to load a second dataset (same folder structure as the primary).
- Choose a common channel to see:
  - Overlaid original vs comparison traces.
  - Absolute difference plot.
  - Relative (percent) difference plot.
- Columns missing in either dataset are skipped automatically.

### 5.6 Compare Part Loads Tab
- Select a side and optional component suppression (same semantics as Part Loads Tab).
- View difference plots for translational and rotational groups across the full domain.

### 5.7 Settings Tab
- *Rolling Min-Max Envelope*: replaces single-channel traces with rolling envelopes (time-domain only) and toggles bar rendering.
- *Legend / Font / Hover Controls*: update Plotly styling in real time.
- *Trace Opacity*: adjust global opacity applied to every trace across the app.

## 6. Export Workflows

### 6.1 Full Data CSV
- Go to *File → Export Full Data as CSV*.
- Choose a destination path. The exported file includes every column and the `DataFolder` tag for traceability.

### 6.2 Tabular Extracts
- *Single Data / Part Loads / Compare Tabs*: Use the context buttons (e.g., *Extract Data*) to write the currently selected subset to CSV. Valid only when a plot is present.
- *Time Domain Representation*: Select a frequency and interval, then click *Extract Data at Each Interval as CSV file* to download time-sampled results.

### 6.3 Ansys Mechanical Templates
1. Load the desired dataset and switch to the Part Loads tab.
2. Press *Extract Part Loads as FEA Input (ANSYS)*.
3. Select one or more sides in the dialog.
4. The application exports intermediate CSV files (original units and scaled by 1000) and launches Ansys Mechanical through the automation API:
   - Frequency-domain data creates a harmonic response template with complex loads.
   - Time-domain data creates a transient template with the appropriate sampling rate.
5. On success the generated `.mechdat` assets are saved in the working directory and Ansys is opened for review.

## 7. Troubleshooting
- **Folder selection dialog keeps reappearing**: the initial load is required. Canceling the very first prompt will close the app; relaunch and choose a valid folder.
- **Tabs disabled**: Certain tabs require single-folder context or matching columns. Load exactly one folder to view interface or part load tabs.
- **Blank plots**: Verify the selected channel exists and contains numeric data. For spectrum plots ensure the `Spectrum Slices` input is a positive integer.
- **Comparison data rejected**: Both datasets must share the same domain (`TIME` vs `FREQ`) and the target column names. Clean up header mismatches in the source `.pld` files.
- **Ansys export fails**: Confirm `ansys-mechanical-core` is installed and licensed. Review the error dialog for missing channels or data inconsistencies.

## 8. Support
- Bug reports and feature requests go to the maintainer listed in the Settings tab footer.
- Include the exported full-data CSV and the application log (console output) when submitting an issue.
