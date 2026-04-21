# P03 Docs And Help Copy Prompt

Read before editing:

- `docs/specs/work_packets/steady_state_soft_start_smoothing/STEADY_STATE_SOFT_START_SMOOTHING_MANIFEST.md`
- `docs/specs/work_packets/steady_state_soft_start_smoothing/STEADY_STATE_SOFT_START_SMOOTHING_STATUS.md`
- `docs/specs/work_packets/steady_state_soft_start_smoothing/P03_docs_help_copy.md`

Implement exactly `P03` on branch `codex/steady_state_soft_start_smoothing/p03-docs-help-copy`.

Stay inside the packet write scope. Run the full `Verification Commands`. Prefer the narrow packet rerun during development and remediation. Run the `Review Gate` before closeout.

Create `docs/specs/work_packets/steady_state_soft_start_smoothing/P03_docs_help_copy_WRAPUP.md` with sections:

- `Implementation Summary`
- `Verification`
- `Manual Test Directives`
- `Residual Risks`
- `Ready for Integration`

At the top of `Implementation Summary`, include `Packet`, `Branch Label`, `Commit Owner`, `Commit SHA`, `Changed Files`, and `Artifacts Produced`. `Commit Owner` must be `worker`, `executor`, or `executor-pending`. `Commit SHA` must be the full 40-character SHA for the substantive packet commit, not `HEAD` or a placeholder.

Commit the substantive packet changes first, capture `git rev-parse HEAD`, then write or update the wrap-up with that SHA. If the wrap-up lands in a separate follow-up docs commit, the recorded SHA may still point at the substantive commit. End `Verification` with `Final Verification Verdict: PASS` or `Final Verification Verdict: FAIL`. Begin `Ready for Integration` with `Yes:` or `No:`. Stop after this packet.
