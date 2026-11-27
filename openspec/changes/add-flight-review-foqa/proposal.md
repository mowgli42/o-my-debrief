# Change: Flight Review (FOQA-style) workspace

## Why

The ISR dashboard covers sensor utilization well, but engineers and operators still
lack a single post-flight view that reconstructs **aircraft** performance alongside
sensor/mission activity on one clock—the FDM/FOQA pattern (synced plots, envelope
events, planned-vs-actual parameters).

## What changes (Phase 0–1 + FOQA event stub)

- **Flight Review** mode: one layout with shared scrub — geo track, multi-panel
  air-data (alt/speed/fuel/attitude), systems-health strip, sensor/mission strip.
- Preserve `currentTime` / `selectedEventId` when switching Debrief ↔ ISR ↔ Analysis
  ↔ Compare ↔ Flight Review (Phase 0 clock unification).
- Demo `systemStatus` enrichment: vertical speed, fuel flow, bus voltage, EGT proxy.
- `GET /api/analysis/flight-review` — air series + FOQA-style threshold events +
  rollup metrics for the workspace.
- Config `config/foqa-event-rules.yaml` for envelope detectors (datalink drop, high
  roll, low fuel, sensor fault linkage).

## Non-goals (this change)

- Multi-mission fleet trending
- Full FADEC / propulsion fidelity
- Live FDM uplink
- Replacing ISR / Analysis / Compare (they remain; Flight Review composes them)
- 3D trajectory viewer