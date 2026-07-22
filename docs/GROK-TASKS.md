# Tasks for Grok (or parallel agents)

These beads are labeled `grok` and are intentionally left open for exploratory /
design-heavy work while the MVP prototype lands on Composer/Cursor.

| Bead | Title | Why Grok |
|------|-------|----------|
| `omd-h3a.8` | Milestone classifier rules YAML + richer BDA linkage | Config DSL design, rule edge cases, target_id graph linking |
| `omd-h3a.9` | Full track replay + map animation polish | Interpolation math, LOD/clustering, animation feel |
| `omd-h3a.10` | AI after-action summary from milestones | Prompt/schema design for optional local LLM AAR narrative |
| `omd-h3a.11` | Live Redis recorder integration vs o-my-sim | Cross-repo topic fidelity, XML/JSON message normalization |

## Suggested prompts for Grok

1. **Classifier YAML** — Propose a YAML schema for milestone rules covering
   `sensor_collect`, `dissemination`, `strike_executed`, `bda_positive`,
   `datalink_lost`. Include GIVEN/WHEN/THEN examples that map to
   `features/o-my-debrief.feature`.

2. **BDA linkage** — Given strike EXECUTED + later BDA with same `target_id`,
   design how the API should return a linked milestone chain without breaking
   the current `/api/milestones` response shape.

3. **Track replay** — Spec an algorithm to interpolate lat/lon/heading between
   `systemStatus` samples for smooth map play at 10–30× realtime.

4. **o-my-sim live capture** — List exact Redis topics and payload fields from
   `o-my-sim` publishers that the recorder must normalize into the Parquet schema
   in `src/omy_debrief/demo/generate.py` (`SCHEMA`).

Claim with: `bd update <id> --claim`
