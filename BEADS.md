# Task Beads — o-my Platform Debrief

Issue DB: `.beads/` · prefix `omd` · run `bd ready` / `bd list`.

## Epic (shipped)

**`omd-h3a`** — MVP: Platform Debrief prototype (MVP phases closed)

### Follow-on (Grok inputs — closed)

| ID | Task | Notes |
|----|------|-------|
| `omd-h3a.8` | YAML classifier + BDA linkage | Design by Grok; implemented + `store.py` restored |
| `omd-h3a.9` | Track replay + map animation | `/api/track`, `/api/position_at`, smoother play |
| `omd-h3a.10` | AAR summary | Rule-based `/api/summary` + UI modal; LLM hook documented |
| `omd-h3a.11` | o-my-sim recorder fidelity | XML normalize + `tests/test_recorder.py` |

OpenSpec change: `openspec/changes/add-classifier-track-summary/`.

## Epic (open): Plan vs as-executed

**`omd-2ek`** — Plan vs as-executed compare (timeline + map)

OpenSpec: [`openspec/changes/add-plan-vs-actual-compare/`](openspec/changes/add-plan-vs-actual-compare/) · Gherkin: [`features/plan-vs-actual.feature`](features/plan-vs-actual.feature)

| ID | Task | Status |
|----|------|--------|
| `omd-2ek.1` | Demo plan fixtures + `plan_path` on manifest | closed |
| `omd-2ek.2` | API: `GET /api/plan` + `GET /api/compare` fuzzy pairing | closed |
| `omd-2ek.3` | UI: stacked Compare timeline, linkages, hide-plan toggle | closed |
| `omd-2ek.4` | Map: subdued planned route under actual + toggle | closed |
| `omd-2ek.5` | Docs + verification | closed |

## Workflow

```bash
bd ready
bd update <id> --claim
bd close <id>
bd dolt push   # sync beads data when remote configured
```
