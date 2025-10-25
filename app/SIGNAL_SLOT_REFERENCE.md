# Signal / Slot Reference

The table below summarizes the key Qt signal connections that tie the application together. Signatures are simplified to highlight intent.

| Emitter | Signal | Receiver Slot | Purpose |
|---------|--------|---------------|---------|
| `DataManager` | `dataLoaded(pd.DataFrame, str, str)` | `MainWindow.on_data_loaded` | Deliver freshly loaded data, detected domain, and the primary folder path. |
| `DataManager` | `comparisonDataLoaded(pd.DataFrame)` | `MainWindow.on_comparison_data_loaded` | Register secondary dataset used by comparison tabs. |
| `DirectoryTreeDock` | `directories_selected(list[str])` | `MainWindow._on_directories_selected` | Request loading of additional folders selected in the dock tree. |
| `MainWindow.open_action` | `triggered()` | `DataManager.load_data_from_directory` | Launch folder picker to replace the current dataset. |
| `MainWindow.export_full_csv_action` | `triggered()` | `MainWindow._export_full_data_csv` | Export the full merged DataFrame to CSV. |
| `SingleDataTab` | `plot_parameters_changed` | `PlotController.update_single_data_plots` | Redraw the main single-channel plot when selectors or filters change. |
| `SingleDataTab` | `spectrum_parameters_changed` | `PlotController.update_spectrum_plot_only` | Refresh the spectrum subplot without affecting other tabs. |
| `InterfaceDataTab` | `plot_parameters_changed` | `PlotController.update_interface_data_plots` | Update translational and rotational charts for the chosen interface. |
| `PartLoadsTab` | `plot_parameters_changed` | `PlotController.update_part_loads_plots` | Recompute part-load plots based on side filters and processing toggles. |
| `PartLoadsTab` | `export_to_ansys_requested` | `ActionHandler.handle_ansys_export` | Start the Ansys Mechanical template export workflow. |
| `TimeDomainRepresentTab` | `plot_parameters_changed` | `PlotController.update_time_domain_represent_plot` | Rebuild reconstructed time-domain plots for the selected frequency. |
| `TimeDomainRepresentTab` | `extract_data_requested` | `ActionHandler.handle_time_domain_represent_export` | Save sampled time-domain data to CSV. |
| `CompareDataTab` | `plot_parameters_changed` | `PlotController.update_compare_data_plots` | Update comparison, absolute difference, and percent difference plots. |
| `CompareDataTab` | `select_compare_data_requested` | `ActionHandler.handle_compare_data_selection` | Open a dialog to choose a secondary dataset for comparison. |
| `ComparePartLoadsTab` | `plot_parameters_changed` | `PlotController.update_compare_part_loads_plots` | Refresh side-specific difference plots across translational and rotational components. |
| `SettingsTab` | `settings_changed` | `PlotController.update_all_plots_from_settings` | Push global styling and rolling-envelope options to every plot. |

All other signal connections are internal to their widgets (for example, controls within `SingleDataTab` emitting `plot_parameters_changed`). Refer to the corresponding tab class for intra-widget wiring details.
