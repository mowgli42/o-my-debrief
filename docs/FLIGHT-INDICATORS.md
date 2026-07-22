# Flight Indicators (platform panel)

The platform status panel embeds **jQuery Flight Indicators** by Sébastien Matton:

- Demo: https://sebmatton.github.io/flightindicators/
- Source: https://github.com/sebmatton/jQuery-Flight-Indicators (GPLv3)

Vendored under `frontend/public/flightindicators/` (JS, CSS, SVG faces).

## Gauges shown

| Instrument | Driven by |
|------------|-----------|
| Airspeed | `platform.speed_kts` (needle clamped to classic 0–160 face; digital readout shows true kts) |
| Attitude | `platform.roll_deg`, `platform.pitch_deg` |
| Altimeter | `platform.alt_ft` |
| Heading | `platform.heading_deg` |

Svelte wrapper: `frontend/src/lib/FlightInstruments.svelte` (loads jQuery + plugin on mount, updates on scrub/play).
