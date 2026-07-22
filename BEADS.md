# Task Beads — o-my Platform Debrief

Issue DB: `.beads/` · prefix `omd` · run `bd ready` / `bd list`.

## Epic

**`omd-h3a`** — MVP: Platform Debrief prototype  
Spec: `openspec/specs/o-my-debrief/spec.md`

### Implementation phases

| ID | Task |
|----|------|
| `omd-h3a.1` | Scaffold repo: Makefile, docker, openspec workflow, pyproject |
| `omd-h3a.2` | Demo mission generator → Parquet + manifest |
| `omd-h3a.3` | oms-recorder: Redis/JSONL → Parquet writer |
| `omd-h3a.4` | debrief-api: FastAPI `/missions` `/events` `/milestones` `/state_at` + Swagger |
| `omd-h3a.5` | debrief-display: Svelte timeline, milestones, map, vehicle status |
| `omd-h3a.6` | README with screenshots, architecture + sequence diagrams; Grok callouts |
| `omd-h3a.7` | Unit tests for demo parquet + API query endpoints |

### Call out for Grok

See **`docs/GROK-TASKS.md`**.

| ID | Task |
|----|------|
| `omd-h3a.8` | Milestone classifier rules YAML + richer BDA linkage |
| `omd-h3a.9` | Full track replay from position samples + map animation polish |
| `omd-h3a.10` | AI after-action summary from milestones (local LLM optional) |
| `omd-h3a.11` | Live Redis recorder integration test vs o-my-sim publishers |

## Workflow

```bash
bd ready
bd update <id> --claim
# … implement …
bd close <id>
```
