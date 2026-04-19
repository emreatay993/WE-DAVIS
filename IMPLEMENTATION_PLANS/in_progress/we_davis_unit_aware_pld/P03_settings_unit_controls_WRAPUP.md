# Implementation Summary

- Packet: P03 Settings Unit Controls
- Branch Label: codex/we-davis-unit-aware-pld/p03-settings-unit-controls
- Commit Owner: worker
- Commit SHA: 8480cab4422d92ebb2a22c5f3f9fe69f99d4ef21
- Changed Files: app/controllers/plot_controller.py, app/main_window.py, app/ui/tab_settings.py, tests/test_settings_unit_controls.py, IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P03_settings_unit_controls_WRAPUP.md
- Artifacts Produced: IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P03_settings_unit_controls_WRAPUP.md, tests/test_settings_unit_controls.py

- Added a global `Units` section to `SettingsTab` with one display-unit selector per detected quantity family, an export-unit selector limited to `Source Units` and `Display Units`, and a read-only summary of detected source units.
- Moved unit-selection ownership into `MainWindow` by preserving raw primary/comparison frames and raw unit contexts separately from the active display/export selections and current display-oriented unit contexts.
- Routed unit selector changes through the existing `settings_changed -> PlotController.update_all_plots_from_settings()` flow so unit preference changes reuse the current plot refresh path without forcing a reload.
- Added packet-local unit tests that cover settings-tab rendering, signal propagation, centralized unit state updates, and the settings refresh integration point.

# Verification

- PASS: `$env:QT_QPA_PLATFORM='offscreen'; .\venv\Scripts\python.exe -m unittest tests.test_settings_unit_controls`
- PASS: `.\venv\Scripts\python.exe -m compileall app\ui\tab_settings.py app\main_window.py app\controllers\plot_controller.py`
- Final Verification Verdict: PASS

# Manual Test Directives

Ready for manual testing.

- Prerequisite: Start WE-DAVIS from this packet branch and have the sample `.pld` folders available under `resources/sample_data`.
- Load `resources/sample_data/frequency_sample`, open the `Settings` tab, and inspect the new `Units` section. Expected result: the existing settings widgets still render, the units summary is populated, the display selectors match the detected families for the loaded dataset, and the export selector contains only `Source Units` and `Display Units`.
- While the frequency sample is loaded, change one display-unit selector and then change the export-unit selector. Expected result: the selection sticks immediately, the current plots refresh through the normal settings update path, and no data reload dialog or error is triggered.
- Load `resources/sample_data/time_transient_sample` and revisit the `Settings` tab. Expected result: the `Units` section updates to the families detected in the time-domain dataset, and the existing time-domain settings controls still behave as before.

# Residual Risks

- This packet only stores the selected display/export units and raw canonical datasets; it does not yet project converted numeric views into plots.
- The units section is driven by the primary dataset's detected quantity families. Later packets still need to define how projected primary/comparison views consume the stored selections during conversion.
- Export behavior is intentionally unchanged here; the export selector is stored centrally for the later export-mode packet to consume.

# Ready for Integration

- Yes: The packet acceptance criteria are met, required verification passed, and the remaining conversion/export work is deferred to later packets by design.
