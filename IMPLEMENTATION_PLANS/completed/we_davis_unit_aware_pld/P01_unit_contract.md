# P01 Unit Contract

## Objective
- Create the reusable unit model, normalization catalog, quantity-family inference, and conversion APIs that later packets will adopt without rewriting core unit logic.

## Preconditions
- `P00` is `PASS`.

## Execution Dependencies
- `none`

## Target Subsystems
- `app/units/**`
- `tests/__init__.py`
- `tests/test_unit_contract.py`

## Conservative Write Scope
- `app/units/**`
- `tests/__init__.py`
- `tests/test_unit_contract.py`
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P01_unit_contract_WRAPUP.md`

## Required Behavior
- Add a maintainable unit subsystem under `app/units/` rather than scattering ad hoc conversions.
- Define a canonical unit context contract that can represent:
  - source unit per column,
  - normalized unit string,
  - inferred quantity family,
  - compatible display units,
  - current display-unit selection,
  - native-only fallback for unknown or unsupported units.
- Support at least these quantity families in the contract, even if some remain native-only until later adoption:
  - time,
  - frequency,
  - phase,
  - force,
  - moment,
  - displacement,
  - velocity,
  - acceleration,
  - angular displacement,
  - angular velocity,
  - angular acceleration,
  - unknown.
- Provide conversion helpers that return converted copies of scalars, pandas `Series`, and pandas `DataFrame` views without mutating source data.
- Normalize common textual variants such as `kN*m`, `kN m`, `N*m`, `N m`, and analogous angular/unit spellings when feasible.

## Non-goals
- Parsing `max.pld`.
- Emitting unit context from `DataManager`.
- Adding Qt widgets or wiring UI selectors.
- Changing plotting or export code.

## Verification Commands
- `.\venv\Scripts\python.exe -m unittest tests.test_unit_contract`

## Review Gate
- `.\venv\Scripts\python.exe -m unittest tests.test_unit_contract.UnitContractSmokeTests`

## Expected Artifacts
- `IMPLEMENTATION_PLANS/in_progress/we_davis_unit_aware_pld/P01_unit_contract_WRAPUP.md`
- `tests/__init__.py`
- `tests/test_unit_contract.py`

## Acceptance Criteria
- `app/units/` exists and exposes a clear import surface for later packets.
- Unit normalization and quantity-family inference are covered by automated tests.
- Conversion helpers reject incompatible conversions cleanly instead of guessing.

## Handoff Notes
- `P02` should adopt the contract as-is and extend it only if the loader exposes a concrete metadata gap.
- If `P02` needs to expand normalization aliases, it may edit `app/units/**` in-scope because waves are sequential.
