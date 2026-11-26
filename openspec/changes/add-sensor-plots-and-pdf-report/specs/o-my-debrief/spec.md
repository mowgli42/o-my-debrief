## ADDED Requirements

### Requirement: Sensor collect geometry analysis

The API SHALL expose `GET /api/analysis/sensor-collects?mission=…` returning each
successful `sensorCollect` with slant/ground range and footprint geometry
(diameter, area, and/or cone angle) plus roll-up metrics (counts, success rate,
tasked vs collected when plan data exists).

The debrief display SHALL render an interactive scatter or comparable plot of
collect range vs footprint/cone in Analysis mode and SHALL use the same metrics
in the Post Mission Report.

#### Scenario: Demo mission exposes collect geometry points

- **GIVEN** fixtures for `msn-demo-strike-recon` with enriched collect payloads
- **WHEN** client calls `GET /api/analysis/sensor-collects?mission=msn-demo-strike-recon`
- **THEN** `points` includes at least four entries with non-null range and footprint fields
- **AND** `metrics.success_rate` is between 0 and 1

### Requirement: Weapons release vs LAR analysis

The API SHALL expose `GET /api/analysis/weapons-lar?mission=…` listing each weapon
release (EXECUTED strike task) with release geometry relative to a LAR envelope
and summary compliance counts.

The debrief display SHALL visualize release points against the LAR envelope with
summary metrics in Analysis mode.

#### Scenario: Demo strike release inside LAR

- **GIVEN** the demo mission with an EXECUTED strike carrying LAR and release fields
- **WHEN** client calls `GET /api/analysis/weapons-lar?mission=msn-demo-strike-recon`
- **THEN** `releases` has at least one entry with `within_lar=true`
- **AND** `lar_summary` reports compliance totals

### Requirement: Time-aligned sensor state plots

The API SHALL expose `GET /api/analysis/sensor-telemetry?mission=…` with
time-ordered samples suitable for multi-panel plots (health, mode, status, and
related numeric telemetry).

The debrief display SHALL show time-aligned sensor-state panels adapted from the
refactored-octo-spork multi-panel pattern, synchronized with mission duration.

#### Scenario: Sensor telemetry series for demo mission

- **GIVEN** demo parquet includes `sensorStatus` events
- **WHEN** client calls `GET /api/analysis/sensor-telemetry?mission=msn-demo-strike-recon`
- **THEN** `samples` length is greater than 5
- **AND** each sample includes `timestamp`, `sensor`, and `health`

### Requirement: Three-page Post Mission Report (PMR)

The API SHALL expose `GET /api/report/pmr?mission=…` returning print-ready HTML
with exactly three pages:

1. Mission Overview (route/waypoints summary, key times, collection and weapons summary)
2. Platform and Sensor Health (uptime/degradation highlights)
3. Two-column layout: sensor FOV/distance plot (SVG) and supporting metrics
   (uptime, tasked vs collected, dissemination, LAR notes)

The debrief display SHALL provide **Generate Post Mission Report (PDF)** that opens
this document and invokes the browser print dialog for PDF export.

#### Scenario: PMR HTML contains three page sections

- **GIVEN** the demo mission is loaded
- **WHEN** client calls `GET /api/report/pmr?mission=msn-demo-strike-recon`
- **THEN** response `Content-Type` is `text/html`
- **AND** body includes headings for Mission Overview, Platform and Sensor Health,
  and a third page with FOV plot and detail columns