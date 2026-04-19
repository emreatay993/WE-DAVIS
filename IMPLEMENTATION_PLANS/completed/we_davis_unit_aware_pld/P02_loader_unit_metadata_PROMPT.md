Read these files first:
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_MANIFEST.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_STATUS.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P02_loader_unit_metadata.md`

Implement exactly one packet: `P02`.

Branch label:
- `codex/we-davis-unit-aware-pld/p02-loader-unit-metadata`

Required rules:
1. Stay inside the packet write scope from `P02_loader_unit_metadata.md`.
2. Reuse the unit contract from `P01`; do not invent a second metadata model.
3. Keep `.log` input out of scope.
4. Run the packet's full `Verification Commands`.
5. Run the packet `Review Gate` before marking the packet done.
6. Create `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P02_loader_unit_metadata_WRAPUP.md`.
7. Put `Packet`, `Branch Label`, `Commit Owner`, `Commit SHA`, `Changed Files`, and `Artifacts Produced` at the top of `Implementation Summary`.
8. Treat `Commit Owner` as a packet-contract token (`worker`, `executor`, or `executor-pending`), not a git author or committer name.
9. Commit the substantive packet changes first, capture `git rev-parse HEAD`, then write or update the wrap-up using that full 40-character SHA.
10. Commit packet-local changes and the wrap-up on the packet branch when you own the final substantive packet state.
11. Do not edit the shared status ledger.
12. Stop after this packet.
