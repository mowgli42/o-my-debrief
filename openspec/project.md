# o-my-debrief — project context

## Mission

Capture OMS bus messages from o-my / o-my-sim, persist to Parquet, query via FastAPI,
and visualize in a Svelte debrief station (timeline ◆/▶, milestones, map, vehicle status).

## Stack

| Layer | Choice |
|-------|--------|
| Recorder | Python asyncio + redis (optional) / demo JSONL → Parquet (pyarrow) |
| API | FastAPI + Pydantic + pyarrow reads |
| UI | Svelte 5 + Vite + Tailwind + Leaflet |
| Tracking | Beads (`bd`) + OpenSpec + Gherkin |

## Related repos

- `o-my` — C2 / UCI bus processors
- `o-my-sim` — publishers / scenario clock
- `fuzzy-reconciler` — reference OpenSpec + Svelte/FastAPI layout
- `battlespace-manager` — potential display consumer

## Conventions

- Topics align with `uci_common.topics` (`uci.platform.status`, `uci.task`, …).
- Demo mission id: `msn-demo-strike-recon`.
- API base path: `/api/*`, Swagger at `/docs`.
- Data root: `DEBRIEF_DATA_DIR` (default `data/debrief`).
