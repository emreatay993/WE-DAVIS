Slide 1 — WE-DAVIS Beta Tollgate

- Purpose: Approve beta release for org-wide evaluation
- Tagline: Whole-Engine Data Visualization tool
- Presenter(s): <Name>, <Role>, <Team>
- Ask: Proceed to Beta; allocate support channel and pilot users

Figure mockup

- Title slide with product name and a one-sentence value proposition under it
- Background: subtle engineering image or blueprint grid

Slide 2 — Elevator Pitch & Objectives

- Problem: Fragmented workflows for TIME/FREQ load analysis and export
- Solution: Unified desktop app to load .pld data, explore, compare, and export
- Beta objectives: Validate usability, stability, performance on real datasets

Figure mockup

- 3-step flow graphic: Load → Explore → Export

Slide 3 — Users & Primary Use Cases

- Users: NVH/loads engineers, analysts, method engineers, CAE simulation engineers
- Use cases:
  - Inspect single/multi-folder datasets
  - Compare campaigns (Δ absolute/relative)
  - Part loads drill-down (T*/R* groups)
  - FREQ → time-domain representation (θ-based)
  - Export to ANSYS templates (harmonic/transient)
- Non-goals (beta): Cloud data management, multi-user project sharing

Figure mockup

- Persona icons mapped to 4–5 use cases with short captions

Slide 4 — Scope & Out-of-Scope (Beta)

- In scope: Data load, plotting, comparisons, CSV export, ANSYS export, Windows support
- Out of scope: Linux/macOS, cloud sync, automated report generation
- Constraints: Requires .pld format with full.pld + max.pld per folder

Figure mockup

- Two-column scope table with checkmarks vs crosses

Slide 5 — Architecture Overview

- Layers:
  - app/analysis: processing, ANSYS exporter
  - app/controllers: PlotController, ActionHandler
  - app/plotting: Plotter (Plotly)
  - app/ui: PyQt tabs & dock
  - app/data_manager.py: I/O + signals
  - app/main_window.py: composition & wiring
- Key libraries: PyQt5, PyQtWebEngine, Plotly, endaq, pandas, scipy, ANSYS Mechanical

Figure mockup

- Box-and-arrow module diagram with data/control paths

Slide 6 — Data Model & Sources

- Inputs: full.pld (numeric), max.pld (headers) per folder
- Domain detection: FREQ vs TIME
- Columns:
  - TIME or FREQ, optional NO, measurement columns
  - FREQ includes Phase_ columns
  - DataFolder for grouping multi-folder loads
- Combine: Concatenate validated folders, sort by domain column

Figure mockup

- File icons → parser → combined DataFrame schema (domain + channels + DataFolder)

Slide 7 — Data Flow & Signals

- Load: DataManager → dataLoaded(df, domain, folder)
- Populate UI: MainWindow fills selectors, toggles tabs
- Plot updates: Tab signals → PlotController → Plotter → WebViews
- Comparison: ActionHandler → comparisonDataLoaded(df) → Δ / %Δ (phase-aware in FREQ)
- Export: ActionHandler → AnsysExporter (harmonic/transient)

Figure mockup

- Sequence diagram: user → UI → controllers → plots/export

Slide 8 — UI Overview (Tabs & Dock)

- Dock: Multi-select folders; emits directories_selected
- Tabs:
  - Single Data (phase in FREQ; spectrum/filters in TIME)
  - Interface Data (T*/R* grouped)
  - Part Loads (side filter, exclusions, section/Tukey in TIME)
  - Time Domain Rep. (FREQ-only, θ reconstruction)
  - Compare Data / Compare Part Loads (overlay + Δ/%Δ)
  - Settings (envelope, fonts, hover, opacity)

Figure mockup

- Annotated screenshot of MainWindow with tab labels and callouts

Slide 9 — Key Features (Beta)

- Multi-folder grouping with clear legends
- Δ and %Δ comparisons (phase-aware in FREQ when Phase_ available)
- Rolling min–max envelope (TIME) for large datasets
- Spectrum over time (TIME) via rolling FFT
- ANSYS export: Harmonic (FREQ) & Transient (TIME) templates
- CSV export of combined data

Figure mockup

- Collage of three small plot thumbnails (single, compare, envelope)

Slide 10 — Demo Storyboard

- Load single TIME dataset; show Single Data plot
- Toggle spectrum; show Heatmap and Lines variants
- Switch to FREQ dataset; show phase plot and Time Domain Rep
- Compare two runs; show overlay + Δ + %Δ
- Export ANSYS template (harmonic or transient)

Figure mockup

- Five-panel storyboard with arrows showing the journey

Slide 11 — Performance, QA & Telemetry (Beta)

- Performance: Responsive plots; envelope for large time series
- Stability: Graceful error handling; safe fallbacks to empty figures
- QA: Manual test cases; scripts/test_dt.py for Δt validation
- Telemetry (optional): Usage feedback via support channel during beta

Figure mockup

- Table with KPIs and acceptance thresholds (e.g., load time, interactivity fps)

Slide 12 — Rollout Plan, Risks & Ask

- Pilot: X–Y teams; 2–4 weeks beta window
- Support: Dedicated Teams/Slack channel; office hours
- Docs: User guide + Architecture + DataFlow (docs/)
- Risks & mitigations:
  - Large datasets → use envelope; documented limits
  - ANSYS version mismatches → compatibility note; export on supported hosts
  - Data format drift → validation warnings; FAQ guidance
- Ask: Approval to proceed to Beta; confirm pilot roster; name support contacts

Figure mockup

- Timeline with milestones; risk matrix (impact vs likelihood)














