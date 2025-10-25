Architecture

Directory Structure

- app/
  - analysis/: domain-specific processing and export logic
    - data_processing.py: sectioning, Tukey window, low-pass filter, builders for plot-ready DataFrames
    - ansys_exporter.py: ANSYS Mechanical integration; harmonic/transient template generation
  - controllers/: UI orchestration and business logic
    - plot_controller.py: builds plot data, responds to UI, manages computed metrics and comparisons
    - action_handler.py: long-running/complex user actions (comparison load, CSV extraction, ANSYS export)
  - plotting/: figure construction
    - plotter.py: Plotly figure factory, common styling, spectrum and envelope plots
  - ui/: PyQt5 widgets (tabs and dock)
    - directory_tree_dock.py: folder selection dock, emits directories_selected
    - tab_*.py: tab widgets for data exploration and settings
  - config_manager.py: QSS styles and button styles
  - data_manager.py: data I/O, validation, header mapping, signals
  - main_window.py: composition root, signal wiring, top-level state
  - tooltips.py: HTML tooltips
- main.py: application bootstrap
- scripts/: utilities and diagnostics
  - test_dt.py: robust Δt computation sampler for TIME data

Code Tree (ASCII)

```
WE-DAVIS/
  app/
    analysis/
      ansys_exporter.py
      data_processing.py
    controllers/
      action_handler.py
      plot_controller.py
    plotting/
      plotter.py
    resources/
      icon.ico
    ui/
      directory_tree_dock.py
      tab_compare_data.py
      tab_compare_part_loads.py
      tab_interface_data.py
      tab_part_loads.py
      tab_settings.py
      tab_single_data.py
      tab_time_domain_represent.py
    utils/
      helpers.py
    config_manager.py
    data_manager.py
    main_window.py
    tooltips.py
  scripts/
    test_dt.py
  full_data.csv
  main.py
  requirements.txt
```

Key Responsibilities

- DataManager
  - Opens folder dialogs, validates presence of full.pld and max.pld
  - Reads .pld files into pandas, infers domain (TIME/FREQ)
  - Derives column headers from max.pld; inserts Phase_ columns for FREQ
  - Emits dataLoaded(df, domain, first_folder) and comparisonDataLoaded(df)

- MainWindow
  - Holds application state: df, df_compare, data_domain, raw_data_folder
  - Configures menus, dock, tabs; applies QSS from config_manager
  - Routes UI signals to PlotController and ActionHandler
  - Adjusts tab availability based on number of data folders and domain

- PlotController
  - Builds plot-ready DataFrames using analysis.data_processing helpers
  - Manages computed selections in TIME: Time Step (Δt), Sampling Rate (Hz)
  - Drives Single Data, Interface Data, Part Loads, Time Domain Represent, Compare Data, Compare Part Loads tabs
  - Computes absolute/relative differences for comparison workflows; handles complex difference in FREQ with phase

- ActionHandler
  - Opens comparison-data selection; triggers DataManager.load_comparison_data
  - Exports time-domain reconstructed samples to CSV from TimeDomainRepresentTab
  - Prepares data subsets and invokes AnsysExporter for harmonic/transient templates

- Plotter
  - Standard figure creation for single/multi series and comparison
  - Spectrum from rolling FFT (endaq.calc) and rolling min-max envelope (endaq.plot)
  - Centralized styling: legend, hover, fonts, opacity, positions

- analysis.data_processing
  - Core transforms: sectioning, Tukey window, low-pass filter (Butterworth)
  - Computed metrics: Δt series, sampling rate series
  - Builders returning dict[str, DataFrame] per DataFolder or single DataFrame

- analysis.ansys_exporter
  - Starts ansys.mechanical.core App; accesses global objects
  - Builds loads over frequency/time, real/imag components for harmonic, partitions for transient
  - Saves .mechdat and cleans up temp folders/files; shows completion dialogs

Data Model

- Combined DataFrame (df):
  - Mandatory domain column: FREQ or TIME
  - Optional NO; Many measurement columns like: I1 - Left (T1), I1 - Left (R1), etc.
  - For FREQ domain: matching Phase_ columns for each magnitude column
  - DataFolder: basename of source folder to support multi-folder grouping

Domain-Driven Behavior

- FREQ
  - Phase plots enabled in Single Data (single-folder only)
  - Time Domain Represent tab visible; reconstructs y(θ) = A cos(θ − φ)
  - ANSYS: Harmonic template via phase-aware loads

- TIME
  - Sectioning, low-pass filter, Tukey available where applicable
  - Computed selections: Time Step (Δt), Sampling Rate (Hz)
  - Rolling min-max envelope option across plots
  - ANSYS: Transient template with partitioned load tables

Signals and Ownership

- DataManager → MainWindow: dataLoaded, comparisonDataLoaded
- Tabs → PlotController: plot_parameters_changed (per tab), spectrum_parameters_changed (SingleData)
- Tabs → ActionHandler: export and compare selection requests
- MainWindow orchestrates signal connections and selector population after data loads


