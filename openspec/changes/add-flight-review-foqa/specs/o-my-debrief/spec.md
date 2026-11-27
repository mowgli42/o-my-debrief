## ADDED Requirements

### Requirement: Flight Review analysis API

The API SHALL expose `GET /api/analysis/flight-review?mission=…` returning:

- `air_series` time-ordered samples (altitude, speed, fuel, attitude, propulsion/
  electrical proxies, and planned-vs-actual fields: `cmd_alt_ft`, `cmd_speed_kts`,
  `alt_error_ft`, `spd_error_kts`, `xte_nm`)
- `events` FOQA-style threshold / anomaly events with timestamps and severity
- `metrics` rollups (duration, max alt, fuel start/end, event counts,
  `exceedance_stats`)
- `health_timeline` per-sample systems flags (datalink, bus, EGT, fuel band)
- `planned_vs_actual` rollup (mean/max XTE, mean abs alt/spd error)
- Optional links to ISR / collect stats when present

#### Scenario: Demo mission returns flight-review payload

- **GIVEN** fixtures for `msn-demo-strike-recon`
- **WHEN** client calls `GET /api/analysis/flight-review?mission=msn-demo-strike-recon`
- **THEN** `air_series` has at least as many points as track samples
- **AND** samples include `xte_nm` and `cmd_alt_ft` when a plan exists
- **AND** `events` includes envelope detectors (e.g. datalink / XTE)
- **AND** `metrics.duration_min` and `exceedance_stats` are present
- **AND** `health_timeline` has matching sample count

### Requirement: Flight Performance Report

The API SHALL expose `GET /api/report/flight-performance?mission=…` returning
printable HTML with five sections: Flight overview, Aircraft performance, Systems
health, Mission execution, Post-flight assessment.

#### Scenario: Demo mission flight performance report

- **GIVEN** fixtures for `msn-demo-strike-recon`
- **WHEN** client calls `GET /api/report/flight-performance?mission=msn-demo-strike-recon`
- **THEN** the HTML includes all five section headings

### Requirement: Fleet trends rollup

The API SHALL expose `GET /api/analysis/fleet-trends` returning per-mission FOQA /
sensor rollups across the manifest plus aggregates.

#### Scenario: Manifest fleet trends

- **GIVEN** at least one mission in the manifest
- **WHEN** client calls `GET /api/analysis/fleet-trends`
- **THEN** `missions` is a non-empty list
- **AND** `aggregates` includes warn and collection totals

### Requirement: Flight Review workspace with shared clock

The debrief display SHALL provide a **Flight Review** mode that shows synchronized
geographic track, multi-panel air-data plots, a systems-health summary, and
sensor/mission highlights driven by the same scrub time and selection as other modes.
Switching between Flight Review, ISR, Analysis, and Compare SHALL NOT reset
`currentTime`.

#### Scenario: Analyst opens Flight Review and scrubs

- **GIVEN** the demo mission is loaded
- **WHEN** the user opens Flight Review
- **THEN** air-data panels and map reflect the current scrub time
- **WHEN** the user scrubs the timeline
- **THEN** air-data cursor and map position update together
- **WHEN** the user switches to ISR and back
- **THEN** the scrub time is unchanged