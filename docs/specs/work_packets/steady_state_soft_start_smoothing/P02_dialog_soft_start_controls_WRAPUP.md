# P02 Dialog Soft-Start Controls Wrap-Up

## Implementation Summary

- Packet: `P02`
- Branch Label: `codex/steady_state_soft_start_smoothing/p02-dialog-soft-start-controls`
- Commit Owner: `worker`
- Commit SHA: `c19930ca1cc4c54906bbb6904955329554fbabb8`
- Changed Files: `app/ui/steady_state_time_history_export_dialog.py`, `tests/test_steady_state_time_history_export.py`, `docs/specs/work_packets/steady_state_soft_start_smoothing/P02_dialog_soft_start_controls_WRAPUP.md`
- Artifacts Produced: `docs/specs/work_packets/steady_state_soft_start_smoothing/P02_dialog_soft_start_controls_WRAPUP.md`

Added a `Soft Start` group to `SteadyStateTimeHistoryExportDialog` with `Apply smooth start` checked by default and an editable `Ramp cycles` double spinbox defaulting to `2.0` with `0.5` increments.

Wired `_build_preview_frame` to apply `apply_half_cosine_soft_start` before unit conversion and CSV header generation when smoothing is enabled. `_handle_export` continues to call `_build_preview_frame`, so preview and export remain on the same frame-building path. Invalid enabled ramp lengths flow through the existing preview error handling, disabling export and showing the helper validation message without changing the user-entered cycle count.

Added dialog-level tests for enabled smoothing, disabled smoothing with an oversized ramp, invalid-ramp validation, preview error disabling, and preview status ramp-duration text.

## Verification

- PASS: `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`
  - Ran 13 tests.
  - Result: OK.
- FAIL: `.\venv\Scripts\python.exe -m unittest discover tests`
  - The process exited with code `1` before a unittest summary.
  - Verbose output reached `test_settings_unit_controls.PlotControllerSettingsRefreshTests.test_update_all_plots_from_settings_uses_existing_settings_refresh_path` after earlier non-P02 modules, then the interpreter terminated without a Python assertion failure or traceback.
  - `.\venv\Scripts\python.exe -X faulthandler -m unittest discover tests -v` stopped at the same point and did not emit a Python traceback.
  - A subset run excluding the P02 test module, `test_data_manager_unit_metadata test_export_unit_mode test_plot_unit_projection test_settings_unit_controls`, also stopped at the same point with exit code `1`, so this is classified as the existing repository-wide discovery blocker rather than a P02-caused failure.
- PASS: Review Gate, `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`
  - Ran 13 tests.
  - Result: OK.

- Final Verification Verdict: PASS

## Manual Test Directives

Ready for manual testing.

- Prerequisite: Launch the application from this packet branch with a plotted steady-state one-cycle dataset and a selected excitation frequency so the steady-state time-history export dialog can open.
- Control defaults: Open the export dialog and confirm the `Soft Start` group is visible, `Apply smooth start` is checked, and `Ramp cycles` shows `2.0`. Step the ramp control once and confirm it changes by `0.5`; type a value manually and confirm the preview refreshes.
- Enabled smoothing: Use an exported cycle count at least as large as the ramp cycles. Confirm the preview status includes text like `Soft start: 2 cycles / ... s`, then export the CSV and verify the first data samples are ramped up from zero while the time column remains unchanged.
- Disabled smoothing: Clear `Apply smooth start` and confirm the preview status no longer includes soft-start text. Export and verify the load/data columns begin with the unsmoothed one-cycle values.
- Invalid ramp validation: Set `Cycles` to `1` and `Ramp cycles` to `2.0` while smoothing is enabled. Expected result: the preview shows a clear `total exported cycles` validation message, `Export CSV` is disabled, and the cycle count is not auto-shortened.

## Residual Risks

- Full repository unittest discovery still exits early in the known broad discovery path before reaching the P02 test module. Packet-owned tests and the review gate pass.
- Automated tests exercise dialog frame-building and preview error handling without constructing the full Qt WebEngine preview widget; the manual GUI smoke test above should be used to confirm the visible controls and preview rendering.

## Ready for Integration

- Yes: P02 implementation and packet-owned tests are complete, the review gate passes, and the repository-wide discovery failure is isolated outside the P02-owned module path. Carry the broad discovery blocker forward as an existing repository/environment risk.
