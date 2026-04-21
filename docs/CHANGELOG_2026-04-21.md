# WE-DAVIS Changelog

Change window: commits from 2026-04-11 through 2026-04-21.

Reviewed commit range: `e97c3bce0115b60786960dcdda1262ef6b24013f..b7b3f5f`.

The commits in this window landed on 2026-04-19, 2026-04-20, and 2026-04-21.

## For Users

### Data Loading and Samples

- Added bundled sample PLD datasets for frequency and time-transient workflows.
- Improved PLD filename handling so capitalized `.PLD` suffixes are accepted.
- Fixed selector refresh behavior after loading a new dataset.
- Restored unit-aware loading for multi-select tabs.
- Refined multi-select load controls.
- Corrected units in the transient sample dataset.

### Units and Export Behavior

- Added unit controls in settings so loaded data can be interpreted and displayed with the intended unit system.
- Added plot unit projection so charts can present converted units consistently.
- Updated ANSYS export behavior to honor the selected export unit mode.
- Defaulted ANSYS export `TIME` values to seconds when the source data does not provide a time unit.
- Added Settings-tab guidance explaining how CSV exports use Source Units and Display Units.
- Updated Full Data CSV export confirmation to state that it uses the current display units.
- Updated the Extract Data at Each Interval CSV export so unit-aware values also carry unit labels in the CSV headers.
- Added tooltip and confirmation text showing that the interval CSV export follows Settings > Export Units.

### Steady-State Workflows

- Added steady-state cycle estimator tools.
- Added a steady-state time-history export workflow.
- Improved multi-part time-domain reconstruction.
- Added steady-state soft-start smoothing for exported steady-state time histories.
- Added soft-start controls, validation, help text, and documentation for the steady-state export dialog.
- Made the steady-state time-history export dialog maximizable/fullscreenable.
- Added `K` and `L` Plotly preview shortcuts in the steady-state export dialog for legend placement and visibility.
- Rendered steady-state estimator help as HTML.

### Fixes and Cleanup

- Removed a sampling-rate FutureWarning.
- Cleaned stale offline packaging artifacts from the tracked tree.

## For Developers

### Unit System Infrastructure

- Added a reusable unit contract subsystem under `app/units/`.
- Added loader metadata plumbing so data managers, controllers, plotting, and export paths can share unit context.
- Updated plotting and ANSYS export code to use the unit metadata contract instead of relying only on implicit defaults.

### UI and Controller Work

- Added settings UI controls for unit configuration.
- Added steady-state cycle estimator and time-history export dialogs.
- Added a reusable checkable combo box widget for multi-select UI flows.
- Updated action handling, main window wiring, and tab integrations for the new workflows.
- Added a reusable steady-state soft-start export helper and integrated it with the export dialog.
- Added scoped keyboard shortcut wiring for the steady-state export preview.

### Tests and Regression Coverage

- Added tests for unit contracts, data manager unit metadata, settings unit controls, plot unit projection, export unit mode, and steady-state time-history export.
- Added package test initialization for the new regression suite.
- Added regression coverage for soft-start smoothing, fullscreen window controls, Plotly shortcut actions, and CSV unit-labeled interval exports.

### Documentation and Repository Hygiene

- Updated developer and README documentation for the new workflows and sample data.
- Archived the completed unit-aware implementation packet set.
- Added and closed the steady-state soft-start smoothing packet set.
- Added plan-specific references for the steady-state soft-start work.
- Ignored local generated artifacts.
- Removed stale offline-build helper artifacts from the tracked tree.

## Commit List

- `73705e6` Fix selector refresh when loading new data
- `d76d07c` Add bundled sample PLD datasets
- `4e28b21` Add reusable unit contract subsystem
- `0edeada` Add P01 packet wrap-up
- `698cf94` Fix P01 wrap-up format
- `290b966` P02: emit loader unit metadata
- `535141b` P02: add loader unit metadata wrap-up
- `8480cab` Add settings unit controls
- `0a47993` Add P03 wrap-up
- `e3c2ca1` Fix P03 wrap-up headings
- `94d2b8e` Implement plot unit projection
- `b6947a4` Add P04 wrap-up
- `49a12ae` P05 honor export unit mode
- `c4ad622` P05 add wrap-up
- `0aed3e5` P06: close unit-aware docs and regressions
- `ea733b0` P06: add closeout wrap-up
- `22a428b` Fix sampling-rate FutureWarning
- `2784aaa` Archive completed unit-aware packet set
- `27f7be0` Ignore local generated artifacts
- `c1e7e08` Remove stale offline build artifacts
- `032d567` Restore unit-aware load handling with multi-select tabs
- `26fc66f` Default TIME unit to seconds for ANSYS export
- `4da5d53` Add steady-state cycle estimator tools
- `4b338d9` Support multi-part time-domain reconstruction
- `a017d4d` Handle capitalized PLD suffixes
- `4873064` Add steady-state time-history export workflow
- `1f14223` docs: add recent changelog
- `5271acf` ui: refine multiselect load controls
- `989ef8d` ui: render steady-state estimator help as html
- `374ce17` data: correct transient sample units
- `ffbff9d` build: clean stale offline packaging artifacts
- `834cf6f` Add steady-state soft-start work packets
- `acc41c9` Add steady-state soft-start helper
- `483e71c` Add P01 soft-start wrap-up
- `ff011e4` Remediate P01 wrap-up format
- `d526629` Fix P01 wrap-up verdict format
- `28b331e` Record P01 packet acceptance
- `c19930c` Add soft-start controls to steady-state export dialog
- `a71e8e9` Add P02 soft-start controls wrap-up
- `a328645` Fix P02 wrap-up verdict format
- `0c730c5` Record P02 packet acceptance
- `a5386d6` Document steady-state soft-start smoothing
- `f40c4e2` Add P03 wrap-up
- `16541db` Fix P03 wrap-up verdict format
- `516e5b4` Add plan-specific steady-state references
- `dc60d8b` Update P03 wrap-up for reference remediation
- `e5e8910` Record P03 packet acceptance
- `b7b3f5f` Improve time-history export UX and unit labeling
