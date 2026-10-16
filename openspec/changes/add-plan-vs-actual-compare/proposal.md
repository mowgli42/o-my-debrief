# Change: Plan vs as-executed compare (timeline + map)

## Why

Analysts need to see how the flown mission differed from the briefed plan:
which weapon releases and collects lined up, which actions were unplanned, and
how the flown track diverged from the planned route. Today the debrief shows
only as-executed events and a single route polyline (manifest waypoints) with
no plan layer, no pairing, and no unplanned highlighting.

## What changes

- Persist a per-mission **mission plan** (planned route + planned events) alongside
  as-executed Parquet; extend the demo generator so plan ≠ actual (time skew +
  one unplanned action).
- API: `GET /api/plan` and `GET /api/compare` with fuzzy event pairing within a
  configurable time tolerance.
- UI **Compare** view: stacked mission-overview timeline (plan above as-executed),
  linkage lines between fuzzy-paired like events, glowing icons for unplanned
  as-executed actions, and a slide toggle to hide the mission plan.
- Map: subdued planned route drawn **under** the actual flown track, with a
  show/hide planned-route toggle.

## Non-goals

- Multi-mission side-by-side compare across different mission IDs
- Editing / authoring mission plans in the UI
- Full OMS mission-plan schema import from o-my C2 (demo/sidecar JSON is enough)
- Automatic scoring / grade of mission success beyond pair/unmatched lists
- LLM narrative of plan deviations (can feed `/api/summary` later)
