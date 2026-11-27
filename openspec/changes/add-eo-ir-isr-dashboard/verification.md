# Verification: add-eo-ir-isr-dashboard

| Scenario | Evidence |
| --- | --- |
| ISR API payload | `test_analysis_sensor_isr` — fov 19, col 7, det 5, opp 4, faults 2 |
| Engineering / Operator UI | `docs/screenshots/17-isr-engineering.png`, `18-isr-operator.png` |
| Correlation inspector | `19-isr-event-inspector.png` — EO TGT-042 quality/pointing |
| Regression | `make test` — 21 passed |