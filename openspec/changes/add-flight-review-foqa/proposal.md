# Change: Flight Review (FOQA-style) workspace

## Why

The ISR dashboard covers sensor utilization well, but engineers and operators still
lack a single post-flight view that reconstructs **aircraft** performance alongside
sensor/mission activity on one clock—the FDM/FOQA pattern (synced plots, envelope
events, planned-vs-actual parameters).

## What changes (Phases 0–6)

- **Flight Review** mode: shared scrub — geo track, multi-panel air-data (alt/speed/
  fuel/attitude + planned-vs-actual errors), systems-health strip, sensor strip.
- Preserve `currentTime` / `selectedEventId` across Debrief ↔ ISR ↔ Analysis ↔
  Compare ↔ Flight Review (Phase 0 clock unification).
- Demo `systemStatus` enrichment: VS, fuel flow, bus V, EGT; plan `cmd_alt_ft` /
  `cmd_speed_kts` for parameter compare.
- `GET /api/analysis/flight-review` — air series, XTE / cmd errors, FOQA events,
  exceedance stats, health timeline, planned-vs-actual rollups.
- `config/foqa-event-rules.yaml` — datalink, roll, fuel, bus, EGT, VS, XTE, sensor fault.
- `GET /api/report/flight-performance` — five-section print-HTML report.
- `GET /api/analysis/fleet-trends` — multi-mission rollup (demo may be one mission).

## Non-goals (this change)

- Full FADEC / propulsion fidelity
- Live FDM uplink
- Replacing ISR / Analysis / Compare (they remain; Flight Review composes them)
- 3D trajectory viewer
