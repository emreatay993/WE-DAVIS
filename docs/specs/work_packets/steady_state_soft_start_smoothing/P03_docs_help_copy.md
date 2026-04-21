# P03 Docs And Help Copy

## Objective

Document the soft-start smoothing behavior, theory, caveats, and references in user-facing and developer-facing help surfaces.

## Preconditions

- `P00` is `PASS`.
- `P01` and `P02` are `PASS` and their accepted behavior is present in the Wave 3 base revision.

## Execution Dependencies

- `P02`

## Target Subsystems

- `app/ui/steady_state_cycle_estimator_dialog.py`
- `app/tooltips.py`
- `docs/UI-Guide.md`
- `docs/modules/analysis.md`
- `docs/modules/ui.md`

## Conservative Write Scope

- `app/ui/steady_state_cycle_estimator_dialog.py`
- `app/tooltips.py`
- `docs/UI-Guide.md`
- `docs/modules/analysis.md`
- `docs/modules/ui.md`
- `docs/specs/work_packets/steady_state_soft_start_smoothing/P03_docs_help_copy_WRAPUP.md`

## Required Behavior

- Explain why steady-state exported loads can create an artificial initial step when the transient model starts from zero state.
- Explain why this export uses a one-sided half-cosine ramp instead of the existing full Tukey window.
- Include the resonance decay estimate `N = ln(1 / r) / (2*pi*zeta)`.
- Include the example `zeta = 0.02`, `r = 0.01`, `36.65`, rounded to `37` cycles.
- State that smoothing helps load introduction/convergence but is not a guaranteed cycle-count reducer.
- Reference the ANSYS and SciPy documents named in the implementation plan.
- Keep tooltip copy short and reserve long theory for help/docs surfaces.

## Non-Goals

- Do not change analysis or dialog behavior in this packet.
- Do not add CSV metadata rows.
- Do not alter the legacy v0 GUI unless a direct import or shipped workflow is found during packet work.

## Verification Commands

- `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`
- `.\venv\Scripts\python.exe -m unittest discover tests`

## Review Gate

- `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`

## Expected Artifacts

- `docs/specs/work_packets/steady_state_soft_start_smoothing/P03_docs_help_copy_WRAPUP.md`

## Acceptance Criteria

- Docs/help copy matches final implementation behavior from `P02`.
- Required formula, example, and caveat are present.
- Required references are present in a suitable help/docs location.
- Verification commands pass or the wrap-up records a concrete blocking failure.
- Changed files stay within the conservative write scope.

## Handoff Notes

- Keep docs concise and implementation-specific. Avoid broad refactors of the docs structure.
