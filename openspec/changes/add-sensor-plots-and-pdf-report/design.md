# Design: sensor plots + PMR

## Decisions

| Topic | Choice | Rationale |
| --- | --- | --- |
| Charting in UI | `d3` (same major as octo-spork) | Reuse multi-panel brush + scales; single new frontend dep |
| PMR delivery | FastAPI HTML + `@media print` CSS | No PDF engine dep; user Save as PDF from print dialog |
| FOV in PMR | Server-built SVG scatter | Deterministic report without headless browser |
| Telemetry source | `sensorStatus` rows in Parquet | Distinct from `systemStatus`; demo generator adds samples |
| LAR model | Circle envelope (`center`, `radius_nm`) + release point | Enough for demo scatter; polygon later if OMS schema adds it |

## Risks

- Legacy missions without enriched payloads return empty analysis points — UI shows
  graceful empty state; PMR still renders overview from milestones.
- D3 bundle size — acceptable for analyst workstation; not on critical path for MVP scrub.

## API sketch

- `sensor-collects`: `{ points[], metrics{ success_rate, tasked, collected, ... } }`
- `sensor-telemetry`: `{ samples[] }` keyed fields for panels
- `weapons-lar`: `{ releases[], lar_summary{ in_lar, total } }`