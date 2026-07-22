# Change: YAML classifier, track replay, AAR summary, recorder XML

## Why

Grok landed design for `omd-h3a.8` (YAML milestone rules + BDA linkage) but the
implement commit replaced `store.py` with a placeholder. Remaining Grok beads
(`omd-h3a.9`–`.11`) need concrete API/UI hooks.

## What changes

- Restore Parquet store; load `config/milestone-rules.yaml` with hardcoded fallback
- BDA→strike linkage fields on Milestone (`linked_to_strike`, `linked_strike_event_id`, `link_note`)
- `/api/track`, `/api/position_at` (linear interpolation), smoother UI play
- `/api/summary` rule-based AAR narrative (+ LLM hook note)
- Recorder XML normalization for o-my-sim `PlatformStatusReport`
- Docs: integration notes; GitHub issues mirrored from beads

## Non-goals

- Live Redis e2e against a running o-my-sim stack in CI
- Real local LLM inference (hook only)
- Map clustering / LOD for dense tracks
