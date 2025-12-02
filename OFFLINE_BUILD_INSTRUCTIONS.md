# WE-DAVIS Offline Build Instructions

## Problem Summary

When building WE-DAVIS with PyInstaller in an environment with internet access and then transferring to an offline corporate network, plots appeared empty with the error:

```
js: uncaught reference error: plotly is not defined
```

## Root Cause

PyInstaller was not automatically including Plotly's JavaScript files (`plotly.min.js` and related resources) in the bundled executable. The application code was trying to use Plotly, but the necessary JavaScript library wasn't available in the offline environment.

## Solution

The `.spec` file has been updated to explicitly include:
1. All Plotly package data files (including `plotly.min.js`)
2. All endaq package data files (since endaq also uses Plotly)
3. Hidden imports for all Plotly and endaq submodules

## Building for Offline Use

### Option 1: Using the Build Script (Recommended)

Simply run the provided batch file:

```batch
build_offline.bat
```

This script will:
- Clean previous build artifacts
- Build the executable with all necessary resources
- Create the distribution in `dist\WE-DAVIS\`

### Option 2: Manual PyInstaller Command

If you prefer to build manually:

```batch
pyinstaller WE-DAVIS.spec --clean --noconfirm
```

**DO NOT** use the simple command you were using before, as it doesn't include the necessary data files:
```batch
# ❌ DON'T USE THIS ANYMORE
pyinstaller --onedir -w --name "WE-DAVIS" main.py --clean --noconfirm
```

## Transferring to Offline Environment

1. After building successfully, locate the distribution folder:
   ```
   dist\WE-DAVIS\
   ```

2. **Transfer the ENTIRE `dist\WE-DAVIS\` folder** to your offline corporate network
   - This includes all files in the `_internal` subfolder
   - The folder structure must be preserved

3. On the offline system, run:
   ```
   dist\WE-DAVIS\WE-DAVIS.exe
   ```

## Verifying the Build

Before transferring to the offline environment, you can test locally:

1. Build the executable using one of the methods above

2. **Disconnect from the internet** (or disable your network adapter)

3. Run the executable:
   ```
   dist\WE-DAVIS\WE-DAVIS.exe
   ```

4. Load some data and verify that:
   - Plots display correctly
   - No JavaScript errors appear in any console output
   - All plot interactions work (zoom, pan, hover, etc.)

5. Reconnect to the internet

If plots work while offline on your local machine, they will work in the corporate offline network.

## Required Libraries on Offline System

The offline system needs **NO additional Python packages** because PyInstaller bundles everything. However, ensure the offline system has:

- Windows 10 or later
- No special runtime dependencies (PyInstaller bundles Python runtime)

## Troubleshooting

### If plots still don't appear:

1. Check if the `_internal` folder exists next to the `.exe` file
   - If missing, you didn't transfer the complete folder

2. Look for error messages in the application
   - If you see "plotly is not defined", the build wasn't done with the updated `.spec` file

3. Verify the build was done with the updated `.spec` file:
   - Open `WE-DAVIS.spec`
   - Confirm it includes `collect_data_files('plotly')`

4. Ensure you're using the `.spec` file, not the simple PyInstaller command

### If build fails:

1. Ensure all packages are installed:
   ```batch
   pip install -r requirements.txt
   ```

2. Check that PyInstaller is up to date:
   ```batch
   pip install --upgrade pyinstaller
   ```

3. Delete build artifacts and try again:
   ```batch
   rmdir /s /q build dist
   pyinstaller WE-DAVIS.spec --clean --noconfirm
   ```

## Technical Details

### What Changed in `WE-DAVIS.spec`

The updated `.spec` file now includes:

```python
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files from plotly (includes plotly.min.js and other resources)
plotly_datas = collect_data_files('plotly')

# Collect data files from endaq (which also uses plotly for plotting)
endaq_datas = collect_data_files('endaq')

# Combine all data files
all_datas = plotly_datas + endaq_datas

# Collect all submodules to ensure everything is included
hidden_imports = collect_submodules('plotly') + collect_submodules('endaq')
```

These additions ensure that:
- `plotly.min.js` is bundled in the `_internal` folder
- All Plotly template files and resources are included
- All endaq plotting resources are included
- Python can find and load these resources at runtime

### How Plotly Works Offline

When `plotly.io.to_html()` is called with `include_plotlyjs=True`, it:
1. Looks for the bundled `plotly.min.js` file in the package data
2. Reads the entire JavaScript library
3. Embeds it directly into the generated HTML
4. No internet connection required

Without the fix, PyInstaller wasn't including the JavaScript file, so Plotly couldn't embed it, resulting in empty plots.

## Summary

✅ **Always use** `WE-DAVIS.spec` to build
✅ **Always transfer** the entire `dist\WE-DAVIS\` folder
✅ **Test offline** before transferring to corporate network
❌ **Never use** the simple `pyinstaller` command anymore
❌ **Never transfer** just the `.exe` file without the `_internal` folder

---

For questions or issues, refer to the main project documentation or contact the development team.

