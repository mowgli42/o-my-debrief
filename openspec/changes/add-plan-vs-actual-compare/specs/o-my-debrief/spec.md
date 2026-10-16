## ADDED Requirements

### Requirement: Mission plan persistence and query

The system SHALL persist a per-mission mission plan (planned route and planned
events) referenced from the mission manifest via `plan_path`. The API SHALL
expose `GET /api/plan?mission=…`. When no plan exists, the API SHALL return
HTTP 200 with `{ "available": false, "route": [], "events": [] }`.

#### Scenario: Demo mission includes a plan distinct from as-executed

- **GIVEN** fixtures generated for `msn-demo-strike-recon`
- **WHEN** client calls `GET /api/plan?mission=msn-demo-strike-recon`
- **THEN** response has `available=true`, a non-empty `route` of lat/lon points,
  and planned events including at least one planned strike and one planned collect
- **AND** at least one planned event timestamp differs from its closest as-executed
  peer by a non-zero delta within a few minutes

### Requirement: Fuzzy plan-vs-actual event compare

The API SHALL expose `GET /api/compare?mission=…&tolerance_seconds=…` (default 90)
that fuzzy-matches planned events to as-executed events of the same family
(strike, collect, BDA, dissemination, waypoint). Results SHALL include `pairs`
(with ids, family kind, `delta_seconds`), `unmatched_plan`, and `unmatched_actual`.

#### Scenario: Pair weapon releases despite slight time skew

- **GIVEN** a mission plan with a planned strike and an as-executed EXECUTED strike
  on the same `target_id` within the tolerance window
- **WHEN** client calls `GET /api/compare?mission=…&tolerance_seconds=90`
- **THEN** response `pairs` includes a strike pair linking those events
- **AND** `delta_seconds` is within 90

#### Scenario: Unplanned as-executed action is unmatched

- **GIVEN** an as-executed sensor collect (or strike) with no planned peer of the
  same family inside the tolerance
- **WHEN** client calls `/api/compare`
- **THEN** that event appears in `unmatched_actual`

### Requirement: Stacked plan / as-executed timeline compare view

The debrief display SHALL provide a Compare view with the mission-plan timeline
stacked above the as-executed timeline on a shared time axis. Paired events SHALL
show connecting linkages. Unplanned as-executed actions SHALL use a glowing icon.
A slide toggle SHALL hide the mission-plan track and linkages.

#### Scenario: Analyst reviews plan vs flown timeline

- **GIVEN** the demo mission with plan and as-executed data is loaded
- **WHEN** the user opens Compare view
- **THEN** the plan track appears above the as-executed track
- **AND** paired like events (e.g. weapon release to weapon release) show a
  connecting linkage
- **AND** unplanned as-executed markers glow
- **WHEN** the user turns on “Hide mission plan”
- **THEN** the plan track and linkages are hidden and only as-executed remains

### Requirement: Planned route under actual track on the map

The map SHALL render the planned route as a subdued polyline underneath the
actual flown track, with a toggle to show or hide the planned route only.

#### Scenario: Toggle planned route visibility

- **GIVEN** Compare or main map view with both planned route and actual track
- **WHEN** the planned-route toggle is on
- **THEN** a subdued planned polyline is visible beneath the actual track
- **WHEN** the toggle is turned off
- **THEN** the planned polyline is hidden and the actual track remains
