## 1. Plan fixtures & models

- [x] Extend demo generator to write `<mission>.plan.json` (route + planned events with intentional time skew + one unplanned actual event)
- [x] Add `plan_path` (and optional planned waypoint list) on mission manifest
- [x] Pydantic models for `MissionPlan`, `PlanEvent`, `ComparePair`, `CompareResult`

## 2. API contracts

- [x] `GET /api/plan?mission=` — load plan sidecar; graceful empty when missing
- [x] `GET /api/compare?mission=&tolerance_seconds=` — fuzzy family matching
- [x] OpenAPI/Swagger docs for new endpoints
- [x] Unit tests: pairing with skew, unmatched actual, missing plan

## 3. Compare timeline UI

- [x] Compare mode entry in debrief shell (header control)
- [x] Stacked tracks: plan above as-executed, shared scrubber/playhead
- [x] SVG/CSS linkage lines between fuzzy pairs
- [x] Glow styling for unmatched as-executed markers
- [x] Slide toggle: Hide mission plan (collapses plan track + linkages)

## 4. Map planned route

- [x] Leaflet planned-route layer under actual track (subdued style)
- [x] Show/hide planned-route toggle
- [x] Wire plan route from `/api/plan`

## 5. Docs & verification

- [x] Gherkin scenarios in `features/` aligned with OpenSpec
- [x] Update `BEADS.md` / README status row when shipped
- [x] Fill `verification.md` evidence matrix (tests + manual/screenshot)
