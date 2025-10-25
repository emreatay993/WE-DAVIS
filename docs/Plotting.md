Plotting

Overview

- Plotter (app/plotting/plotter.py) centralizes figure creation and styling.
- Input can be a single DataFrame (multi-column) or dict[str, DataFrame] for multi-trace.
- Standard layout parameters are applied uniformly.

Standard Figures

- create_standard_figure(data_to_plot, title, y_axis_title="Value")
  - If data_to_plot is DataFrame: adds a trace per column
  - If dict[str, DataFrame]: adds a trace per item; assumes one data column per df
  - X-axis title auto-derived from index name ("Time [s]" or "Freq [Hz]")
  - Hover template adapts to domain (Hz vs Time)

Spectrum Figures

- create_spectrum_figure(df, num_slices, plot_type, freq_max=None, colorscale='Hot')
  - Builds rolling FFT via endaq.calc.fft.rolling_fft (adds resultant)
  - Renders with endaq.plot.spectrum_over_time
  - Colorscale applied for Heatmap/Surface; x-axis "Frequency (Hz)", y-axis "Time (s)"

Comparison and Differences

- create_comparison_figure(df1, df2, column, title)
  - Overlays primary vs comparison series for the same column
- create_difference_figure(diff_df, title, y_title)
  - Draws one trace per difference series (used for part-loads comparisons)

Rolling Envelope (TIME)

- create_rolling_envelope_figure(df_dict, title, desired_num_points, plot_as_bars)
  - Concatenates dict of single-column frames into a multi-column DataFrame
  - Uses endaq.plot.rolling_min_max_envelope to reduce points while preserving extrema
  - Obeys global trace opacity

Global Styling and Behavior

- Legend position: cycled by MainWindow key 'K' across presets; toggle visibility with 'L'
- Font sizes and hover mode are set from SettingsTab via PlotController.update_all_plots_from_settings
- Global trace opacity set from SettingsTab.opacity_spin

WebView Integration

- load_fig_to_webview(fig, web_view)
  - Converts figure to full HTML via plotly.io.to_html
  - Writes to a temporary file, tracks and cleans previous temp files per widget
  - Loads into QWebEngineView via file URL










