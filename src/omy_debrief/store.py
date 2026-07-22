"""Parquet read helpers, YAML milestone classifier, and state/track queries."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
import yaml

from omy_debrief.models.events import (
    DebriefEvent,
    Milestone,
    MissionManifest,
    PlatformState,
    TaskStatusEntry,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RULES = REPO_ROOT / "config" / "milestone-rules.yaml"


def data_dir() -> Path:
    return Path(os.environ.get("DEBRIEF_DATA_DIR", "data/debrief"))


def rules_path() -> Path:
    return Path(os.environ.get("DEBRIEF_RULES", str(DEFAULT_RULES)))


def load_manifest() -> list[MissionManifest]:
    path = data_dir() / "manifest.json"
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    if isinstance(raw, dict):
        raw = [raw]
    return [MissionManifest(**m) for m in raw]


@lru_cache(maxsize=8)
def _read_table(mission_id: str) -> list[dict[str, Any]]:
    manifests = {m.mission_id: m for m in load_manifest()}
    if mission_id not in manifests:
        raise KeyError(f"Unknown mission: {mission_id}")
    parquet = data_dir() / manifests[mission_id].parquet_path
    table = pq.read_table(parquet)
    rows = table.to_pylist()
    for row in rows:
        if isinstance(row.get("payload_json"), str):
            row["payload"] = json.loads(row["payload_json"] or "{}")
        else:
            row["payload"] = row.get("payload") or {}
    return rows


@lru_cache(maxsize=4)
def load_rules() -> dict[str, Any]:
    path = rules_path()
    if path.exists():
        return yaml.safe_load(path.read_text()) or {"rules": [], "linkage": {}}
    return {"rules": [], "linkage": {}}


def clear_cache() -> None:
    _read_table.cache_clear()
    load_rules.cache_clear()


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _get_path(obj: Any, dotted: str) -> Any:
    cur = obj
    for part in dotted.split("."):
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            cur = getattr(cur, part, None)
    return cur


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return [value]


def _match_when(ev: DebriefEvent, when: dict[str, Any]) -> bool:
    for key, expected in when.items():
        actual = _get_path(ev, key) if "." in key else getattr(ev, key, None)
        if key.startswith("payload."):
            actual = _get_path(ev.payload or {}, key.removeprefix("payload."))
        if isinstance(expected, bool):
            if bool(actual) is not expected:
                return False
            continue
        expected_list = _as_list(expected)
        # Case-insensitive string compare for statuses
        if isinstance(actual, str):
            actual_norm = actual.lower()
            if not any(str(x).lower() == actual_norm for x in expected_list):
                return False
        elif actual not in expected_list:
            return False
    return True


def _format_template(template: str, ev: DebriefEvent) -> str:
    """Minimal `{field}` / `{field or 'default'}` formatter."""

    def repl(match: re.Match[str]) -> str:
        expr = match.group(1).strip()
        default = None
        field = expr
        if " or " in expr:
            field, default_raw = expr.split(" or ", 1)
            field = field.strip()
            default = default_raw.strip().strip("'\"")
        value = getattr(ev, field, None)
        if value in (None, ""):
            return default if default is not None else ""
        return str(value)

    return re.sub(r"\{([^}]+)\}", repl, template)


def _positive_bda(ev: DebriefEvent, rule: dict[str, Any]) -> bool:
    cfg = rule.get("positive_if") or {}
    assessment = (ev.payload or {}).get("assessment")
    allowed = cfg.get("payload.assessment") or []
    if assessment and assessment in _as_list(allowed):
        return True
    pattern = cfg.get("summary_contains")
    if pattern and re.search(pattern, ev.summary or "", re.IGNORECASE):
        return True
    return False


def _build_from_rule(ev: DebriefEvent, rule: dict[str, Any]) -> Milestone:
    kind = rule["kind"]
    if kind == "bda" and _positive_bda(ev, rule):
        kind = "bda_positive"
    title = _format_template(rule.get("title_template") or rule.get("title") or ev.summary, ev)
    outcome = ev.summary if rule.get("outcome_from", "summary") == "summary" else ev.summary
    status = rule.get("status") or ev.status or "completed"
    marker = rule.get("marker") or ev.marker or "diamond"
    return Milestone(
        milestone_id=f"ms-{ev.event_id}",
        mission_id=ev.mission_id,
        timestamp=ev.timestamp,
        kind=kind,
        title=title,
        outcome=outcome,
        status=status,
        marker=marker,  # type: ignore[arg-type]
        event_id=ev.event_id,
        lat=ev.lat,
        lon=ev.lon,
        target_id=ev.target_id,
    )


def _fallback_milestone(ev: DebriefEvent) -> Milestone | None:
    """Hardcoded classifier — used when YAML missing or no rule matches."""
    kind = None
    title = None
    marker = ev.marker
    status = ev.status or "completed"

    if ev.event_type == "sensorCollect" and ev.status == "success":
        kind = "sensor_collect"
        title = f"{ev.sensor or 'Sensor'} collect on {ev.target_id or 'target'}"
        marker = "diamond"
    elif ev.event_type == "dissemination" and (ev.status or "").lower() in {
        "delivered",
        "success",
        "ok",
    }:
        kind = "dissemination"
        title = f"Data disseminated ({ev.target_id or 'product'})"
        marker = "circle"
    elif ev.event_type == "task" and (ev.status or "").upper() == "EXECUTED":
        kind = "strike_executed"
        title = f"Strike EXECUTED — {ev.target_id or 'target'}"
        marker = "caret"
    elif ev.event_type == "task" and (ev.status or "").upper() == "ASSIGNED":
        kind = "strike_assigned"
        title = f"Strike assigned — {ev.target_id or 'target'}"
        marker = "caret"
        status = "pending"
    elif ev.event_type == "bda":
        positive = "neutral" in (ev.summary or "").lower() or (ev.payload or {}).get(
            "assessment"
        ) in {"neutralized", "destroyed", "killed"}
        kind = "bda_positive" if positive else "bda"
        title = f"BDA: {ev.target_id or 'target'} verified"
        marker = "flag"
    elif ev.event_type == "systemStatus" and (ev.payload or {}).get("datalink_up") is False:
        kind = "datalink_lost"
        title = "Datalink lost"
        marker = "none"

    if not kind:
        return None
    return Milestone(
        milestone_id=f"ms-{ev.event_id}",
        mission_id=ev.mission_id,
        timestamp=ev.timestamp,
        kind=kind,
        title=title or ev.summary,
        outcome=ev.summary,
        status=status,
        marker=marker,  # type: ignore[arg-type]
        event_id=ev.event_id,
        lat=ev.lat,
        lon=ev.lon,
        target_id=ev.target_id,
    )


def _link_bda_to_strikes(
    milestones: list[Milestone],
    events: list[DebriefEvent],
    cfg: dict[str, Any],
) -> None:
    within = timedelta(minutes=float(cfg.get("within_minutes", 15)))
    match_on = cfg.get("match_on", "target_id")
    strikes = [
        e
        for e in events
        if e.event_type == "task" and (e.status or "").upper() == "EXECUTED"
    ]
    for m in milestones:
        if m.kind not in {"bda", "bda_positive"}:
            continue
        m_ts = _parse_ts(m.timestamp)
        best: DebriefEvent | None = None
        best_delta: timedelta | None = None
        for s in strikes:
            if match_on == "target_id" and (s.target_id or "") != (m.target_id or ""):
                continue
            s_ts = _parse_ts(s.timestamp)
            if s_ts > m_ts:
                continue
            delta = m_ts - s_ts
            if delta > within:
                continue
            if best_delta is None or delta < best_delta:
                best = s
                best_delta = delta
        if best:
            m.linked_strike_event_id = best.event_id
            m.linked_to_strike = True
            mins = int((best_delta or timedelta()).total_seconds() // 60)
            note = f"Linked to strike {best.payload.get('task_id') or best.event_id} (executed {mins} min earlier)"
            m.link_note = note
            if m.outcome and note not in m.outcome:
                m.outcome = f"{m.outcome} · {note}"


def row_to_event(row: dict[str, Any]) -> DebriefEvent:
    return DebriefEvent(
        event_id=row["event_id"],
        mission_id=row["mission_id"],
        timestamp=row["timestamp"],
        event_type=row["event_type"],
        source_topic=row.get("source_topic") or "",
        summary=row.get("summary") or "",
        target_id=row.get("target_id"),
        lat=row.get("lat"),
        lon=row.get("lon"),
        sensor=row.get("sensor"),
        status=row.get("status"),
        payload=row.get("payload") or {},
        marker=row.get("marker") or "none",
    )


def list_events(
    mission_id: str,
    *,
    start: str | None = None,
    end: str | None = None,
    types: list[str] | None = None,
) -> list[DebriefEvent]:
    rows = _read_table(mission_id)
    start_dt = _parse_ts(start) if start else None
    end_dt = _parse_ts(end) if end else None
    type_set = set(types) if types else None
    out: list[DebriefEvent] = []
    for row in rows:
        ts = _parse_ts(row["timestamp"])
        if start_dt and ts < start_dt:
            continue
        if end_dt and ts > end_dt:
            continue
        if type_set and row["event_type"] not in type_set:
            continue
        out.append(row_to_event(row))
    out.sort(key=lambda e: e.timestamp)
    return out


def extract_milestones(mission_id: str) -> list[Milestone]:
    events = list_events(mission_id)
    rules_doc = load_rules()
    rules = rules_doc.get("rules") or []
    milestones: list[Milestone] = []

    for ev in events:
        matched: Milestone | None = None
        for rule in rules:
            when = rule.get("when") or {}
            if _match_when(ev, when):
                matched = _build_from_rule(ev, rule)
                break
        if matched is None:
            matched = _fallback_milestone(ev)
        if matched:
            milestones.append(matched)

    linkage = (rules_doc.get("linkage") or {}).get("bda_to_strike")
    if linkage:
        _link_bda_to_strikes(milestones, events, linkage)
    return milestones


def state_at(mission_id: str, time_iso: str) -> PlatformState:
    target = _parse_ts(time_iso)
    rows = sorted(_read_table(mission_id), key=lambda r: r["timestamp"])
    last_status: dict[str, Any] | None = None
    expended: list[dict[str, Any]] = []
    current_waypoint: str | None = None
    current_waypoint_index: int | None = None
    tasks_by_id: dict[str, TaskStatusEntry] = {}

    for row in rows:
        ts = _parse_ts(row["timestamp"])
        if ts > target:
            break
        if row["event_type"] == "systemStatus":
            last_status = row
            wp = (row.get("payload") or {}).get("waypoint")
            if wp:
                current_waypoint = str(wp)
        if row["event_type"] == "waypoint":
            payload = row.get("payload") or {}
            label = payload.get("waypoint") or row.get("summary")
            if label:
                current_waypoint = str(label)
            if payload.get("index") is not None:
                try:
                    current_waypoint_index = int(payload["index"])
                except (TypeError, ValueError):
                    pass
        if row["event_type"] == "task":
            payload = row.get("payload") or {}
            task_id = str(payload.get("task_id") or row.get("event_id"))
            tasks_by_id[task_id] = TaskStatusEntry(
                task_id=task_id,
                status=(row.get("status") or "UNKNOWN").upper(),
                timestamp=row["timestamp"],
                target_id=row.get("target_id"),
                summary=row.get("summary") or "",
                lat=row.get("lat"),
                lon=row.get("lon"),
            )
            if (row.get("status") or "").upper() == "EXECUTED":
                for mun in payload.get("munitions_released") or []:
                    expended.append(
                        {
                            "munition": mun,
                            "timestamp": row["timestamp"],
                            "target_id": row.get("target_id"),
                        }
                    )

    nearby = [
        row_to_event(r)
        for r in rows
        if abs((_parse_ts(r["timestamp"]) - target).total_seconds()) <= 180
    ][:12]

    tasks = sorted(tasks_by_id.values(), key=lambda t: t.timestamp)

    if not last_status:
        return PlatformState(
            timestamp=time_iso,
            mission_id=mission_id,
            current_waypoint=current_waypoint,
            current_waypoint_index=current_waypoint_index,
            tasks=tasks,
            nearby_events=nearby,
        )

    p = last_status.get("payload") or {}
    if not current_waypoint and p.get("waypoint"):
        current_waypoint = str(p.get("waypoint"))

    return PlatformState(
        timestamp=time_iso,
        mission_id=mission_id,
        callsign=p.get("callsign") or "HAWK-1",
        lat=last_status.get("lat"),
        lon=last_status.get("lon"),
        alt_ft=p.get("alt_ft"),
        heading_deg=p.get("heading_deg"),
        speed_kts=p.get("speed_kts"),
        roll_deg=p.get("roll_deg"),
        pitch_deg=p.get("pitch_deg"),
        fuel_percent=float(p.get("fuel_percent", 100)),
        datalink_up=bool(p.get("datalink_up", True)),
        datalink_mbps=p.get("datalink_mbps"),
        datalink_last_contact=last_status["timestamp"],
        payload_active=list(p.get("payload_active") or []),
        payload_mode=p.get("payload_mode"),
        weapons=dict(p.get("weapons") or {}),
        weapons_expended=expended,
        gear=p.get("gear") or "up",
        weapons_bay=p.get("weapons_bay") or "closed",
        readiness=last_status.get("status") or "GREEN",
        current_waypoint=current_waypoint,
        current_waypoint_index=current_waypoint_index,
        tasks=tasks,
        nearby_events=nearby,
    )


def mission_waypoints(mission_id: str) -> list[dict[str, Any]]:
    path = data_dir() / "manifest.json"
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    if isinstance(raw, dict):
        raw = [raw]
    for m in raw:
        if m.get("mission_id") == mission_id:
            return list(m.get("waypoints") or [])
    return []


def track_samples(mission_id: str) -> list[dict[str, Any]]:
    """Raw position samples from systemStatus (for map track)."""
    samples: list[dict[str, Any]] = []
    for ev in list_events(mission_id, types=["systemStatus"]):
        if ev.lat is None or ev.lon is None:
            continue
        p = ev.payload or {}
        samples.append(
            {
                "timestamp": ev.timestamp,
                "lat": ev.lat,
                "lon": ev.lon,
                "alt_ft": p.get("alt_ft"),
                "heading_deg": p.get("heading_deg"),
                "speed_kts": p.get("speed_kts"),
                "roll_deg": p.get("roll_deg"),
                "pitch_deg": p.get("pitch_deg"),
                "fuel_percent": p.get("fuel_percent"),
            }
        )
    return samples


def interpolate_track(mission_id: str, time_iso: str) -> dict[str, Any] | None:
    """Linear interpolate lat/lon/heading between surrounding systemStatus samples."""
    samples = track_samples(mission_id)
    if not samples:
        return None
    target = _parse_ts(time_iso)
    times = [_parse_ts(s["timestamp"]) for s in samples]
    if target <= times[0]:
        return {**samples[0], "interpolated": False}
    if target >= times[-1]:
        return {**samples[-1], "interpolated": False}
    for i in range(len(samples) - 1):
        t0, t1 = times[i], times[i + 1]
        if t0 <= target <= t1:
            span = (t1 - t0).total_seconds() or 1.0
            frac = (target - t0).total_seconds() / span
            a, b = samples[i], samples[i + 1]

            def lerp(x: Any, y: Any) -> float | None:
                if x is None or y is None:
                    return x if x is not None else y
                return float(x) + (float(y) - float(x)) * frac

            return {
                "timestamp": time_iso,
                "lat": lerp(a["lat"], b["lat"]),
                "lon": lerp(a["lon"], b["lon"]),
                "alt_ft": lerp(a.get("alt_ft"), b.get("alt_ft")),
                "heading_deg": lerp(a.get("heading_deg"), b.get("heading_deg")),
                "speed_kts": lerp(a.get("speed_kts"), b.get("speed_kts")),
                "roll_deg": lerp(a.get("roll_deg"), b.get("roll_deg")),
                "pitch_deg": lerp(a.get("pitch_deg"), b.get("pitch_deg")),
                "fuel_percent": lerp(a.get("fuel_percent"), b.get("fuel_percent")),
                "interpolated": True,
            }
    return None


def mission_summary(mission_id: str) -> dict[str, Any]:
    """Rule-based after-action narrative from milestones (LLM hook optional later)."""
    manifests = {m.mission_id: m for m in load_manifest()}
    if mission_id not in manifests:
        raise KeyError(f"Unknown mission: {mission_id}")
    m = manifests[mission_id]
    milestones = extract_milestones(mission_id)
    collects = [x for x in milestones if x.kind == "sensor_collect"]
    strikes = [x for x in milestones if x.kind == "strike_executed"]
    bdas = [x for x in milestones if x.kind in {"bda", "bda_positive"}]
    dissem = [x for x in milestones if x.kind == "dissemination"]
    linked = [x for x in bdas if x.linked_to_strike]

    lines = [
        f"Mission {m.name} ({mission_id}) · platform {m.platform_callsign}",
        f"Window {m.start_time} → {m.end_time} · {m.event_count} events recorded.",
        f"Collections: {len(collects)} sensor success(es); dissemination events: {len(dissem)}.",
        f"Strikes executed: {len(strikes)}; BDA reports: {len(bdas)} ({len(linked)} linked to prior strike).",
    ]
    for s in strikes:
        lines.append(f"  ▶ {s.timestamp} {s.title} — {s.outcome}")
    for b in bdas:
        link = f" [{b.link_note}]" if b.link_note else ""
        lines.append(f"  ⚑ {b.timestamp} {b.title}{link}")

    narrative = "\n".join(lines)
    return {
        "mission_id": mission_id,
        "name": m.name,
        "narrative": narrative,
        "stats": {
            "collects": len(collects),
            "disseminations": len(dissem),
            "strikes_executed": len(strikes),
            "bda_reports": len(bdas),
            "bda_linked": len(linked),
            "milestones": len(milestones),
        },
        "milestones": [ms.model_dump() for ms in milestones],
        "generator": "rule-based",
        "llm_hook": "Set DEBRIEF_LLM_SUMMARY=1 and provide adapter to replace narrative (future).",
    }
