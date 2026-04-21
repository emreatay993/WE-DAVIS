# Steady-State Soft-Start Smoothing Status

## Packet Status

| Packet | Status | Branch Label | Accepted Commit SHA | Notes |
| --- | --- | --- | --- | --- |
| `P00` | `PASS` | `n/a` | `n/a` | Bootstrap packet docs created. |
| `P01` | `PASS` | `codex/steady_state_soft_start_smoothing/p01-analysis-helper-tests` | `acc41c9ffcbd256df85a459d7a9193997daaa916` | Accepted. Packet-owned tests and review gate passed; broad `unittest discover tests` crash reproduced on target branch `master` as a baseline repository/environment blocker. |
| `P02` | `PASS` | `codex/steady_state_soft_start_smoothing/p02-dialog-soft-start-controls` | `c19930ca1cc4c54906bbb6904955329554fbabb8` | Accepted. Packet-owned tests and review gate passed; broad discovery blocker carried forward. |
| `P03` | `PENDING` | `codex/steady_state_soft_start_smoothing/p03-docs-help-copy` | `n/a` | Awaiting `P02`. |

## Ledger Notes

- The executor owns updates after `P00`.
- For every later `PASS`, record the accepted branch label, accepted substantive 40-character commit SHA, commands, artifacts, and residual risks.

## P01 Acceptance Record

- Accepted branch label: `codex/steady_state_soft_start_smoothing/p01-analysis-helper-tests`
- Accepted substantive commit SHA: `acc41c9ffcbd256df85a459d7a9193997daaa916`
- Commands:
  - PASS: `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`
  - FAIL on packet branch and target branch baseline: `.\venv\Scripts\python.exe -m unittest discover tests` exited `-1073740791`
  - PASS review gate: `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`
- Artifacts:
  - `docs/specs/work_packets/steady_state_soft_start_smoothing/P01_analysis_helper_tests_WRAPUP.md`
- Residual risk:
  - Repository-wide `unittest discover tests` is blocked by a native Windows crash that reproduces on `master` without P01 changes.

## P02 Acceptance Record

- Accepted branch label: `codex/steady_state_soft_start_smoothing/p02-dialog-soft-start-controls`
- Accepted substantive commit SHA: `c19930ca1cc4c54906bbb6904955329554fbabb8`
- Commands:
  - PASS: `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`
  - FAIL baseline blocker: `.\venv\Scripts\python.exe -m unittest discover tests`
  - PASS review gate: `.\venv\Scripts\python.exe -m unittest tests.test_steady_state_time_history_export`
- Artifacts:
  - `docs/specs/work_packets/steady_state_soft_start_smoothing/P02_dialog_soft_start_controls_WRAPUP.md`
- Residual risk:
  - Repository-wide `unittest discover tests` remains blocked by the existing broad discovery crash.
