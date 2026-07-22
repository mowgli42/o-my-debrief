# Task Beads — o-my Platform Debrief

See `.beads/` for the issue database (run `bd list` after beads setup).

## Shipped / Current Focus

MVP: Recorder (redis → parquet) → API (FastAPI time + milestone queries + Swagger) → Display (Svelte timeline with diamonds/carets, milestones list, map, vehicle status panel synced to scrubber).

Core flows: live/sim capture during o-my mission → post-mission or live debrief scrubbing → exportable after-action summary.

## Next

Break spec requirements into beads issues. Prioritize recorder + sample data generator, then API endpoints, then frontend components (timeline viz, map integration, status cards).

Reference patterns from fuzzy-reconciler for OpenSpec validation, Svelte/FastAPI structure, docker, and Makefile.
