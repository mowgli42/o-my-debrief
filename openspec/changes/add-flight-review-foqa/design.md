# Design: Flight Review FOQA

## Decisions

| Topic | Choice | Rationale |
| --- | --- | --- |
| Entry | Header **Flight Review** mode | Same pattern as ISR; keeps timeline as clock |
| Air-data plots | D3 multi-panel from track samples | Reuse octo-spork pattern; d3 already installed |
| Events | YAML rules over track + derived XTE | Mirrors milestone-rules; ponytail |
| Map | Reuse `MissionMap` | Avoid third map component for v1 |
| API | One `/api/analysis/flight-review` | Single fetch for shell |
| Report | Print-HTML five sections | Same pattern as PMR; no new PDF deps |
| Fleet | `/api/analysis/fleet-trends` | Manifest rollup; demo may have one mission |

## Phase map

- **0** Clock: modes share scrub/selection (App.svelte only)
- **1** Shell UI + flight-review API + demo airfields + FOQA events
- **2** Planned vs actual: XTE, cmd alt/spd, error series
- **3** Richer FOQA detectors + exceedance_stats
- **4** Aircraft health timeline
- **5** Five-section Flight Performance Report
- **6** Multi-mission fleet trends API + light UI
