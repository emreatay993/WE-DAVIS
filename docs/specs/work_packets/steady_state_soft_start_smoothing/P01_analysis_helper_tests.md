# P01 Analysis Helper And Tests

## Objective

Add `apply_half_cosine_soft_start(frame, ramp_cycles, frequency_hz, time_column="Time")` and focused unit coverage for the steady-state export data boundary.

## Preconditions

- `P00` is `PASS`.
- Start from the captured Wave 1 base revision.

## Execution Dependencies

- `P00`

## Target Subsystems

- `app/analysis/steady_state_time_history_export.py`
- `tests/test_steady_state_time_history_export.py`

## Conservative Write Scope

- `app/analysis/steady_state_time_history_export.py`
- `tests/test_steady_state_time_history_export.py`
- `docs/specs/work_packets/steady_state_soft_start_smoothing/P01_analysis_helper_tests_WRAPUP.md`

## Required Behavior

- Add a pure helper named `apply_half_cosine_soft_start`.
- Preserve row count, index, column order, time step, inclusive endpoint, and CSV schema.
- Apply the multiplier to every non-time column only.
- Validate `ramp_cycles >= 0`.
- Validate `frequency_hz > 0`.
- Validate `ramp_cycles <= total exported cycles`, where total cycles come from the final time and frequency.
- Return a defensive copy even when `ramp_cycles == 0`.
- Do not alter existing full Tukey window behavior.

## Non-Goals

- Do not add UI controls or dialog validation in this packet.
- Do not update docs/help copy in this packet.
- Do not change estimator math or cycle-count defaults.

## Verification Commands

- `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`
- `.\venv\Scripts\python.exe -m unittest discover tests`

## Review Gate

- `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`

## Expected Artifacts

- `docs/specs/work_packets/steady_state_soft_start_smoothing/P01_analysis_helper_tests_WRAPUP.md`

## Acceptance Criteria

- Unit tests cover no-op ramp behavior, first-row zeroing, ramp-end multiplier reaching `1.0`, unchanged `Time`, unit conversion/header compatibility after smoothing, and invalid negative/nonpositive/too-long inputs.
- Verification commands pass or the wrap-up records a concrete blocking failure.
- Changed files stay within the conservative write scope.

## Handoff Notes

- `P02` depends on this helper and may rely on the test file as the canonical regression anchor for smoothing semantics.
