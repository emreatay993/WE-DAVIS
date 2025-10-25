UI Guide

Main Window

- Menu: File → Open New Data, Export Full Data as CSV; View → toggle directory dock
- Dock: DirectoryTreeDock presents filesystem view rooted at parent of the first loaded data folder; multi-select emits directories_selected(list)
- Tabs: Single Data, Interface Data, Part Loads, Compare Data, Compare Data (Part Loads), Settings; Time Domain Rep. tab is conditionally shown for FREQ

Single Data Tab

- Column selector lists non-Phase columns plus computed items in TIME: "Time Step (Δt)", "Sampling Rate (Hz)"
- Options (TIME only):
  - Section Data (min/max time)
  - Low-Pass Filter (cutoff, order)
  - Spectrum (rolling FFT): plot type (Heatmap/Surface/Waterfall/Animation/Peak/Lines), colorscale, slices
- Plots:
  - Regular plot always visible
  - Phase plot: shown for FREQ if a matching Phase_ column exists and single-folder
  - Spectrum plot: shown when Spectrum is checked (TIME only)

Interface Data Tab

- Interface selector: type-to-search list of interfaces found by I\d+[A-Za-z]?
- Part Side Filter: sides extracted from column names (e.g., "Left", "Right")
- Plots:
  - Translational components (T1, T2, T3, T2/T3)
  - Rotational components (R1, R2, R3, R2/R3)

Part Loads Tab

- Side filter selector; Exclude T2/T3/R2/R3 checkbox (keeps resultants T2/T3, R2/R3)
- TIME-only options: Section Data, Tukey Window (α)
- Lower controls: selector for data points (reserved), Extract Data (CSV of sampled time-domain in Time Domain Rep.), Extract Part Loads as FEA Input (ANSYS)
- Plots: Translational and Rotational component groups

Time Domain Representation Tab (FREQ domain only)

- Frequency selector populated with unique FREQ values
- Interval selector with divisors of 360 for sampling (1..360)
- Extract Data button emits extract_data_requested; ActionHandler exports sampled CSV
- Plot reconstructs y(θ) = A cos(θ − φ) for each selected side component

Compare Data Tab

- Column selector lists regular non-Phase columns
- Button opens comparison folder; triggers DataManager.load_comparison_data
- Plots:
  - Primary vs Comparison overlay
  - Absolute Difference Δ
  - Relative Difference (%) relative to primary

Compare Part Loads Tab

- Side filter selector; Exclude toggle (same rule as Part Loads)
- Plots: Δ series for translational and rotational groups using complex magnitude+phase when available

Settings Tab

- Data Processing (TIME): Rolling Min-Max envelope controls
- Graphical Settings: font sizes, hover mode, global trace opacity
- Changes broadcast settings_changed; PlotController.update_all_plots_from_settings refreshes figures

Directory Tree Dock

- Multi-select folders; selections emit directories_selected(list) to request additional loads via DataManager.load_data_from_paths
- Hidden columns 1–3; only the name column is visible

Keyboard Shortcuts

- K: cycle legend position
- L: toggle legend visibility



