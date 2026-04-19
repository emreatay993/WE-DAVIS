# P02 Loader Unit Metadata

## Objective
- Extend the `.pld` loading pipeline so `DataManager` preserves `UNIT` metadata from `max.pld`, aligns it with the final DataFrame columns, and emits unit context with both primary and comparison data.

## Preconditions
- `P00` is `PASS`.
- `P01` is `PASS`.

## Execution Dependencies
- `P01`

## Target Subsystems
- `app/data_manager.py`
- `app/main_window.py`
- `tests/test_data_manager_unit_metadata.py`

## Conservative Write Scope
- `app/data_manager.py`
- `app/main_window.py`
- `tests/test_data_manager_unit_metadata.py`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P02_loader_unit_metadata_WRAPUP.md`

## Required Behavior
- Update header parsing so `max.pld` contributes both label and unit metadata.
- Align unit metadata to the final loaded columns, including:
  - ordinary data columns,
  - phase columns synthesized for FREQ datasets,
  - domain columns such as `TIME` and `FREQ`,
  - fallback handling for `Extra_Column_*` columns.
- Emit unit context with:
  - `dataLoaded(df, data_domain, folder_path, unit_context)`
  - `comparisonDataLoaded(df_compare, unit_context_compare)`
- Preserve current domain detection, column naming, multi-folder concatenation, and `DataFolder` behavior.
- Keep `.log` input out of scope.

## Non-goals
- Adding unit selectors to the UI.
- Converting plotted values.
- Changing export behavior.

## Verification Commands
- `.\venv\Scripts\python.exe -m unittest tests.test_data_manager_unit_metadata`

## Review Gate
- `.\venv\Scripts\python.exe -m unittest tests.test_data_manager_unit_metadata.DataManagerUnitMetadataTests`

## Expected Artifacts
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P02_loader_unit_metadata_WRAPUP.md`
- `tests/test_data_manager_unit_metadata.py`

## Acceptance Criteria
- Sample `max.pld` files produce unit context with no loss of existing column labeling.
- Primary and comparison loads both surface unit metadata to consumers.
- Existing sample data still loads with the correct `TIME` or `FREQ` domain.

## Handoff Notes
- `P03` will consume the emitted unit context and should not re-derive source units from the files.
- If slot signatures change in `MainWindow`, keep the adoption narrow and store raw unit context there for later packets.
