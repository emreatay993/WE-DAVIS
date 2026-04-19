# P05 Export Unit Mode

## Objective
- Replace fixed export scaling with explicit source/display conversion and validate ANSYS export eligibility against the parsed quantity-family model.

## Preconditions
- `P00` is `PASS`.
- `P01` is `PASS`.
- `P02` is `PASS`.
- `P03` is `PASS`.
- `P04` is `PASS`.

## Execution Dependencies
- `P04`

## Target Subsystems
- `app/controllers/action_handler.py`
- `app/analysis/ansys_exporter.py`
- `tests/test_export_unit_mode.py`

## Conservative Write Scope
- `app/controllers/action_handler.py`
- `app/analysis/ansys_exporter.py`
- `tests/test_export_unit_mode.py`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode_WRAPUP.md`

## Required Behavior
- Replace the hard-coded `* 1000` path with explicit use of the unit conversion service.
- Honor the global export mode:
  - `Source Units`
  - `Display Units`
- Keep CSV extraction and time-domain reconstruction export aligned with the selected export mode where units are known.
- Permit ANSYS export only when the selected data resolves to load-compatible quantity families and units for the existing exporter assumptions.
- Fail unsupported export cases with a clear user-facing message instead of silently guessing a scale factor.
- Update filenames and status messages so they no longer claim data was simply multiplied by 1000.

## Non-goals
- Broad redesign of `AnsysExporter`.
- Arbitrary support for every possible quantity family in ANSYS templates.
- Moving packet docs to the completed folder.

## Verification Commands
- `$env:QT_QPA_PLATFORM='offscreen'; .\venv\Scripts\python.exe -m unittest tests.test_export_unit_mode`

## Review Gate
- `.\venv\Scripts\python.exe -m compileall app\controllers\action_handler.py app\analysis\ansys_exporter.py`

## Expected Artifacts
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode_WRAPUP.md`
- `tests/test_export_unit_mode.py`

## Acceptance Criteria
- Export preprocessing no longer contains a hard-coded multiply-by-1000 branch.
- Source/display export mode is honored for supported datasets.
- Unsupported quantity families are rejected clearly before ANSYS export starts.

## Handoff Notes
- `P06` should document the new export behavior and remove any docs that describe fixed scaling.
- If ANSYS validation relies on a helper split from `ActionHandler`, keep the helper inside packet scope and test it without requiring Ansys installation.
