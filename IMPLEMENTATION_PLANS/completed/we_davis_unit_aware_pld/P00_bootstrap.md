# P00 Bootstrap

## Objective
- Establish the packet-set artifacts on disk for fresh-context execution and mark bootstrap as complete without starting implementation packets.

## Preconditions
- Approved plan exists at `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_PLAN.md`.

## Execution Dependencies
- `none`

## Target Subsystems
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/**`

## Conservative Write Scope
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_PLAN.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_MANIFEST.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_STATUS.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P00_bootstrap.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P00_bootstrap_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P01_unit_contract.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P01_unit_contract_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P02_loader_unit_metadata.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P02_loader_unit_metadata_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P03_settings_unit_controls.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P03_settings_unit_controls_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P04_plot_unit_projection.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P04_plot_unit_projection_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/EXECUTOR_THREAD_PROMPT.md`

## Required Behavior
- Write a coherent packet set that a fresh executor thread can use without relying on prior chat context.
- Mark `P00` as `PASS` and every later packet as `PENDING` in the status ledger.
- Do not start `P01` or any later packet from this bootstrap packet.

## Non-goals
- Any code implementation under `app/`.
- Any executor dispatch or worker spawning.
- Moving the packet set to `IMPLEMENTATION_PLANS/completed`.

## Verification Commands
- `.\venv\Scripts\python.exe -m compileall IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld`

## Review Gate
- `none`

## Expected Artifacts
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_PLAN.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_MANIFEST.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_STATUS.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P00_bootstrap.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P00_bootstrap_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P01_unit_contract.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P01_unit_contract_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P02_loader_unit_metadata.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P02_loader_unit_metadata_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P03_settings_unit_controls.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P03_settings_unit_controls_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P04_plot_unit_projection.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P04_plot_unit_projection_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout_PROMPT.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/EXECUTOR_THREAD_PROMPT.md`

## Acceptance Criteria
- All packet docs exist in the packet directory.
- The manifest includes authoritative `Execution Waves`.
- The status ledger marks only `P00` as `PASS`.

## Handoff Notes
- The executor should read the manifest, status ledger, and `P00` only at startup.
- The executor should not move this packet set to `IMPLEMENTATION_PLANS/completed` until implementation is done and the merge is confirmed.
