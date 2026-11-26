# Change: Sensor collect / LAR analysis plots + multi-page PMR PDF

## Why

Post-mission debrief needs richer analysis than timeline milestones: how collection
geometry varied with slant range and footprint, whether weapon releases fell inside
the Launch Acceptability Region (LAR), and time-aligned sensor health telemetry.
Analysts also need a compact, shareable three-page Post Mission Report (PMR) for
staff briefings without manually stitching screenshots.

## What changes

- Demo generator enriches `sensorCollect` payloads (slant/ground range, footprint,
  cone angle), periodic `sensorStatus` telemetry, and strike LAR + release geometry.
- API: `GET /api/analysis/sensor-collects`, `/api/analysis/sensor-telemetry`,
  `/api/analysis/weapons-lar`; extend `/api/summary` stats with analysis rollups.
- `GET /api/report/pmr?mission=` — print-ready HTML (3-page layout + embedded FOV SVG).
- Debrief UI: **Analysis** mode with D3 FOV scatter, weapons LAR chart, and
  time-aligned sensor-state multi-panel (adapted from refactored-octo-spork).
- **Generate Post Mission Report (PDF)** opens PMR HTML and triggers browser print.

## Non-goals

- Server-side PDF rasterization (WeasyPrint, wkhtmltopdf) unless already on stack
- Editing LAR envelopes or re-tasking in the UI
- Embedding the sensor video player in analysis or PMR pages
- Multi-mission PDF bundles