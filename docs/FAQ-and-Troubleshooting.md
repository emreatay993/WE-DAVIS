FAQ and Troubleshooting

Data Loading

- Q: Folder selection shows warnings about missing .pld files.
  - A: Each folder must contain both full.pld and max.pld. Skip invalid folders or fix contents.

- Q: Domain mismatch warning for one of the selected folders.
  - A: All folders in a batch must be either TIME or FREQ. Remove the mismatched folder or load it separately.

- Q: No TIME or FREQ column found.
  - A: Ensure the full.pld file conforms to expected format and includes a TIME or FREQ column.

UI/Plots

- Q: Phase plot doesn’t appear in Single Data.
  - A: Phase plot is shown only in FREQ domain, single-folder mode, and when a matching Phase_ column exists.

- Q: Spectrum controls don’t show up.
  - A: Spectrum is TIME-only. Ensure TIME data is loaded and the computed selections are not active.

- Q: Plots are slow or heavy.
  - A: Use Rolling Min-Max envelope (Settings) to reduce points; consider sectioning TIME data; hide legend or reduce opacity.

Comparison

- Q: Comparison data fails to load.
  - A: Load primary data first. Comparison data must include the same domain column (TIME or FREQ) and compatible column names.

- Q: Relative difference shows zeros or spikes.
  - A: Relative difference divides by the primary series magnitude; zeros in primary cause spikes. Inspect absolute difference for context.

ANSYS Export

- Q: ANSYS session fails to start.
  - A: Install and license ANSYS Mechanical. Ensure ansys-mechanical-core and related packages match the installed version.

- Q: Harmonic export yields only forces or only moments.
  - A: If R* or T* series are all zeros, corresponding load objects are deleted automatically.

- Q: Transient export is very large.
  - A: Data is partitioned into ~50k-row segments. Consider sectioning TIME data before export.

Environment

- Q: QtWebEngine errors.
  - A: Ensure PyQtWebEngine matches PyQt5 versions in requirements.txt.

- Q: Import errors for endaq modules.
  - A: Verify endaq is installed from requirements. Some corporate environments block wheels; ensure internet access or local wheel cache.

Logging and Diagnostics

- Run scripts/test_dt.py on TIME data to validate time step integrity.
- Temporarily add prints in controllers to inspect options flows if needed.















