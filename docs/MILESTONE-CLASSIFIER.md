# Milestone Classifier Rules (YAML) + BDA Linkage

**Bead**: omd-h3a.8

## Goal
Externalize the hardcoded if-elif logic in `src/omy_debrief/store.py:extract_milestones` into a declarative YAML (or JSON) config. This makes it easy to add new mission types, adjust rules per customer, and support richer logic like BDA-to-strike/target linkage without code changes.

## Proposed YAML Schema

```yaml
version: 1
rules:
  - kind: sensor_collect
    when:
      event_type: sensorCollect
      status: success
    title: "{sensor} collect on {target_id or 'target'}"
    marker: diamond
    outcome_from: summary

  - kind: dissemination
    when:
      event_type: dissemination
      status: [delivered, success, ok]
    title: "Data disseminated ({target_id or 'product'})"
    marker: circle

  - kind: strike_assigned
    when:
      event_type: task
      status: ASSIGNED
    title: "Strike assigned — {target_id}"
    marker: caret
    status: pending

  - kind: strike_executed
    when:
      event_type: task
      status: EXECUTED
    title: "Strike EXECUTED — {target_id}"
    marker: caret

  - kind: bda
    when:
      event_type: bda
    title: "BDA: {target_id} verified"
    marker: flag
    # Positive if assessment or summary indicates success
    positive_if:
      payload.assessment: [neutralized, destroyed, killed]
      summary_contains: neutralized|destroyed|verified positive

  - kind: datalink_lost
    when:
      event_type: systemStatus
      payload.datalink_up: false
    title: "Datalink lost"
    marker: none
    status: warning

# Optional global linkage rules for chaining (post-processing)
linkage:
  bda_to_strike:
    within_minutes: 15
    match_on: target_id
    add_to_milestone:
      linked_strike: true
      note: "BDA for strike on same target"
```

## Implementation Sketch (store.py)

```python
import yaml
from pathlib import Path

RULES_PATH = Path(os.environ.get("DEBRIEF_RULES", "config/milestone-rules.yaml"))

@lru_cache

def load_rules():
    if RULES_PATH.exists():
        return yaml.safe_load(RULES_PATH.read_text())
    return {"rules": [], "linkage": {}}

def extract_milestones(...):
    events = list_events(...)
    rules = load_rules()
    milestones = []
    for ev in events:
        for rule in rules.get("rules", []):
            if matches_when(ev, rule["when"]):
                m = build_milestone(ev, rule)
                milestones.append(m)
                break  # first match wins
    # Post-process linkage
    if rules.get("linkage", {}).get("bda_to_strike"):
        link_bda_to_strikes(milestones, events, rules["linkage"]["bda_to_strike"])
    return milestones

def matches_when(ev, when):
    # recursive dict match, supports lists (any), nested payload.XXX, contains, etc.
    ...
```

## Richer BDA Linkage

After basic extraction, run a second pass:
- For each BDA milestone, find the most recent `strike_executed` milestone (or raw task EXECUTED event) with same `target_id` within `within_minutes`.
- If found, set `m.linked_strike_event_id = strike.event_id` and append a note or child entry.
- In frontend Milestones.svelte or a detail panel, show "↳ Linked to strike STRK-01 (executed 6 min earlier)" or highlight the chain.
- This fulfills the 'richer BDA linkage' without changing the /milestones response shape much (add optional fields to Milestone model).

## Next
- Add `pyyaml` to pyproject.toml (or use orjson + custom for zero-dep).
- Make rules hot-reloadable or overridable per mission in manifest.
- Expose /api/milestone-rules (debug) or validate in tests.
- Update Gherkin scenarios for new rule-driven behavior.

This directly addresses the design-heavy part of omd-h3a.8 while keeping the current working classifier as fallback.
