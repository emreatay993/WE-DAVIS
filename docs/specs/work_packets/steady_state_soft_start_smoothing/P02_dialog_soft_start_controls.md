# P02 Dialog Soft-Start Controls

## Objective

Wire the new soft-start behavior into `SteadyStateTimeHistoryExportDialog` so preview and CSV export use the same smoothed frame and invalid ramp settings disable export.

## Preconditions

- `P00` is `PASS`.
- `P01` is `PASS` and its accepted helper commit is present in the Wave 2 base revision.

## Execution Dependencies

- `P01`

## Target Subsystems

- `app/ui/steady_state_time_history_export_dialog.py`
- `app/analysis/steady_state_time_history_export.py`
- `tests/test_steady_state_time_history_export.py`

## Conservative Write Scope

- `app/ui/steady_state_time_history_export_dialog.py`
- `tests/test_steady_state_time_history_export.py`
- `docs/specs/work_packets/steady_state_soft_start_smoothing/P02_dialog_soft_start_controls_WRAPUP.md`

## Required Behavior

- Add a `Soft Start` control group to the export dialog.
- Add checkbox text `Apply smooth start`, checked by default.
- Add a manually editable double spinbox for `Ramp cycles`, default `2.0`, step `0.5`.
- Apply smoothing in `_build_preview_frame` before unit conversion and header generation.
- Keep `_handle_export` using `_build_preview_frame` so preview and export remain identical.
- If enabled ramp cycles exceed total exported cycles, disable export and show the validation message through the existing preview error path.
- Include ramp duration in preview status when enabled, for example `Soft start: 2 cycles / 0.00285 s`.
- Disabled smoothing must leave the frame unsmoothed.
- Do not auto-shorten or rewrite the cycle count.

## Non-Goals

- Do not change the helper's mathematical contract unless a `P01` regression requires a scoped update to `tests/test_steady_state_time_history_export.py`.
- Do not update user/developer docs in this packet.
- Do not change full Tukey window behavior.

## Verification Commands

- `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`
- `.\venv\Scripts\python.exe -m unittest discover tests`

## Review Gate

- `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`

## Expected Artifacts

- `docs/specs/work_packets/steady_state_soft_start_smoothing/P02_dialog_soft_start_controls_WRAPUP.md`

## Acceptance Criteria

- The export dialog exposes the controls with the required defaults.
- Preview/export frame construction applies smoothing only when enabled.
- Invalid ramp cycles make preview/export fail with a clear message.
- Tests pass or the wrap-up records a concrete blocking failure.
- Changed files stay within the conservative write scope.

## Handoff Notes

- This packet owns any inherited regression anchor in `tests/test_steady_state_time_history_export.py` if dialog integration requires revising helper expectations.
- `P03` should document the final user-facing behavior from this packet.
