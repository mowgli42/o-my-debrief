# Task Beads — o-my Platform Debrief

Issue DB: `.beads/` · prefix `omd` · run `bd ready` / `bd list`.

## Epic

**`omd-h3a`** — MVP: Platform Debrief prototype (MVP phases closed)

### Follow-on (Grok inputs incorporated)

| ID | Task | Notes |
|----|------|-------|
| `omd-h3a.8` | YAML classifier + BDA linkage | Design by Grok; implemented + `store.py` restored |
| `omd-h3a.9` | Track replay + map animation | `/api/track`, `/api/position_at`, smoother play |
| `omd-h3a.10` | AAR summary | Rule-based `/api/summary` + UI modal; LLM hook documented |
| `omd-h3a.11` | o-my-sim recorder fidelity | XML normalize + `tests/test_recorder.py` |

OpenSpec change: `openspec/changes/add-classifier-track-summary/`.

## Workflow

```bash
bd ready
bd update <id> --claim
bd close <id>
```
