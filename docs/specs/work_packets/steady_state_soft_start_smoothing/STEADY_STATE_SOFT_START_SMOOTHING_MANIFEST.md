# Steady-State Soft-Start Smoothing Work Packets

## Scope Baseline

Implement the plan in `IMPLEMENTATION_PLANS/in_progress/Steady-State Export Soft-Start Smoothing.md`.

The feature adds an enabled-by-default, one-sided half-cosine soft start to steady-state time-history CSV export. The existing steady-state cycle estimator remains conservative and must not auto-reduce the exported cycle count.

## Requirement Anchors

- Analysis helper: `app/analysis/steady_state_time_history_export.py`
- Export dialog: `app/ui/steady_state_time_history_export_dialog.py`
- Analysis tests: `tests/test_steady_state_time_history_export.py`
- User/developer docs and help copy:
  - `app/ui/steady_state_cycle_estimator_dialog.py`
  - `app/tooltips.py`
  - `docs/UI-Guide.md`
  - `docs/modules/analysis.md`
  - `docs/modules/ui.md`

## Locked Defaults

- Default soft-start enabled: yes.
- Default ramp cycles: `2.0`.
- Ramp control step: `0.5`.
- Smoothing envelope: `0.5 * (1 - cos(pi * t / T_ramp))` for `0 <= t < T_ramp`, then `1.0`.
- Smoothing applies to load/data columns only, never the time column.
- Smoothing runs before unit conversion and CSV header generation.
- Smoothing does not change the estimator's recommended cycle count.
- No CSV metadata rows are added.

## Packet Order

- `P00` bootstrap packet docs.
- `P01` pure analysis helper plus unit tests.
- `P02` export dialog controls, validation, preview status, and helper integration.
- `P03` docs/help copy and references.

## Branch Labels

- `P01`: `codex/steady_state_soft_start_smoothing/p01-analysis-helper-tests`
- `P02`: `codex/steady_state_soft_start_smoothing/p02-dialog-soft-start-controls`
- `P03`: `codex/steady_state_soft_start_smoothing/p03-docs-help-copy`

## Execution Waves

### Wave 1

- `P01`

### Wave 2

- `P02`

### Wave 3

- `P03`

## Handoff Artifacts

- `docs/specs/work_packets/steady_state_soft_start_smoothing/STEADY_STATE_SOFT_START_SMOOTHING_STATUS.md`
- `docs/specs/work_packets/steady_state_soft_start_smoothing/P01_analysis_helper_tests_WRAPUP.md`
- `docs/specs/work_packets/steady_state_soft_start_smoothing/P02_dialog_soft_start_controls_WRAPUP.md`
- `docs/specs/work_packets/steady_state_soft_start_smoothing/P03_docs_help_copy_WRAPUP.md`

## Executor Notes

- The target merge branch must be captured before Wave 1 starts.
- Packet workers must use dedicated worktrees and packet branches.
- Packet workers must not edit the shared status ledger.
- The executor owns status updates and final `PASS` / `FAIL` decisions.
- Packet verification commands assume the executor prepares a packet-worktree `venv` helper pointing at the main checkout's `.venv`.
