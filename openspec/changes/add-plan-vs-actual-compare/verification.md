| Scenario | Evidence |
|----------|----------|
| Demo mission includes a plan distinct from as-executed | `tests/test_api.py::test_plan_available`; fixtures write `msn-demo-strike-recon.plan.json` |
| Pair weapon releases despite slight time skew | `tests/test_api.py::test_compare_fuzzy_and_unplanned` (strike pair, δ=75s ≤ 90) |
| Unplanned as-executed action is unmatched | Same test: TGT-061 collect in `unmatched_actual` |
| Analyst reviews plan vs flown timeline | `docs/screenshots/09-plan-vs-actual-compare.png` — stacked tracks, linkages, glow, “10 paired · 1 unplanned” |
| Hide mission plan toggle | `docs/screenshots/10-compare-hide-plan.png` — plan track collapsed |
| Toggle planned route visibility | `docs/screenshots/11-planned-route-off.png` |
| Living design | `openspec/changes/add-plan-vs-actual-compare/` + `features/plan-vs-actual.feature` |
