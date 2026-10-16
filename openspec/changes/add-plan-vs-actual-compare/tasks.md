## 1. Plan fixtures & models

- [ ] Extend demo generator to write `<mission>.plan.json` (route + planned events with intentional time skew + one unplanned actual event)
- [ ] Add `plan_path` (and optional planned waypoint list) on mission manifest
- [ ] Pydantic models for `MissionPlan`, `PlanEvent`, `ComparePair`, `CompareResult`

## 2. API contracts

- [ ] `GET /api/plan?mission=` — load plan sidecar; graceful empty when missing
- [ ] `GET /api/compare?mission=&tolerance_seconds=` — fuzzy family matching
- [ ] OpenAPI/Swagger docs for new endpoints
- [ ] Unit tests: pairing with skew, unmatched actual, missing plan

## 3. Compare timeline UI

- [ ] Compare mode entry in debrief shell (header control)
- [ ] Stacked tracks: plan above as-executed, shared scrubber/playhead
- [ ] SVG/CSS linkage lines between fuzzy pairs
- [ ] Glow styling for unmatched as-executed markers
- [ ] Slide toggle: Hide mission plan (collapses plan track + linkages)

## 4. Map planned route

- [ ] Leaflet planned-route layer under actual track (subdued style)
- [ ] Show/hide planned-route toggle
- [ ] Wire plan route from `/api/plan`

## 5. Docs & verification

- [ ] Gherkin scenarios in `features/` aligned with OpenSpec
- [ ] Update `BEADS.md` / README status row when shipped
- [ ] Fill `verification.md` evidence matrix (tests + manual/screenshot)
