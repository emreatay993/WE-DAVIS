Read these files first:
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_MANIFEST.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/WE_DAVIS_UNIT_AWARE_PLD_STATUS.md`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout.md`

Implement exactly one packet: `P06`.

Branch label:
- `codex/we-davis-unit-aware-pld/p06-regression-docs-closeout`

Required rules:
1. Stay inside the packet write scope from `P06_regression_docs_closeout.md`.
2. Refresh docs to match actual implemented behavior and explicitly keep `.log` support deferred.
3. After all packets are eventually complete and the merge is confirmed, the packet set should be moved from `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld` to `IMPLEMENTATION_PLANS/completed/we_davis_unit_aware_pld`, but do not perform that move inside this packet unless the executing user explicitly confirms the merge already happened.
4. Run the packet's full `Verification Commands`.
5. Run the packet `Review Gate` before marking the packet done.
6. Create `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P06_regression_docs_closeout_WRAPUP.md`.
7. Put `Packet`, `Branch Label`, `Commit Owner`, `Commit SHA`, `Changed Files`, and `Artifacts Produced` at the top of `Implementation Summary`.
8. Treat `Commit Owner` as a packet-contract token (`worker`, `executor`, or `executor-pending`), not a git author or committer name.
9. Commit the substantive packet changes first, capture `git rev-parse HEAD`, then write or update the wrap-up using that full 40-character SHA.
10. Commit packet-local changes and the wrap-up on the packet branch when you own the final substantive packet state.
11. Do not edit the shared status ledger.
12. Stop after this packet.
