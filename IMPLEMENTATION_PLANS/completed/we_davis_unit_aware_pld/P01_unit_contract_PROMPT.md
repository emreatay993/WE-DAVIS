Read these files first:
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_MANIFEST.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_STATUS.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P01_unit_contract.md`

Implement exactly one packet: `P01`.

Branch label:
- `codex/we-davis-unit-aware-pld/p01-unit-contract`

Required rules:
1. Stay inside the packet write scope from `P01_unit_contract.md`.
2. Prefer a maintainable `app/units/` package over ad hoc helpers in unrelated modules.
3. Run the packet's full `Verification Commands`.
4. Run the packet `Review Gate` before marking the packet done.
5. Create `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P01_unit_contract_WRAPUP.md`.
6. Put `Packet`, `Branch Label`, `Commit Owner`, `Commit SHA`, `Changed Files`, and `Artifacts Produced` at the top of `Implementation Summary`.
7. Treat `Commit Owner` as a packet-contract token (`worker`, `executor`, or `executor-pending`), not a git author or committer name.
8. Commit the substantive packet changes first, capture `git rev-parse HEAD`, then write or update the wrap-up using that full 40-character SHA.
9. Commit packet-local changes and the wrap-up on the packet branch when you own the final substantive packet state.
10. Do not edit the shared status ledger.
11. Stop after this packet.
