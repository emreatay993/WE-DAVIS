Use [$subagent-work-packet-executor](C:\Users\emre_\.codex\skills\subagent-work-packet-executor\SKILL.md) to execute the packet set at `C:\Users\emre_\PycharmProjects\WE-DAVIS\IMPLEMENTATION_PLANS\in_progress\we_davis_unit_aware_pld`.

Target merge branch: `master`.

Treat the packet docs on disk as the only source of truth. Do not rely on prior planning chat. Execute the packet set wave by wave until all packets are `PASS` or a terminal `FAIL` occurs.

After all packets are `PASS` and after I confirm the merge into `master` succeeded, move:

- `C:\Users\emre_\PycharmProjects\WE-DAVIS\IMPLEMENTATION_PLANS\in_progress\we_davis_unit_aware_pld`

to:

- `C:\Users\emre_\PycharmProjects\WE-DAVIS\IMPLEMENTATION_PLANS\completed\we_davis_unit_aware_pld`

Keep the packet-set contents intact during that move, including the manifest, status ledger, packet specs, prompts, and wrap-up files.
