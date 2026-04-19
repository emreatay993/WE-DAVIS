# WE-DAVIS Unit-Aware `.pld` Support

## Summary
- Make WE-DAVIS unit-aware for `.pld` inputs by reading source units from the `UNIT` column in `max.pld`, keeping raw numeric data in source units, and projecting converted values in-app for plotting, comparison, and optional export. The implementation will treat `T*` and `R*` only as translational/rotational grouping hints for existing tabs; quantity family and conversion compatibility will come from parsed unit strings. The UI will expose global unit settings in `SettingsTab`, with one display-unit selector per detected quantity family and an export toggle between source units and display units.

## Key Changes
- Extend the loader so `DataManager` parses and preserves channel-unit metadata from `max.pld` instead of discarding the `UNIT` column.
- Introduce a reusable unit model and conversion service that normalizes unit strings, infers quantity families, exposes compatible display units, and converts DataFrame projections without mutating source data.
- Update `MainWindow`, `PlotController`, and `Plotter` so all tabs render active display units in values, axis labels, and hover content.
- Replace the hard-coded `* 1000` export path in `ActionHandler` with explicit conversion based on the new export toggle.
- Keep unsupported or unknown units in source units only; do not guess conversions.

## Public Interface Changes
- `DataManager.dataLoaded` changes from `(pd.DataFrame, str, str)` to `(pd.DataFrame, str, str, object)` where the fourth value is the loaded unit context.
- `DataManager.comparisonDataLoaded` changes from `(pd.DataFrame)` to `(pd.DataFrame, object)` so comparison data carries its own unit metadata.
- `SettingsTab` gains a new global Units section with:
  - detected source-unit summary,
  - one display-unit selector per detected quantity family,
  - export-units selector with `Source Units` and `Display Units`.
- Plot labels and hover text become unit-aware and may show `Mixed Units` when one grouped chart contains traces from different quantity families.

## Execution Tasks

### T01 Define the unit contract
- Goal: establish the canonical in-memory model for source units, quantity families, compatible display units, and export mode.
- Preconditions: current `.pld` loader and plot/update flow are unchanged baseline.
- Conservative write scope: `app/data_manager.py`, new unit module under `app/` or `app/analysis/`, signal consumers in `app/main_window.py` only as needed for contract adoption.
- Deliverables:
  - unit normalization table and quantity-family mapping,
  - `UnitContext` structure for per-column metadata,
  - conversion API for projecting one series/DataFrame to a requested display unit,
  - explicit handling for domain columns (`TIME`, `FREQ`, `Phase_*`) and unknown units.
- Verification:
  - unit-focused tests for normalization and family inference,
  - smoke checks against sample `max.pld` files proving `kN` and `kN*m` are captured separately.
- Non-goals:
  - UI wiring,
  - plot updates,
  - export behavior changes.
- Packetization notes: likely `P01`; keep isolated from UI so later tasks can depend on a stable contract.

### T02 Extend `.pld` loading to preserve unit metadata
- Goal: make `DataManager` parse `max.pld` into both channel labels and unit metadata while preserving existing DataFrame column naming behavior.
- Preconditions: T01 unit contract is fixed.
- Conservative write scope: `app/data_manager.py`, sample-data or loader-facing tests only.
- Deliverables:
  - header parsing that captures `Interface Label` plus `UNIT`,
  - mapping from final DataFrame columns to source-unit metadata,
  - updated `dataLoaded` and `comparisonDataLoaded` emissions carrying unit context,
  - compatibility handling for extra unnamed columns and missing or blank unit entries.
- Verification:
  - loader tests for both bundled sample folders,
  - manual sanity check that primary and comparison loads still produce the same columns and domain detection as before.
- Non-goals:
  - changing any tab controls,
  - converting plotted values,
  - changing export files.
- Packetization notes: likely `P02`; depends on `P01` and should land before UI or plot work.

### T03 Add global unit controls and application state
- Goal: expose unit-aware settings in the UI and store active display and export choices centrally.
- Preconditions: T02 emits usable unit context from primary and comparison loads.
- Conservative write scope: `app/ui/tab_settings.py`, `app/main_window.py`, minimal signal wiring in `app/controllers/plot_controller.py`.
- Deliverables:
  - Units section in `SettingsTab`,
  - dynamic selectors for detected quantity families only,
  - export mode selector,
  - main-window state for raw primary data, raw comparison data, loaded unit contexts, and active display-unit selections,
  - refresh trigger when a unit selector changes.
- Verification:
  - manual load of sample `.pld` data showing detected unit families and selectors,
  - signal-level check that changing a unit selector triggers full plot refresh without reloading data.
- Non-goals:
  - conversion logic implementation,
  - export rewrite,
  - documentation updates.
- Packetization notes: likely `P03`; narrow enough to implement after loader work without touching export code.

### T04 Apply conversion to plotting and comparison paths
- Goal: make all in-app plots and comparisons render in the selected display units while keeping raw data untouched.
- Preconditions: T01 through T03 complete and active unit selections available from `MainWindow`.
- Conservative write scope: `app/controllers/plot_controller.py`, `app/plotting/plotter.py`, only minimal tab code if labels need local updates.
- Deliverables:
  - converted plot projections for `Single Data`, `Compare Data`, `Interface Data`, `Part Loads`, `Compare Part Loads`, and `Time Domain Representation`,
  - unit-aware axis labels and hover text,
  - correct unit handling for computed metrics (`Time Step`, `Sampling Rate`, frequency, phase),
  - `Mixed Units` y-axis labeling when a grouped chart contains traces from multiple quantity families.
- Verification:
  - manual smoke across all tabs with sample frequency and time-domain data,
  - comparison verification that absolute differences follow display units and percent differences remain unchanged,
  - regression check that phase plots still work for FREQ data.
- Non-goals:
  - export behavior,
  - ANSYS-specific validation changes,
  - `.log` support.
- Packetization notes: likely `P04`; keep all conversion-on-read behavior here so export can adopt the same service later.

### T05 Replace hard-coded export scaling with explicit unit conversion
- Goal: make CSV and ANSYS export use the selected export mode instead of fixed multiplication by 1000.
- Preconditions: plotting conversion path is stable and the unit service can project source or display units deterministically.
- Conservative write scope: `app/controllers/action_handler.py`, `app/analysis/ansys_exporter.py` only if unit validation or labels require it.
- Deliverables:
  - export path honoring `Source Units` vs `Display Units`,
  - removal of hard-coded `* 1000` CSV generation,
  - ANSYS export validation that allows only load-compatible families and fails clearly on unsupported families,
  - filenames and messages updated to reflect export mode rather than `multiplied by 1000`.
- Verification:
  - manual CSV export in both modes,
  - regression check that ANSYS harmonic and transient templates still generate for supported load-unit datasets,
  - validation check that unsupported quantity families are blocked with a clear message.
- Non-goals:
  - redesigning ANSYS templates for arbitrary physical quantities,
  - new export UI beyond the global mode selector.
- Packetization notes: likely `P05`; keep after plot adoption because it reuses the same conversion contract.

### T06 Closeout, audit, and docs refresh
- Goal: finish the change with regression coverage and concise repo docs updates.
- Preconditions: T01 through T05 complete.
- Conservative write scope: tests, targeted docs such as `app/README.md`, `docs/README.md`, and module docs already describing units and export behavior.
- Deliverables:
  - regression tests covering loader metadata, conversion behavior, and export mode,
  - doc updates removing the fixed `multiplied by 1000` assumption,
  - explicit note that `.log` input remains out of scope for this pass.
- Verification:
  - run the targeted test suite,
  - manual end-to-end smoke on both bundled sample datasets.
- Non-goals:
  - packet manifest authoring,
  - broader refactoring of unrelated UI or docs.
- Packetization notes: likely `P06`; safe as a final audit and closeout task and should not be merged backward unless the implementation remains very small.

## Work Packet Conversion Map
1. `P00 Bootstrap`: packet scaffolding, task ledger, and tracking docs only if this plan is later packetized.
2. `P01 Unit Contract`: derived from `T01`.
3. `P02 Loader Metadata Adoption`: derived from `T02`.
4. `P03 Settings and App State`: derived from `T03`.
5. `P04 Plot and Comparison Conversion`: derived from `T04`.
6. `P05 Export Conversion and Validation`: derived from `T05`.
7. `P06 Regression and Docs Closeout`: derived from `T06`.
8. No planned task merges. The contract, loader, UI state, plot adoption, and export adoption each cross different verification boundaries and should stay separate.

## Test Plan
- Unit tests for unit normalization, quantity-family inference, compatibility lookup, and conversion factors.
- Loader tests proving `max.pld` unit metadata survives parsing for both primary and comparison datasets.
- Manual smoke tests for:
  - frequency-domain sample load,
  - time-domain sample load,
  - changing display units and seeing all relevant tabs refresh,
  - comparison plots and absolute and relative difference correctness,
  - export in both source and display modes.
- Regression checks that:
  - multi-folder loading still works,
  - phase columns remain aligned for FREQ data,
  - unsupported units remain source-only and do not crash plotting.

## Assumptions
- This pass covers `.pld` input only; `.log` support is intentionally deferred.
- Source units are always auto-detected from `max.pld`; there is no manual source-unit override in v1.
- Quantity family is inferred from the unit string, not from `T*` or `R*`.
- `T*` and `R*` continue to control only existing translational and rotational grouping in the current tabs.
- Unknown or unsupported units remain displayable and exportable only in source units.
- The unit selectors are generated from the currently loaded dataset’s detected families rather than a fixed global catalog.
