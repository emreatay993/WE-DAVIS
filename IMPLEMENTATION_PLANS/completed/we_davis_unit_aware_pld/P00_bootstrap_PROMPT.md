Read these files first:
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_MANIFEST.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_STATUS.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P00_bootstrap.md`

Implement exactly one packet: `P00`.

Scope:
- Documentation bootstrap only.
- Do not start `P01` or any later packet.

Branch label:
- `master`

Required steps:
1. Ensure the bootstrap packet docs listed in the spec exist and are internally consistent.
2. Run the full `Verification Commands` from the packet spec.
3. Create `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P00_bootstrap_WRAPUP.md`.
4. Put `Packet`, `Branch Label`, `Commit Owner`, `Commit SHA`, `Changed Files`, and `Artifacts Produced` at the top of `Implementation Summary`.
5. Treat `Commit Owner` as one of `worker`, `executor`, or `executor-pending`, not a git identity.
6. Use a full 40-character real git SHA for `Commit SHA` when one exists; otherwise explain clearly.
7. End `Verification` with `Final Verification Verdict: PASS` or `Final Verification Verdict: FAIL`.
8. Begin `Ready for Integration` with `Yes:` or `No:`.
9. Stop after this packet.
