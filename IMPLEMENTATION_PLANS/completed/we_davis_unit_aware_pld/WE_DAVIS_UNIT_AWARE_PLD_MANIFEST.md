# WE_DAVIS_UNIT_AWARE_PLD Manifest

## Scope Baseline
- Packetize the approved `.pld`-only unit-awareness plan for WE-DAVIS into a fresh-context execution set.
- Preserve the current PyQt5 app architecture: `DataManager` owns ingestion, `MainWindow` owns app state, `PlotController` owns plotting orchestration, `Plotter` owns figure formatting, and `ActionHandler` owns export workflows.
- Allow new modules when they improve maintainability, but keep adoption conservative and explicit.

## Requirement Anchors
- User request on 2026-04-19: make WE-DAVIS unit-aware for `.pld` inputs, add UI controls for input/display units, and convert data in-app.
- Scope correction on 2026-04-19: skip `.log` input support for now.
- Semantic correction on 2026-04-19: `T1/T2/T3` and `R1/R2/R3` are translational/rotational components, not guaranteed force/moment semantics.
- Base implementation plan: `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_PLAN.md`
- Relevant repo anchors:
  - `app/data_manager.py`
  - `app/main_window.py`
  - `app/controllers/plot_controller.py`
  - `app/controllers/action_handler.py`
  - `app/plotting/plotter.py`
  - `app/ui/tab_settings.py`
  - `resources/sample_data/frequency_sample/PLD_HEADER_DATA_max.pld`
  - `resources/sample_data/time_transient_sample/PLD_HEADER_DATA_max.pld`

## Locked Defaults
- `.pld` input only in this packet set.
- Source units are auto-detected from `max.pld`; no manual source-unit override in v1.
- Quantity family is inferred from the parsed unit string, not from `T*` or `R*`.
- `T*` and `R*` remain grouping hints for existing translational and rotational views only.
- The UI exposes one display-unit selector per detected quantity family in `SettingsTab`.
- Unknown or unsupported units stay native-only; the app must not guess conversions.
- Exports must support an explicit `Source Units` vs `Display Units` mode.

## Packet Order

| Packet | Title | Branch Label | Primary Purpose |
| --- | --- | --- | --- |
| `P00` | Bootstrap | `master` | Write and register the packet docs on disk. |
| `P01` | Unit Contract | `codex/we-davis-unit-aware-pld/p01-unit-contract` | Define unit normalization, quantity families, and conversion APIs. |
| `P02` | Loader Unit Metadata | `codex/we-davis-unit-aware-pld/p02-loader-unit-metadata` | Parse `UNIT` data from `max.pld` and emit unit context with loaded data. |
| `P03` | Settings Unit Controls | `codex/we-davis-unit-aware-pld/p03-settings-unit-controls` | Add global unit selectors and app state for display/export choices. |
| `P04` | Plot Unit Projection | `codex/we-davis-unit-aware-pld/p04-plot-unit-projection` | Apply converted projections to plotting and comparison flows. |
| `P05` | Export Unit Mode | `codex/we-davis-unit-aware-pld/p05-export-unit-mode` | Replace hard-coded export scaling with explicit source/display conversion. |
| `P06` | Regression Docs Closeout | `codex/we-davis-unit-aware-pld/p06-regression-docs-closeout` | Finish regression coverage and refresh user/developer docs. |

## Execution Waves

### Wave 1
- `P01`

### Wave 2
- `P02`

### Wave 3
- `P03`

### Wave 4
- `P04`

### Wave 5
- `P05`

### Wave 6
- `P06`

## Handoff Artifacts
- Plan doc:
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_PLAN.md`
- Packet-set control docs:
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_MANIFEST.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_STATUS.md`
- Packet specs:
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P00_bootstrap.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P01_unit_contract.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P02_loader_unit_metadata.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P03_settings_unit_controls.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P04_plot_unit_projection.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout.md`
- Standalone packet prompts:
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P00_bootstrap_PROMPT.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P01_unit_contract_PROMPT.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P02_loader_unit_metadata_PROMPT.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P03_settings_unit_controls_PROMPT.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P04_plot_unit_projection_PROMPT.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode_PROMPT.md`
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout_PROMPT.md`
- Fresh-thread executor handoff prompt:
  - `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/EXECUTOR_THREAD_PROMPT.md`

## Planning Output
- Packet-set name: `WE_DAVIS_UNIT_AWARE_PLD`
- Packet directory: `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld`
- Packet count: `7` total (`P00` through `P06`)
- Auto-relay: skipped
- Suggested executor invocation target merge branch: `master`
