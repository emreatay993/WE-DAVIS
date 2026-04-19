Read these files first:
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_MANIFEST.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_STATUS.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode.md`

Implement exactly one packet: `P05`.

Branch label:
- `codex/we-davis-unit-aware-pld/p05-export-unit-mode`

Required rules:
1. Stay inside the packet write scope from `P05_export_unit_mode.md`.
2. Replace hard-coded scaling with the shared conversion service; do not introduce a second export-specific scaling table.
3. Fail unsupported ANSYS export cases clearly instead of guessing.
4. Run the packet's full `Verification Commands`.
5. Run the packet `Review Gate` before marking the packet done.
6. Create `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P05_export_unit_mode_WRAPUP.md`.
7. Put `Packet`, `Branch Label`, `Commit Owner`, `Commit SHA`, `Changed Files`, and `Artifacts Produced` at the top of `Implementation Summary`.
8. Treat `Commit Owner` as a packet-contract token (`worker`, `executor`, or `executor-pending`), not a git author or committer name.
9. Commit the substantive packet changes first, capture `git rev-parse HEAD`, then write or update the wrap-up using that full 40-character SHA.
10. Commit packet-local changes and the wrap-up on the packet branch when you own the final substantive packet state.
11. Do not edit the shared status ledger.
12. Stop after this packet.
