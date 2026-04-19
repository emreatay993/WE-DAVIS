# P05 Export Unit Mode Wrap-Up

## Implementation Summary

- Packet: P05 Export Unit Mode
- Branch Label: codex/we-davis-unit-aware-pld/p05-export-unit-mode
- Commit Owner: worker
- Commit SHA: 49a12aeaeaa807b888b71e016eba31fe82481b3d
- Changed Files: app/controllers/action_handler.py, app/analysis/ansys_exporter.py, tests/test_export_unit_mode.py, IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode_WRAPUP.md
- Artifacts Produced: IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode_WRAPUP.md, tests/test_export_unit_mode.py, app/controllers/action_handler.py, app/analysis/ansys_exporter.py

- Reworked `ActionHandler` so ANSYS preprocessing starts from preserved source data, projects into either `Source Units` or `Display Units` explicitly through the unit-conversion service, and writes mode-specific CSV filenames instead of the old fixed `multiplied_by_1000` outputs.
- Added ANSYS eligibility validation in `ActionHandler` that checks the selected export frame against the parsed quantity-family contract before any template generation starts, requiring known domain, force, moment, and phase families and rejecting mixed-family or native-only cases with a user-facing warning.
- Updated time-domain reconstruction export to follow the active export mode as well, including reversing displayed `Theta` / trace values back to source units when the user selects `Source Units`.
- Extended `AnsysExporter` with explicit export-unit inputs so harmonic and transient templates now receive the selected domain, force, moment, and phase units directly, convert solver-internal values with the unit service, and remove the hard-coded harmonic `* 1000` moment path and the dead transient scaling variable.
- Added packet-local regression coverage for display-mode ANSYS preprocessing, source-mode time-domain CSV export, unsupported-family ANSYS rejection, and explicit solver-table unit conversion without requiring a local ANSYS installation.

## Verification

- PASS: `$env:QT_QPA_PLATFORM='offscreen'; .\venv\Scripts\python.exe -m unittest tests.test_export_unit_mode`
- PASS: `.\venv\Scripts\python.exe -m compileall app\controllers\action_handler.py app\analysis\ansys_exporter.py`
- Final Verification Verdict: PASS

## Manual Test Directives

Ready for manual testing.

- Prerequisite: start WE-DAVIS from this packet branch and keep `resources/sample_data/frequency_sample` and `resources/sample_data/time_transient_sample` available.
- Load `resources/sample_data/frequency_sample`, set export mode to `Display Units`, choose non-native display units such as `kHz`, `N`, `N*mm`, and `rad`, then run ANSYS export for one side. Expected result: the generated CSV filenames end with `_display_units`, the exported frequency/load values reflect the chosen display units, and template generation proceeds without any `multiplied by 1000` naming or status text.
- In the same frequency sample, switch export mode back to `Source Units` and rerun ANSYS export for the same side. Expected result: the generated CSV filenames end with `_source_units`, the exported values match the raw loaded source units, and the template still launches for the supported load families.
- In `Time Domain Representation`, keep the display units on a converted setup such as `rad` and `N`, then export the reconstructed CSV once in `Display Units` mode and once in `Source Units` mode. Expected result: the display-mode CSV keeps the shown `Theta` / magnitude units, while the source-mode CSV converts `Theta` back to degrees and load traces back to their source units where those units are known.
- Load `resources/sample_data/time_transient_sample` and attempt ANSYS export. Expected result: the export stops before template creation and shows a clear warning that the selected data does not resolve to the known ANSYS-compatible unit families required by the current template assumptions.

## Residual Risks

- The current ANSYS export path now accepts explicit units, but it still assumes one resolved export unit per quantity family across the selected columns; mixed-unit exports within the same family are intentionally rejected instead of being normalized per channel.
- The bundled transient sample still lacks explicit TIME-unit metadata, so transient ANSYS export is expected to warn and stop until a later change provides a known time unit for that path.
- Harmonic force application still follows the legacy Mechanical discrete-value path while harmonic moment application uses APDL tables; this packet makes both paths unit-aware but does not redesign the underlying template strategy.

## Ready for Integration

- Yes: Export preprocessing is unit-mode aware, the hard-coded scale branch is removed, unsupported ANSYS cases fail clearly before template creation, and the packet-local verification and compile gate pass.
