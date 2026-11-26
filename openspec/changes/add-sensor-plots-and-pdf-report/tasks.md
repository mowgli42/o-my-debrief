## 1. Spec & fixtures

- [x] OpenSpec change + Gherkin `features/post-mission-analysis.feature`
- [x] Beads epic `omd-pmr` + child tasks
- [x] Demo generator: collect geometry, `sensorStatus`, strike LAR/release fields

## 2. API / store

- [x] `sensor_collect_analysis`, `sensor_telemetry_series`, `weapons_lar_analysis` in store
- [x] Routes: `/api/analysis/sensor-collects`, `sensor-telemetry`, `weapons-lar`
- [x] `/api/report/pmr` HTML template (3 pages, FOV SVG)
- [x] Extend `/api/summary` stats with analysis rollups
- [x] Unit tests

## 3. Frontend

- [x] Add `d3` dependency
- [x] `SensorFovPlot`, `WeaponsLarPlot`, `SensorStatePanels`, `AnalysisWorkbench`
- [x] Analysis mode toggle; PMR PDF button (print window)
- [x] `api.js` fetch helpers

## 4. Docs

- [x] BEADS.md epic row; README quick-start note
- [x] `verification.md` evidence matrix