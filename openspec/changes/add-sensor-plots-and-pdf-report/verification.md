# Verification: add-sensor-plots-and-pdf-report

| Scenario (Gherkin / spec) | Evidence |
| --- | --- |
| Sensor FOV vs range plot in UI | `SensorFovPlot.svelte`; manual Analysis mode on demo mission |
| Weapons release vs LAR | `WeaponsLarPlot.svelte`; `/api/analysis/weapons-lar` test |
| Sensor state multi-panel | `SensorStatePanels.svelte`; demo `sensorStatus` rows |
| PMR 3-page structure | `/api/report/pmr` HTML; print preview Page 1–3 headings |
| Summary rollups | `test_summary` + analysis fields in response |
| Regression | `make test` green |