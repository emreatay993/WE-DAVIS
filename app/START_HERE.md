# Start Here

Welcome! This checklist gets you productive with WE-DAVIS in under an hour.

## 1. Understand the Product
- Read `EXECUTIVE_SUMMARY.md` for the elevator pitch.
- Skim `DETAILED_USER_MANUAL.md` to see the user-facing flows and vocabulary.
- Review `ARCHITECTURE.md` for a mental model of the code paths you will touch.

## 2. Prepare Your Environment
- Recommended stack: Python 3.10+ on Windows (PyQt5 with QtWebEngine requires desktop support).
- Install dependencies from the app folder: `pip install -r app/requirements.txt`.
- If you plan to test Ansys exports, ensure Ansys Mechanical with the `ansys-mechanical-core` Python package is installed and licensed on the same machine.
- Multiple ANSYS versions can coexist; the application will detect installed versions in `C:\Program Files\ANSYS Inc` and allow version selection during export.

## 3. Run the Application
1. From the repository root run `python main.py`.
2. Select a directory that contains at least one raw data folder (each must hold `full.pld` and `max.pld` files).
3. Confirm that the tabs enable correctly and sample plots render.

## 4. Explore the Codebase
- `FILE_INDEX.md` maps every module to its purpose; keep it open while navigating the project.
- `SIGNAL_SLOT_REFERENCE.md` shows how UI events travel through the controller layer.
- `REFACTORING_PROGRESS.md` highlights known cleanup opportunities.

## 5. Contribute Safely
- Follow the `STATUS_REPORT.md` for current priorities and open risks.
- When touching data ingestion or plotting, update the relevant documentation file and cross-link changes in `DOCUMENTATION_UPDATE_SUMMARY.md`.
- Run a manual smoke test (load TIME and FREQ datasets, exercise each tab) before pushing changes; automated tests are not yet in place.

You are ready to build! Reach out to the maintainer listed in the Settings tab for access to sample datasets or infrastructure credentials.
