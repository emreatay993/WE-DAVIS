Data Flow and Qt Signals

End-to-End Data Path

1) User selects primary data folder(s)
- main.py starts app; MainWindow shows; DataManager.load_data_from_directory opens a folder dialog
- DataManager.load_data_from_paths iterates folders:
  - Validates presence of full.pld and max.pld
  - Reads full.pld to infer domain (has FREQ → FREQ, elif TIME → TIME)
  - Reads max.pld headers; for FREQ injects Phase_ columns per interface
  - Renames columns, adds DataFolder = basename(folder)
- DataManager concatenates valid folders, sorts by domain column, emits:
  dataLoaded(final_df, data_domain, first_valid_folder)

2) MainWindow receives data
- on_data_loaded sets df, data_domain, raw_data_folder
- Updates window title (includes parent dir and folder count)
- Populates selectors:
  - SingleData: regular (non-Phase) columns + computed items for TIME
  - InterfaceData: interfaces from I\d+[A-Za-z]? prefix; side list from column regex
  - PartLoads & ComparePartLoads: sides extracted from column pattern " - <side> ("
  - TimeDomainRepresent (FREQ): loads unique FREQ into selector
- Enables/disables tabs based on folder count (single-folder only for several tabs)
- Shows/hides TimeDomainRepresent tab depending on domain (FREQ only)
- Toggles SettingsTab rolling envelope for TIME only
- Triggers PlotController.update_all_plots_from_settings

3) Plot building and updates
- Each tab emits plot_parameters_changed on UI change
- PlotController snapshots tab options, builds plot-ready DataFrames using analysis.data_processing builders
- Plotter turns DataFrames/dicts into Plotly figures with uniform styling
- Tabs load figures via load_fig_to_webview

Comparison Flow

- User clicks "Select Data for Comparison" in CompareDataTab
- ActionHandler.handle_compare_data_selection → DataManager.load_comparison_data
- DataManager loads comparison folder (same mapping rules), emits comparisonDataLoaded(df_compare)
- MainWindow.on_comparison_data_loaded validates domain alignment with primary df
- CompareDataTab gets columns (regular, non-Phase) and enables selection
- PlotController.update_compare_data_plots:
  - Builds two aligned series (primary vs comparison)
  - Computes absolute difference; for FREQ uses complex arithmetic if Phase_ exists
  - Computes relative difference (%) against primary magnitude

Signals Overview

- DataManager
  - dataLoaded(pd.DataFrame, str data_domain, str first_folder)
  - dataLoadFailed(str)
  - comparisonDataLoaded(pd.DataFrame)

- DirectoryTreeDock
  - directories_selected(list[str]) → MainWindow._on_directories_selected → DataManager.load_data_from_paths

- Tabs → PlotController
  - SingleDataTab.plot_parameters_changed, spectrum_parameters_changed
  - InterfaceDataTab.plot_parameters_changed
  - PartLoadsTab.plot_parameters_changed
  - TimeDomainRepresentTab.plot_parameters_changed
  - CompareDataTab.plot_parameters_changed
  - ComparePartLoadsTab.plot_parameters_changed

- Tabs → ActionHandler
  - CompareDataTab.select_compare_data_requested → handle_compare_data_selection
  - PartLoadsTab.export_to_ansys_requested → handle_ansys_export
  - TimeDomainRepresentTab.extract_data_requested → handle_time_domain_represent_export

Domain-Specific Logic

- FREQ
  - Phase plots available for Single Data (single-folder)
  - TimeDomainRepresent reconstructs cosinusoidal tracks at a chosen frequency using magnitude and phase
  - ANSYS export uses phase-aware real/imag components

- TIME
  - Sectioning, Tukey, and low-pass filter available where appropriate
  - Computed metrics injected in SingleData selector: "Time Step (Δt)", "Sampling Rate (Hz)"
  - Settings: Rolling Min-Max Envelope option active; PlotController directs envelope figure when enabled

Error Handling and Guards

- Folder validation warnings (missing .pld) and domain mismatch warnings per folder
- Comparison requires primary data first and matching domain column
- Safe fallbacks: empty frames produce empty figures; filter errors are caught and ignored gracefully



