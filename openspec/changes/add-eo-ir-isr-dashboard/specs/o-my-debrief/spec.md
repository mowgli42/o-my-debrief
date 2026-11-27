## ADDED Requirements

### Requirement: EO/IR ISR analysis API

The API SHALL expose `GET /api/analysis/sensor-isr?mission=…` returning:

- `track` samples with aircraft position
- `fov_history` ground footprints (observability over time)
- `collections` successful image footprints with quality metrics
- `detections` with timestamps and locations
- `opportunities` observable-but-uncollected / unused collection opportunities
- `faults` hardware/software/anomaly events
- `engineering` rollup metrics (uptime, pointing error, quality, latency, faults)
- `operator` rollup metrics (observe %, FOV util, opportunities vs collects, revisits)
- `events` correlatable list for timeline/inspector

#### Scenario: Demo mission ISR payload is populated

- **GIVEN** fixtures for `msn-demo-strike-recon`
- **WHEN** client calls `GET /api/analysis/sensor-isr?mission=msn-demo-strike-recon`
- **THEN** `fov_history` and `collections` are non-empty
- **AND** `engineering.uptime_pct` and `operator.observe_pct` are present
- **AND** at least one detection and one opportunity appear

### Requirement: ISR dashboard with Engineering and Operator modes

The debrief display SHALL provide an **ISR** mode with a large central geospatial
map showing flight path, sensor pointing, FOV footprints, detections, collections,
and uncollected opportunities. Users SHALL switch between Engineering and Operator
perspectives without losing current time or map selection. Selecting an ISR event
SHALL update the inspector and scrub context.

#### Scenario: Analyst switches Engineering to Operator

- **GIVEN** the demo mission is loaded and ISR mode is open
- **WHEN** the user selects Operator mode
- **THEN** operator utilization metrics are shown
- **AND** the map and scrub time remain at the prior context
- **WHEN** the user selects a collection footprint
- **THEN** the inspector shows geometry, quality, and health for that event