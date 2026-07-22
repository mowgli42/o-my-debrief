# o-my Platform Debrief

**Platform Debrief capability for the Open Arsenal o-my OMS ecosystem.**

Captures live or simulated OMS bus messages (systemStatus, sensorStatus, tasks, BDA, etc.) from o-my Redis topics. Persists to Parquet for efficient time-based queries. Exposes via FastAPI/Swagger. Renders in a purpose-built Svelte web debrief station featuring:

- Interactive timeline with ◆ diamonds for sensor collects and ▶ carets for strike tasks
- Stacked key milestones panel (left)
- Simple route/task map (center)
- Vehicle/platform status display (fuel, datalink, payload, weapons, gear/bay)

Enables pilots and analysts to quickly understand collection, dissemination, strike execution, and verification outcomes.

## Quickstart (once implemented)

```bash
# After cloning
make dev          # or docker compose up
# Open http://localhost:5173 (frontend) or API docs at :8000/docs
```

See `openspec/specs/o-my-debrief/spec.md` for the complete specification, requirements, and scenarios.

See `features/o-my-debrief.feature` for Gherkin acceptance criteria.

This repository follows the established **OpenSpec + Gherkin + Beads** workflow (as in fuzzy-reconciler, battlespace-manager, schwerpunkt). Use Cursor/Claude with the provided specs and beads issues for implementation.

## Components

1. **oms-recorder** (or data-recorder/): Redis listener + Parquet writer
2. **debrief-api**: FastAPI Parquet reader with time/milestone queries + Swagger
3. **debrief-display**: Svelte 5 frontend (timeline, map, status panels)

## Status

- [x] Spec & Gherkin defined
- [ ] Beads issues created / implementation started
- [ ] Recorder prototype
- [ ] API + Swagger
- [ ] Display MVP (timeline + map + status sync)

Related repos: o-my, o-my-sim, battlespace-manager, fuzzy-reconciler (reference patterns).

---

*Part of Open Arsenal — Open by Design • Agile by Default*