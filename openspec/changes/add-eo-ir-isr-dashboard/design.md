# Design: EO/IR ISR dashboard

## Decisions

| Topic | Choice | Rationale |
| --- | --- | --- |
| Entry | Header **ISR** mode (alongside Analysis / Compare) | Keeps scrub + milestones; swaps center+right for ISR layout |
| Map | New `IsrSensorMap.svelte` (Leaflet) | Avoid overloading MissionMap; reuse basemap tiles |
| Data | One `/api/analysis/sensor-isr` payload | Single fetch; eng/ops share same events |
| Footprints | Ground circles + optional polygon rings in payload | Demo-scale; enough to show FOR vs collect |
| Modes | `engineering` \| `operator` toggle | Shared map/time; swap side metrics + layer emphasis |
| Ponytail | No new deps beyond existing Leaflet + D3 | YAGNI |

## Correlation model

Each ISR event carries `timestamp`, `lat`/`lon`, optional `footprint`, `pointing`,
`quality`, `health`, `outcome`. Scrub time filters “active” FOV; click sets
`selectedEventId` shared with debrief clock.