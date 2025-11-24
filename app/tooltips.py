# File: app/tooltips.py

"""A central repository for all UI tooltip strings."""

SPECTRUM_SLICES = """
<b>Controls the Time vs. Frequency Resolution Trade-off.</b><br><br>
The total time signal is divided into this many segments (slices)
to see how the frequency content changes over time.<br><br>
&#8226; <b>More Slices:</b> Better <i>time resolution</i> (pinpoint <b>when</b> an
  event occurs), but lower frequency precision.<br>
&#8226; <b>Fewer Slices:</b> Better <i>frequency precision</i> (distinguish
  between close frequencies), but vaguer timing.<br><br>
A good starting point is 400.
"""

TUKEY_WINDOW = """
<b>Smoothly tapers data at boundaries to prevent spectral leakage.</b><br><br>
When extracting a <i>section</i> of time-domain data for detailed simulations, 
abrupt cuts at the start/end create artificial discontinuities that introduce 
non-physical high-frequency content (spectral leakage).<br><br>
<b>The Tukey window:</b><br>
&#8226; Smoothly fades data to zero at both boundaries<br>
&#8226; Preserves the central portion of your signal<br>
&#8226; Reduces spurious frequencies in FFT-based analyses<br><br>
<b>Alpha parameter</b> (0.1-0.5) controls the taper fraction:<br>
&#8226; <b>Lower values (0.1):</b> Minimal tapering, preserves more data<br>
&#8226; <b>Higher values (0.5):</b> Gentler transitions, better leakage reduction<br><br>
<i>Recommended for exporting the loads as inputs to transient FEA simulations 
where only a specific portion of data is needed.</i>
"""

ROLLING_MIN_MAX_ENVELOPE = """
<b>Efficiently visualize large time-domain datasets by showing envelope bounds.</b><br><br>
Large scale data often contains thousands of high-frequency oscillation points 
that can overwhelm plots and make it difficult to identify overall trends and 
peak magnitudes.<br><br>
<b>This feature:</b><br>
&#8226; Divides the time series into fixed-size bins<br>
&#8226; Displays only the <i>minimum</i> and <i>maximum</i> values within each bin<br>
&#8226; Preserves critical peak load information while reducing visual clutter<br>
&#8226; Improves rendering performance for datasets with 100k+ points<br><br>
<b>Number of Points Shown</b> controls the bin resolution (default: 50,000):<br>
&#8226; More points = finer envelope detail<br>
&#8226; Fewer points = faster rendering with coarser bounds<br><br>
<i>Ideal for quick exploratory analysis of long-duration data where you need to see overall behavior without plotting every individual cycle and time point.</i>
"""