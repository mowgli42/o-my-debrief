# Design: Flight Review FOQA

## Decisions

| Topic | Choice | Rationale |
| --- | --- | --- |
| Entry | Header **Flight Review** mode | Same pattern as ISR; keeps timeline as clock |
| Air-data plots | D3 multi-panel from track samples | Reuse octo-spork pattern; d3 already installed |
| Events | YAML rules over track + known OMS events | Mirrors milestone-rules; ponytail |
| Map | Reuse `MissionMap` | Avoid third map component for v1 |
| API | One `/api/analysis/flight-review` | Single fetch for shell |

## Phase map

- **0** Clock: modes share scrub/selection (App.svelte only)
- **1** Shell UI + flight-review API + demo airfields + FOQA events
- Later: XTE series, PMR five-section report, fleet trends