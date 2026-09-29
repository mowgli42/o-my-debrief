# o-my-debrief

Platform Debrief for the Open Arsenal o-my OMS ecosystem: captures OMS bus messages, persists to Parquet, FastAPI query API, Svelte debrief station (timeline, map, flight instruments, sensor video).
Stack: Python (FastAPI, pyarrow), Svelte 5, Vite, Tailwind, Leaflet; Beads for tracking.
Posture: ponytail (repo >30 days). Shared health pack in `.cursor/skills/` and `.cursor/rules/`.

## Commands

- Backend (API :8020): `make backend` (or `uvicorn omy_debrief.api.app:app --reload --port 8020`)
- Frontend (UI :8920): `cd frontend && npm install && npm run dev`
- Fixtures: `make fixtures`
- Tests: `make test`
- Capture screenshots: `make capture`
- Secrets scan: `bash scripts/scan-secrets.sh .`
- Beads: `bd ready` / `bd show <id>` / `bd update <id> --claim`

## Hard prohibitions

- Do not commit private keys, `*-key.pem`, `*.key`, `.env` secrets, or `BEGIN … PRIVATE KEY`. Generate locally; gitignore keys. Public certs OK.
- Do not invent Redis topics, API routes, or demo mission IDs not present in code/OpenSpec.
- Do not rewrite OpenSpec / Gherkin / Beads to match a hoped-for future. Update only when code already changed.
- Do not embed the full sensor video player in the main debrief UI; keep pop-out `/video.html`.

## Verify by change type

| Change | Check |
| --- | --- |
| UI / Svelte | `npm run dev` + scrub timeline / open video viewer |
| API / FastAPI | `make test` or `curl http://127.0.0.1:8020/api/health` |
| Spec | matching `features/o-my-debrief.feature` + openspec still true |
| Demo / screenshots | `make capture` |
| Secrets | `bash scripts/scan-secrets.sh .` passes |

## Source of truth

- Behavior: `openspec/specs/o-my-debrief/spec.md` + `features/o-my-debrief.feature`
- Remaining work: Beads (`bd`) / GitHub issues
- Demo evidence: `docs/screenshots/` + README quick start
- Health bar: `.cursor/rules/repo-health.mdc`

## House vocabulary

- Milestone markers: ◆ sensor collects, ▼ strike tasks, ⚑ BDA
- Tabs: Mission vs Launch/Recovery
- Pop-out video viewer (not embedded)
- House terms: debrief station, scrub, state_at, OMS bus

## Borrowed patterns

- Hard prohibitions + verify-by-change-type from ossrules.md portfolio patterns (Svelte/FastAPI shape)
- Secrets prohibition from repo-health-loop template
