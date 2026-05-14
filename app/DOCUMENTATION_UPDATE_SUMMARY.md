# Documentation Update Summary

## Overview

The documentation set has been refreshed against the current WE-DAVIS source
tree. The update focuses on architecture, file inventory, signal wiring,
README/developer guidance, unit-aware exports, steady-state workflows, and
current verification commands.

## Updated Areas

- Architecture references now include `app/units/`, steady-state helpers,
  current dialogs, unit-context flow, and automated tests.
- File index line counts and module responsibilities were refreshed.
- Signal references now include unit-context payloads, load progress/failure
  signals, steady-state action signals, and the Part Loads to Time Domain
  Representation refresh path.
- README/developer docs now use the current `WE-DAVIS` name, root
  `requirements.txt`, `python main.py`, `python -m unittest discover -s tests
  -p "test_*.py"`, and `python -m PyInstaller --noconfirm WE-DAVIS.spec`.
- Export docs now describe source/display export-unit modes and
  `AnsysExportUnits` rather than fixed scaling.
- User/UI docs now cover display units, export-unit mode, steady-state
  time-history export, and soft start.

## Follow-Up

- Re-run this refresh after any major UI/export/refactor work.
- Keep `FILE_INDEX.md` line counts in the release checklist.
- Add Qt signal/wiring tests when the environment supports headless Qt.
