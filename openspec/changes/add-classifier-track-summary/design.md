# Design

## Decisions

1. **YAML first, fallback always** — If rules file missing or no match, use prior hardcoded classifier so demos never break.
2. **Linkage post-pass** — After extraction, match BDA to most recent EXECUTED task with same `target_id` within `within_minutes`.
3. **Interpolation** — Linear lat/lon/heading between adjacent `systemStatus` samples; no spline for MVP.
4. **Summary** — Deterministic narrative from milestones; `llm_hook` string documents future adapter without requiring an LLM now.
5. **XML** — stdlib ElementTree only; tolerate namespaced tags via local-name strip.

## Risks

- Template `{field or 'x'}` parser is intentionally minimal — complex expressions stay in Python fallback.
- Redis live proof remains manual (documented).
