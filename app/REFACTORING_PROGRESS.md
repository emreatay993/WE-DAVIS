# Refactoring Progress and Opportunities

## Current State

- Core responsibilities are separated across `DataManager`, `MainWindow`,
  controllers, analysis helpers, plotting, UI widgets, and unit services.
- Automated `unittest` coverage exists under `tests/` for unit contracts, PLD
  metadata loading, plotting unit projection, settings unit controls, export
  unit modes, and steady-state time-history export helpers.
- `utils/helpers.py` now contains shared PLD label parsing helpers used by
  controllers and the main window.
- Documentation covers architecture, file inventory, data/signals, setup,
  settings, and module references.

## Low-Hanging Improvements

1. **Graceful Initial Cancel**
   `DataManager.load_data_from_directory()` still calls `sys.exit(1)` when the
   first startup folder dialog is canceled. Replace it with a soft failure path.
2. **Background Loading**
   Large PLD loads and expensive plot rebuilds run synchronously on the UI
   thread. Move ingestion and long plot operations toward worker threads or
   `QtConcurrent`.
3. **Configurable File Patterns**
   `full.pld` and `max.pld` suffixes are hard-coded. Centralize them if
   alternate export naming becomes common.

## Medium-Term Targets

1. **Plot Reuse and Caching**
   Cache expensive intermediate frames/figures by DataFrame identity plus tab
   settings, especially for spectrum and large multi-folder plots.
2. **Comparison Alignment**
   Comparison logic assumes compatible shapes/indexes. Add explicit alignment
   policies for diverging sample counts or time/frequency grids.
3. **Processing Pipeline API**
   Sectioning, filtering, Tukey, and future metrics could move into a composed
   processing pipeline to keep controller methods smaller.

## Long-Term Considerations

1. **Async ANSYS Export Feedback**
   ANSYS template generation can be slow. Add progress and cancellation support
   around exporter calls.
2. **Export Strategy Interfaces**
   `AnsysExporter` is tightly coupled to one downstream tool. A strategy
   interface would make Abaqus/custom CSV templates easier to add.
3. **Headless UI Signal Tests**
   Unit tests cover services and contracts. Add targeted Qt signal tests for tab
   wiring and selector behavior when the test environment supports it.
