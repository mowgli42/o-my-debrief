# Verification: add-flight-review-foqa

| Scenario | Evidence |
| --- | --- |
| Flight-review API | `test_analysis_flight_review` — air 8, datalink_drop/bus_low/sensor_fault |
| Shared clock | `setExclusiveMode` does not reset `currentTime` |
| Air-data panels | `docs/screenshots/20-flight-review.png` |
| FOQA event select | `docs/screenshots/21-flight-review-foqa-event.png` |
| Regression | `make test` — 22 passed |