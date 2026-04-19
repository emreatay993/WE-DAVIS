# P06 Regression Docs Closeout Wrap-Up

## Implementation Summary

- Packet: P06 Regression Docs Closeout
- Branch Label: codex/we-davis-unit-aware-pld/p06-regression-docs-closeout
- Commit Owner: worker
- Commit SHA: 0aed3e56f2fce558e24441b27a1b4abe26668e3b
- Changed Files: app/README.md, docs/README.md, docs/modules/analysis.md, tests/test_data_manager_unit_metadata.py, tests/test_export_unit_mode.py, tests/test_plot_unit_projection.py, tests/test_settings_unit_controls.py, IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout_WRAPUP.md
- Artifacts Produced: IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout_WRAPUP.md, app/README.md, docs/README.md, docs/modules/analysis.md, tests/test_data_manager_unit_metadata.py, tests/test_export_unit_mode.py, tests/test_plot_unit_projection.py, tests/test_settings_unit_controls.py

- Refreshed the packet-owned user and developer docs to match the shipped unit-aware `.pld` workflow: source units are detected from `max.pld`, `SettingsTab` exposes one display-unit selector per detected quantity family, export behavior is explicitly `Source Units` vs `Display Units`, and `.log` input support is still deferred.
- Removed the stale exporter wording that implied converted outputs are always `multiplied by 1000` and replaced it with the current `ActionHandler` and `AnsysExporter` behavior based on explicit unit contexts and export-mode selection.
- Added a loader regression that proves `max.pld` drives both detected units and quantity-family inference even when channel suffixes look like `T1` or `R1`, which keeps the locked default that quantity family comes from parsed units rather than component naming.
- Added an ANSYS export regression for explicit source-mode output and hardened the packet-owned settings, plotting, and export tests so the required combined unit suite is stable even when earlier tests leave partial Qt or app-module stubs in `sys.modules`.
- Audited the implementation against the manifest defaults and kept the `.log` handoff conservative: future `.log` work should feed the existing `ColumnUnitContext` and export-mode pipeline instead of introducing a manual source-unit override or a parallel conversion path.

## Verification

- PASS: `$env:QT_QPA_PLATFORM='offscreen'; .\venv\Scripts\python.exe -m unittest tests.test_unit_contract tests.test_data_manager_unit_metadata tests.test_settings_unit_controls tests.test_plot_unit_projection tests.test_export_unit_mode`
- PASS: `.\venv\Scripts\python.exe -m compileall app`
- PASS: `$env:QT_QPA_PLATFORM='offscreen'; .\venv\Scripts\python.exe -m unittest tests.test_data_manager_unit_metadata tests.test_plot_unit_projection tests.test_export_unit_mode`
- Final Verification Verdict: PASS

## Manual Test Directives

Ready for manual testing.

- Prerequisite: launch WE-DAVIS from this branch and keep `resources/sample_data/frequency_sample` and `resources/sample_data/time_transient_sample` available. Manual validation for this packet is against `.pld` folders only because `.log` support is still deferred.
- Load `resources/sample_data/frequency_sample`, open `Settings`, and review the `Units` group. Expected result: the summary text reports source units detected from `max.pld`, one display-unit selector appears for each detected quantity family, and `Export Units` defaults to `Source Units`.
- In the same frequency sample, switch display units to values such as `kHz`, `N`, and `rad`, then open `Single Data`, `Compare Data`, and `Time Domain Representation`. Expected result: axes, hover labels, and magnitudes follow the selected display units while grouped mixed-family views continue to use `Mixed Units` where appropriate.
- Run ANSYS export once with `Export Units` set to `Display Units` and once with it set to `Source Units`. Expected result: the generated CSV filenames end with `_display_units` and `_source_units` respectively, the numeric values match the selected mode, and no filename or status text implies a fixed `multiplied by 1000` export path.
- Load `resources/sample_data/time_transient_sample` and export a reconstructed time-domain CSV after choosing converted display units. Expected result: `Display Units` export keeps the shown units, while `Source Units` export converts the reconstructed values back to the detected source-unit context where that context is known.

## Residual Risks

- `.log` ingestion remains out of scope. Future `.log` work should extend `DataManager` so it emits the same raw unit-context contract consumed today by `MainWindow`, `PlotController`, and `ActionHandler`, rather than layering on a separate override model.
- The verification suite now runs reliably in one process, but it still surfaces a pandas `FutureWarning` from `app/analysis/data_processing.py` about `mode.use_inf_as_na`; that warning does not block this packet, but a later cleanup should replace the deprecated option before a pandas upgrade turns it into a failure.
- This closeout packet updates docs and regression coverage only. It does not change the underlying export eligibility rules, so unknown or mixed-family ANSYS export cases still fail closed by design.

## Ready for Integration

- Yes: Documentation now matches the implemented unit-aware behavior, the targeted loader and export regression gaps are covered, the preexisting projection coverage is stable in the required full suite, and the packet is ready for executor review and later packet-set archival after merge confirmation.
