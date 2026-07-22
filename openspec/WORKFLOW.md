# Agent Workflow: OpenSpec + Gherkin + Beads

Follow this order unless the user explicitly requests otherwise.

## 1. Specification (OpenSpec)

- Living capability specs live under `openspec/specs/<capability>/spec.md`.
- Behavior changes use `openspec/changes/<change-id>/` with:
  - `proposal.md` — why + what (include Non-goals)
  - `design.md` — how (decisions, risks)
  - `specs/<capability>/spec.md` — ADDED/MODIFIED requirements with SHALL + GIVEN/WHEN/THEN
  - `tasks.md` — phased checkboxes
  - `verification.md` — scenario → evidence matrix
- Mirror scenarios as `features/*.feature`.
- Validate when CLI available: `npx @fission-ai/openspec validate <change-id> --strict`.

## 2. Task tracking (Beads)

- Create epic + phase children; link with `--spec-id openspec/specs/<capability>/spec.md`.
- Order: demo/contracts → recorder & API → display → docs/tests.
- Work with `bd ready`; claim with `bd update <id> --claim`; `bd close <id>` when done.

## 3. Implementation

- One Beads issue at a time when practical.
- MVP path (from spec): demo Parquet → `/events` + `/state_at` → Svelte shell → milestones → polish.

## 4. Validation

- Unit tests: `make test`
- Manual: Swagger `/docs` + UI scrub on demo mission
- Screenshots: `make capture` (API + Vite running)

## 5. Archiving

- Merge change deltas into `openspec/specs/<capability>/spec.md` after validate.
