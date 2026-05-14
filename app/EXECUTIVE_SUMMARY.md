# Executive Summary

WE-DAVIS centralizes inspection of mechanical load datasets produced during
drivetrain and structural testing. The application streamlines three core
workflows:

- **Insight generation**: Engineers load one or more `.pld` runs, inspect
  individual channels, review interfaces and part loads, and compare datasets
  without scripting.
- **Decision support**: Plotly-backed views expose load distribution, frequency
  behavior, time-history behavior, absolute differences, relative differences,
  and phase-aware comparisons.
- **Downstream handoff**: Unit-aware CSV exports, steady-state time-history
  exports, and ANSYS Mechanical harmonic/transient templates bridge test data to
  simulation.

The codebase is organized around a PyQt5 shell, a PLD/units data layer,
controller slots, reusable analysis helpers, and Plotly rendering. Current docs
cover architecture, onboarding, user workflows, signal wiring, settings, module
responsibilities, and refactoring priorities.
