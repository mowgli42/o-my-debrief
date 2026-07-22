# Tasks for Grok (or parallel agents)

Grok's design for `omd-h3a.8` is incorporated (`docs/MILESTONE-CLASSIFIER.md`,
`config/milestone-rules.yaml`). Implementation completed on branch
`cursor/incorporate-grok-c626` (including restore of `store.py` after a bad paste commit).

| Bead | Title | Status |
|------|-------|--------|
| `omd-h3a.8` | Milestone classifier YAML + BDA linkage | Done (this PR) |
| `omd-h3a.9` | Full track replay + map animation polish | Done (MVP interpolate + play) |
| `omd-h3a.10` | AI after-action summary | Done (rule-based + LLM hook) |
| `omd-h3a.11` | Live Redis vs o-my-sim | Done (XML normalize + unit tests; live manual) |

## Optional follow-ups (new beads / GitHub issues)

1. **Spline / heading-aware track** — Catmull-Rom or dead-reckoning between sparse status samples.
2. **Real local LLM AAR** — Wire `DEBRIEF_LLM_SUMMARY` adapter (Ollama) to replace rule narrative.
3. **CI live Redis job** — Compose profile that boots o-my-sim publishers + recorder for e2e.
4. **Map LOD / clustering** — When event counts exceed ~500 markers.

See also: `docs/OMY-SIM-INTEGRATION.md`.
