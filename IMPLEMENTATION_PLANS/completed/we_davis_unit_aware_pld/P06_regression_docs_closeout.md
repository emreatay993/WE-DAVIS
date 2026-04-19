# P06 Regression Docs Closeout

## Objective
- Close the feature with regression coverage, docs refresh, and explicit handoff guidance for future `.log` work.

## Preconditions
- `P00` is `PASS`.
- `P01` is `PASS`.
- `P02` is `PASS`.
- `P03` is `PASS`.
- `P04` is `PASS`.
- `P05` is `PASS`.

## Execution Dependencies
- `P05`

## Target Subsystems
- `app/README.md`
- `docs/README.md`
- `docs/modules/analysis.md`
- `tests/test_unit_contract.py`
- `tests/test_data_manager_unit_metadata.py`
- `tests/test_settings_unit_controls.py`
- `tests/test_plot_unit_projection.py`
- `tests/test_export_unit_mode.py`

## Conservative Write Scope
- `app/README.md`
- `docs/README.md`
- `docs/modules/analysis.md`
- `tests/test_unit_contract.py`
- `tests/test_data_manager_unit_metadata.py`
- `tests/test_settings_unit_controls.py`
- `tests/test_plot_unit_projection.py`
- `tests/test_export_unit_mode.py`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout_WRAPUP.md`

## Required Behavior
- Audit the implementation against the locked defaults in the manifest.
- Add or refine regression coverage only where gaps remain after `P01` through `P05`.
- Refresh user/developer docs to describe:
  - automatic unit detection from `max.pld`,
  - display-unit controls in `SettingsTab`,
  - export mode behavior,
  - the fact that `.log` input support is still deferred.
- Remove stale wording that claims converted exports are always `multiplied by 1000`.

## Non-goals
- New feature scope beyond the approved unit-awareness plan.
- `.log` loader implementation.
- Executor-side branch merge or cleanup.

## Verification Commands
- `$env:QT_QPA_PLATFORM='offscreen'; .\venv\Scripts\python.exe -m unittest tests.test_unit_contract tests.test_data_manager_unit_metadata tests.test_settings_unit_controls tests.test_plot_unit_projection tests.test_export_unit_mode`
- `.\venv\Scripts\python.exe -m compileall app`

## Review Gate
- `$env:QT_QPA_PLATFORM='offscreen'; .\venv\Scripts\python.exe -m unittest tests.test_data_manager_unit_metadata tests.test_plot_unit_projection tests.test_export_unit_mode`

## Expected Artifacts
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout_WRAPUP.md`

## Acceptance Criteria
- Documentation matches the implemented feature behavior.
- Targeted regression coverage exists for loader metadata, unit projection, and export mode behavior.
- The packet set is ready for executor completion and later post-merge archival into `IMPLEMENTATION_PLANS/completed`.

## Handoff Notes
- After all packets are `PASS` and the user confirms the merge succeeded, move `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld` to `IMPLEMENTATION_PLANS/completed/we_davis_unit_aware_pld`.
- Keep the completed packet-set contents intact during that move, including wrap-ups and the final status ledger.
