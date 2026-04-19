# P04 Plot Unit Projection

## Objective
- Apply unit conversion to plotting and comparison flows so the UI renders active display units while raw data remains unchanged.

## Preconditions
- `P00` is `PASS`.
- `P01` is `PASS`.
- `P02` is `PASS`.
- `P03` is `PASS`.

## Execution Dependencies
- `P03`

## Target Subsystems
- `app/controllers/plot_controller.py`
- `app/plotting/plotter.py`
- `tests/test_plot_unit_projection.py`

## Conservative Write Scope
- `app/controllers/plot_controller.py`
- `app/plotting/plotter.py`
- `tests/test_plot_unit_projection.py`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P04_plot_unit_projection_WRAPUP.md`

## Required Behavior
- Use the unit subsystem to project converted data for:
  - `Single Data`,
  - `Compare Data`,
  - `Interface Data`,
  - `Part Loads`,
  - `Compare Part Loads`,
  - `Time Domain Representation`,
  - computed metrics such as `Time Step` and `Sampling Rate`.
- Update axis labels and hover text to reflect active display units.
- When grouped traces on one plot span different quantity families, keep per-trace values correct and use a `Mixed Units` y-axis label.
- Keep percent difference calculations unit-invariant while absolute differences follow active display units.
- Preserve existing phase-plot behavior for FREQ data.

## Non-goals
- Export conversion.
- ANSYS validation changes.
- New per-tab unit widgets.

## Verification Commands
- `$env:QT_QPA_PLATFORM='offscreen'; .\venv\Scripts\python.exe -m unittest tests.test_plot_unit_projection`

## Review Gate
- `.\venv\Scripts\python.exe -m unittest tests.test_plot_unit_projection.PlotUnitProjectionSmokeTests`

## Expected Artifacts
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P04_plot_unit_projection_WRAPUP.md`
- `tests/test_plot_unit_projection.py`

## Acceptance Criteria
- Converted plotting works for both bundled sample datasets.
- Absolute-difference plots change with display unit selection while relative-difference plots remain stable.
- Hover text and axis labels reflect the active display units without breaking existing plot generation.

## Handoff Notes
- `P05` should reuse the same conversion entry points for export preprocessing instead of duplicating numeric scaling logic.
- If `P04` must extend the unit subsystem for a plotting-specific edge case, keep those changes in `app/units/**` minimal and documented in the wrap-up.
