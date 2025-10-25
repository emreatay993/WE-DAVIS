# Refactoring Progress & Opportunities

## Current State
- Core modules (`data_manager`, `main_window`, `controllers`, `analysis`, `plotting`, `ui`) are functionally organized but lack automated tests.
- Documentation now covers architecture, onboarding, and operations, reducing tribal knowledge risk.
- The plotting pipeline centralizes logic in `PlotController`, minimizing duplication across tabs.

## Low-Hanging Improvements
1. **Graceful Initial Cancel**  
   `DataManager.load_data_from_directory()` calls `sys.exit(1)` when the first dialog is canceled. Replace with a user-friendly prompt so accidental cancels do not close the app.
2. **Utility Consolidation**  
   Several regex helpers live inline within controllers. Move them to `utils/helpers.py` (currently empty) to improve reuse and testability.
3. **Configurable File Patterns**  
   Hard-coded `full.pld` and `max.pld` suffixes could move to a config module, enabling support for alternate data exports without code changes.

## Medium-Term Targets
1. **Plot Reuse & Caching**  
   Recompute-heavy tabs (especially spectrum plots) rebuild entire DataFrames on each interaction. Introduce memoization keyed by DataFrame hash + tab options to improve responsiveness on large datasets.
2. **Comparison Workflow**  
   The comparison feature recalculates differences column by column. Refactor into vectorized utilities with clearer error handling and support for time alignment (if sample counts diverge).
3. **Windowing & Filtering API**  
   Expand `analysis/data_processing.py` into a mini pipeline builder (compose sectioning, filtering, averaging). This will simplify future feature requests (e.g., RMS, peak hold).

## Long-Term Considerations
1. **Automated Tests**  
   Introduce headless tests for `DataManager` (using fixture `.pld` files) and unit tests for data-processing helpers. Consider Qt Test or pytest-qt for UI signal coverage.
2. **Plugin-Based Exports**  
   `AnsysExporter` is tightly coupled to one downstream tool. Abstract exports into a strategy pattern so new formats (e.g., Abaqus, CSV templates) can plug in without modifying the tab.
3. **Asynchronous Loading**  
   Large datasets block the UI thread. Evaluate worker threads or Qt's `QtConcurrent` for background ingestion with progress feedback.

Documenting these opportunities clarifies where to focus future engineering cycles once feature development resumes.
