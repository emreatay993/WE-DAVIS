# P03 Settings Unit Controls

## Objective
- Add global unit controls to `SettingsTab` and store active display/export unit selections centrally in `MainWindow`.

## Preconditions
- `P00` is `PASS`.
- `P01` is `PASS`.
- `P02` is `PASS`.

## Execution Dependencies
- `P02`

## Target Subsystems
- `app/ui/tab_settings.py`
- `app/main_window.py`
- `app/controllers/plot_controller.py`
- `tests/test_settings_unit_controls.py`

## Conservative Write Scope
- `app/ui/tab_settings.py`
- `app/main_window.py`
- `app/controllers/plot_controller.py`
- `tests/test_settings_unit_controls.py`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P03_settings_unit_controls_WRAPUP.md`

## Required Behavior
- Add a Units section to `SettingsTab`.
- Render one display-unit selector per detected quantity family from the currently loaded dataset.
- Add an export-unit selector with exactly:
  - `Source Units`
  - `Display Units`
- Surface a read-only summary of detected source units or detected quantity families.
- Store raw primary/comparison frames and active unit selections on `MainWindow` so later packets can project converted views without overwriting canonical raw data.
- Wire unit-selector changes into the existing plot refresh path without forcing a data reload.
- Keep the control placement global in `SettingsTab`, not duplicated across tabs.

## Non-goals
- Applying numeric conversions to plots.
- Rewriting export logic.
- Refreshing documentation.

## Verification Commands
- `$env:QT_QPA_PLATFORM='offscreen'; .\venv\Scripts\python.exe -m unittest tests.test_settings_unit_controls`

## Review Gate
- `.\venv\Scripts\python.exe -m compileall app\ui\tab_settings.py app\main_window.py app\controllers\plot_controller.py`

## Expected Artifacts
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P03_settings_unit_controls_WRAPUP.md`
- `tests/test_settings_unit_controls.py`

## Acceptance Criteria
- Loading sample data shows unit controls in `SettingsTab` without breaking current settings widgets.
- Unit control changes trigger the existing update path instead of bespoke one-off refresh code.
- Main-window state preserves raw data and selected display/export units separately.

## Handoff Notes
- `P04` should consume the selected units from `MainWindow` or a thin accessor layer, not from direct widget lookups scattered across plotting code.
- If a later packet needs a tiny helper method in `tab_settings.py`, keep it local instead of introducing a second settings owner.
