## 1. Spec

- [x] OpenSpec change + Gherkin `features/flight-review-foqa.feature`
- [x] Beads epic `omd-foqa`

## 2. Data + API (phases 1–6)

- [x] Demo systemStatus: vs_fpm, fuel_flow_pph, bus_v, egt_c
- [x] Plan route cmd_alt_ft / cmd_speed_kts
- [x] `config/foqa-event-rules.yaml` + derived XTE rule
- [x] `store.flight_review_analysis` (XTE, errors, exceedance, health_timeline)
- [x] `GET /api/analysis/flight-review`
- [x] `GET /api/report/flight-performance` five-section HTML
- [x] `GET /api/analysis/fleet-trends`
- [x] Unit tests

## 3. UI

- [x] Flight Review mode; keep scrub/selection across mode switches
- [x] `FlightAirDataPanels` (+ planned-vs-actual panel), `FlightReviewDashboard`
- [x] Health timeline strip, exceedance counts, fleet trends, report button
- [x] Screenshots 20–24

## 4. Docs

- [x] BEADS.md + README + verification.md
