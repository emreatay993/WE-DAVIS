# P04 Plot Unit Projection Wrap-Up

## Implementation Summary

- Packet: P04 Plot Unit Projection
- Branch Label: codex/we-davis-unit-aware-pld/p04-plot-unit-projection
- Commit Owner: worker
- Commit SHA: 94d2b8ec783cedbe8910f0d45a6b33e460f2b944
- Changed Files: app/controllers/plot_controller.py, app/plotting/plotter.py, tests/test_plot_unit_projection.py, IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P04_plot_unit_projection_WRAPUP.md
- Artifacts Produced: IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P04_plot_unit_projection_WRAPUP.md, tests/test_plot_unit_projection.py, app/controllers/plot_controller.py, app/plotting/plotter.py

- Moved plot-time conversion into `PlotController` so plots now project from the preserved raw primary/comparison frames through the active display-unit contexts instead of mutating stored data.
- Applied projected units across `Single Data`, `Compare Data`, `Interface Data`, `Part Loads`, `Compare Part Loads`, `Time Domain Representation`, and computed `Time Step` / `Sampling Rate` series, including converted comparison magnitudes and unit-stable percentage differences.
- Updated plotting metadata so x-axis labels, y-axis labels, comparison labels, and hover text use the active display units, while grouped mixed-family plots fall back to a `Mixed Units` y-axis title.
- Preserved the existing frequency-domain phase workflow while allowing phase and frequency display-unit changes to flow through phase plots and time-domain representation titles/axes.
- Added packet-local controller and smoke coverage, including both bundled sample datasets plus focused tests for mixed-unit grouped traces, computed metrics, comparison scaling, and hover metadata plumbing.

## Verification

- PASS: `$env:QT_QPA_PLATFORM='offscreen'; .\venv\Scripts\python.exe -m unittest tests.test_plot_unit_projection`
- PASS: `.\venv\Scripts\python.exe -m unittest tests.test_plot_unit_projection.PlotUnitProjectionSmokeTests`
- Final Verification Verdict: PASS

## Manual Test Directives

Ready for manual testing.

- Prerequisite: start WE-DAVIS from this packet branch and keep `resources/sample_data/frequency_sample` and `resources/sample_data/time_transient_sample` available.
- Load `resources/sample_data/frequency_sample`, set display units to `kHz`, `N`, and `rad`, then open `Single Data`, `Compare Data`, and `Time Domain Representation`. Expected result: the frequency axis switches to `kHz`, force magnitudes switch to `N`, phase values switch to `rad`, absolute-difference plots rescale with the selected force unit, and relative-difference plots stay numerically unchanged.
- In the same frequency sample, open `Interface Data` or `Part Loads` for a side that includes both translational and rotational result families. Expected result: each trace keeps the correct converted values and any grouped plot spanning multiple quantity families uses `Mixed Units` on the y-axis.
- Load `resources/sample_data/time_transient_sample`, switch to `Single Data`, and select `Time Step (Δt)` and `Sampling Rate (Hz)`. Expected result: the computed series render successfully, their axis/hover labels match the active display units, and the raw loaded data is unchanged when you switch back to a native signal channel.

## Residual Risks

- `Spectrum Plot` data is projected before FFT generation, but the external spectrum helper still owns its own layout semantics; this packet does not add amplitude-unit labels inside the helper-generated spectrum figure.
- TIME-axis projection now supports synthetic time-unit labeling in the plotting layer even though the current settings UI only exposes quantity families detected from source metadata.
- The packet stays inside the plotting layer by design; export-time conversion still depends on the follow-on packet reusing these projection entry points.

## Ready for Integration

- Yes: Plot-time unit projection is implemented in the assigned scope, packet-local verification and the executor smoke gate pass, and the remaining export work is explicitly deferred to P05.
