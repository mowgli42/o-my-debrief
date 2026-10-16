| Scenario | Evidence |
|----------|----------|
| Demo mission includes a plan distinct from as-executed | `make fixtures` + `GET /api/plan?mission=msn-demo-strike-recon`; unit test asserts route/events + time skew |
| Pair weapon releases despite slight time skew | `tests/test_api.py` (or `test_compare.py`) compare endpoint with tolerance=90 |
| Unplanned as-executed action is unmatched | Same test: assert event in `unmatched_actual` |
| Analyst reviews plan vs flown timeline | Manual / Playwright: Compare view, linkages, glow; screenshot under `docs/screenshots/` |
| Hide mission plan toggle | Manual: slide toggle hides plan track + linkages |
| Toggle planned route visibility | Manual: map subdued plan under actual; toggle off removes plan only |
| Living design | This change folder + `features/plan-vs-actual.feature` |
