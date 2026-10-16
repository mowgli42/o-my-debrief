# Design: Plan vs as-executed compare

## Decisions

1. **Plan as sidecar JSON, not Parquet** — Store `data/debrief/<mission_id>.plan.json`
   (path recorded on the mission manifest as `plan_path`). Keeps as-executed
   Parquet append-only and avoids schema churn. Manifest already carries
   waypoints; planned route may reuse or override those coordinates.

2. **Reuse event shapes** — Planned events use the same fields as `DebriefEvent`
   (`event_type`, `marker`, `target_id`, `sensor`, `lat`/`lon`, `timestamp`,
   `summary`) plus `plan_event_id`. No new marker glyphs for plan; plan row uses
   muted styling.

3. **Fuzzy pairing (server-side)** — `GET /api/compare?mission=&tolerance_seconds=`
   (default **90**) returns:
   - `pairs[]`: `{ plan_event_id, actual_event_id, kind, delta_seconds, score }`
   - `unmatched_plan[]`, `unmatched_actual[]` (unplanned = unmatched actual of
     comparable kinds)
   Matching is greedy 1:1 within each **family**:
   - `strike` — task EXECUTED / weapon release (caret)
   - `collect` — sensorCollect (optionally same `sensor`)
   - `bda` — bda / bda_positive
   - `dissem` — dissemination
   - `waypoint` — waypoint reached  
   Score: time proximity inside tolerance; boost when `target_id` matches.
   `ponytail:` O(n·m) per family is fine for demo-scale missions; upgrade to
   interval index if missions grow past ~1k comparable events.

4. **Compare lives in the existing shell** — Header control enters Compare mode
   (not a separate SPA route). Timeline becomes two stacked tracks sharing one
   scrubber/playhead. Hide-plan slide toggle collapses the plan track and
   linkage SVG; as-executed remains.

5. **Map layering** — Planned route: subdued dashed polyline (e.g. slate/cyan at
   low opacity), added to a Leaflet layer **below** the actual track layer.
   Toggle only affects the planned-route layer; waypoints/events unchanged
   unless product polish says otherwise.

6. **Demo deltas** — Generator writes a plan that is close but not identical:
   planned strike ~60–120s earlier/later than EXECUTED, planned collects near
   actuals, plus **one unplanned** as-executed collect or opportunistic release
   so glow/unmatched paths are testable without Redis.

## Risks

- If a mission has no `plan_path`, Compare mode shows an empty plan track and
  disables pairing (UI copy: “No mission plan for this mission”).
- Fuzzy false pairs when two same-kind events fall inside the window — mitigated
  by target_id boost and greedy closest-first; expose `tolerance_seconds` for
  analysts.
- Dual timeline height may crowd the map on short viewports — collapse plan via
  the required toggle; keep lanes compact.
