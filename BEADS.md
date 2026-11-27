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

## Epic: Post-mission analysis + PMR PDF

**`omd-pmr`** — Sensor FOV plots, LAR analysis, sensor telemetry panels, 3-page PMR

OpenSpec: [`openspec/changes/add-sensor-plots-and-pdf-report/`](openspec/changes/add-sensor-plots-and-pdf-report/) · Gherkin: [`features/post-mission-analysis.feature`](features/post-mission-analysis.feature)

| ID | Task | Status |
|----|------|--------|
| `omd-pmr.1` | Demo geometry + sensorStatus + LAR payloads | closed |
| `omd-pmr.2` | Analysis API + `/api/report/pmr` | closed |
| `omd-pmr.3` | Analysis UI (D3) + PMR print button | closed |
| `omd-pmr.4` | Tests + docs | closed |

## Epic: EO/IR ISR dashboard

**`omd-isr`** — Airborne EO/IR sensor performance & utilization (eng + ops)

OpenSpec: [`openspec/changes/add-eo-ir-isr-dashboard/`](openspec/changes/add-eo-ir-isr-dashboard/) · Gherkin: [`features/eo-ir-isr-dashboard.feature`](features/eo-ir-isr-dashboard.feature)

| ID | Task | Status |
|----|------|--------|
| `omd-isr.1` | Demo FOV / detections / opportunities / faults | closed |
| `omd-isr.2` | `GET /api/analysis/sensor-isr` | closed |
| `omd-isr.3` | ISR UI map + Engineering/Operator modes | closed |
| `omd-isr.4` | Tests + screenshots | closed |

## Epic (open): Flight Review FOQA

**`omd-foqa`** — Synced flight review (air-data + health + FOQA events) on one clock

OpenSpec: [`openspec/changes/add-flight-review-foqa/`](openspec/changes/add-flight-review-foqa/) · Gherkin: [`features/flight-review-foqa.feature`](features/flight-review-foqa.feature)

| ID | Task | Status |
|----|------|--------|
| `omd-foqa.1` | OpenSpec + demo airframe proxies + FOQA rules | closed |
| `omd-foqa.2` | `GET /api/analysis/flight-review` | closed |
| `omd-foqa.3` | Flight Review UI + shared scrub | closed |
| `omd-foqa.4` | Tests + screenshots | closed |

## Workflow

```bash
bd ready
bd update <id> --claim
bd close <id>
bd dolt push   # sync beads data when remote configured
```
