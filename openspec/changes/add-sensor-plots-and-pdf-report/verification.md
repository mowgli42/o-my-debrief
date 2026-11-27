# Verification: add-sensor-plots-and-pdf-report

| Scenario (Gherkin / spec) | Evidence |
| --- | --- |
| Sensor FOV vs range plot in UI | `docs/screenshots/12-analysis-fov-lar.png` — 7/7 collects, scatter + LAR |
| Weapons release vs LAR | API smoke `1/1 in_lar`; screenshot 12 LAR envelope |
| Sensor state multi-panel | `docs/screenshots/13-analysis-sensor-telemetry.png` — fuel + datalink dip |
| PMR 3-page structure | `14`–`16` screenshots; `/api/report/pmr` headings verified |
| Summary rollups | `test_summary_analysis_rollups` |
| Regression | `make test` — 20 passed (2026-11-26) |