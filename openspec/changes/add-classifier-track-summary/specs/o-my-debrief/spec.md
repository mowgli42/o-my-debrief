## ADDED Requirements

### Requirement: Config-driven milestone classifier with BDA linkage

The system SHALL load milestone rules from YAML (`DEBRIEF_RULES` or `config/milestone-rules.yaml`)
and classify events into milestones. When YAML is absent or no rule matches, the system SHALL
fall back to the hardcoded classifier. BDA milestones SHALL optionally link to a prior strike
EXECUTED event on the same `target_id` within a configurable time window, exposing
`linked_to_strike`, `linked_strike_event_id`, and `link_note` without breaking existing clients.

#### Scenario: YAML rules classify demo mission and link BDA

- **GIVEN** demo parquet for `msn-demo-strike-recon` and `config/milestone-rules.yaml`
- **WHEN** client calls `GET /api/milestones?mission=msn-demo-strike-recon`
- **THEN** response includes `sensor_collect`, `strike_executed`, and `bda_positive` (or `bda`) kinds
- **AND** at least one BDA milestone has `linked_to_strike=true` and a `linked_strike_event_id`

### Requirement: Interpolated track replay

The API SHALL expose raw track samples from `systemStatus` positions and an interpolated
position at an arbitrary scrub time for smooth map replay.

#### Scenario: Interpolate between status samples

- **GIVEN** a mission with multiple systemStatus positions
- **WHEN** client calls `GET /api/position_at?mission=…&time=` between two samples
- **THEN** response includes lat/lon with `interpolated=true`

### Requirement: Rule-based after-action summary

The API SHALL provide `GET /api/summary?mission=…` returning a deterministic narrative and
stats derived from milestones, with an explicit optional LLM hook for future adapters.

#### Scenario: Summary covers strike and BDA

- **GIVEN** a completed demo mission
- **WHEN** client calls `/api/summary`
- **THEN** narrative mentions strike/BDA outcomes and `generator` is `rule-based`

### Requirement: o-my-sim XML normalization in recorder

The recorder SHALL accept Redis message bodies that are OMS XML (PlatformStatusReport) and
normalize them into the Parquet schema with fuel, position, and readiness fields.

#### Scenario: PlatformStatusReport XML → systemStatus row

- **GIVEN** an o-my-sim-shaped PlatformStatusReport XML string on topic `uci.platform.status`
- **WHEN** `normalize_message` is invoked
- **THEN** event_type is `systemStatus` with lat/lon/fuel extracted
