## ADDED Requirements

### Requirement: Flight Review analysis API

The API SHALL expose `GET /api/analysis/flight-review?mission=…` returning:

- `air_series` time-ordered samples (altitude, speed, fuel, attitude, and available
  propulsion/electrical proxies)
- `events` FOQA-style threshold / anomaly events with timestamps and severity
- `metrics` rollups (duration, max alt, fuel start/end, event counts)
- Optional links to ISR / collect stats when present

#### Scenario: Demo mission returns flight-review payload

- **GIVEN** fixtures for `msn-demo-strike-recon`
- **WHEN** client calls `GET /api/analysis/flight-review?mission=msn-demo-strike-recon`
- **THEN** `air_series` has at least as many points as track samples
- **AND** `events` is a list (may include datalink or envelope events)
- **AND** `metrics.duration_min` is present

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