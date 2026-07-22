# Flight Indicators (Launch / Recovery tab)

The platform status panel keeps **Mission** ops (waypoint, tasks, weapons, payload) free of cockpit clutter. Flight instruments live on the **Launch / Recovery** tab with an altitude climb/descent profile and gear/systems status.

Instruments use **jQuery Flight Indicators** by Sébastien Matton:

- Demo: https://sebmatton.github.io/flightindicators/
- Source: https://github.com/sebmatton/jQuery-Flight-Indicators (GPLv3)

Vendored under `frontend/public/flightindicators/` (JS, CSS, SVG faces).

## Panel tabs

| Tab | Contents |
|-----|----------|
| Mission | Waypoint, fuel, datalink, readiness, payload, weapons, assigned tasks |
| Launch / Recovery | Altitude profile (climb / level / descent), landing gear & bay, aircraft systems, ASI / attitude / altimeter / HDG |

When landing gear is **down**, the Launch / Recovery tab is selected automatically (until the operator picks a tab manually). A small amber dot appears on the tab while gear is down and another tab is active.

## Gauges shown

| Instrument | Driven by |
|------------|-----------|
| Airspeed | `platform.speed_kts` (needle clamped to classic 0–160 face; digital readout shows true kts) |
| Attitude | `platform.roll_deg`, `platform.pitch_deg` |
| Altimeter | `platform.alt_ft` |
| Heading | `platform.heading_deg` |

## Altitude profile

SVG chart of `track[].alt_ft` vs time from `/api/track`, with climb/level/descent shading and a scrub cursor at the current debrief time.

Svelte: `frontend/src/lib/FlightInstruments.svelte`, `AltitudeProfile.svelte`, tab shell in `VehicleStatus.svelte`.
