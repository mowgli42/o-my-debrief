"""Parquet read helpers and milestone extraction."""

from __future__ import annotations

import json
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from omy_debrief.models.events import DebriefEvent, Milestone, MissionManifest, PlatformState


def data_dir() -> Path:
    return Path(os.environ.get("DEBRIEF_DATA_DIR", "data/debrief"))


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


def clear_cache() -> None:
    _read_table.cache_clear()


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


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
    milestones: list[Milestone] = []
    for ev in events:
        kind = None
        title = None
        outcome = ev.summary
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
            kind = "bda_positive" if "neutral" in (ev.summary or "").lower() or (
                ev.payload or {}
            ).get("assessment") in {"neutralized", "destroyed", "killed"} else "bda"
            title = f"BDA: {ev.target_id or 'target'} verified"
            marker = "flag"
        elif ev.event_type == "systemStatus":
            payload = ev.payload or {}
            if payload.get("datalink_up") is False:
                kind = "datalink_lost"
                title = "Datalink lost"
                outcome = "Link down at scrub time"
                marker = "none"

        if kind:
            milestones.append(
                Milestone(
                    milestone_id=f"ms-{ev.event_id}",
                    mission_id=mission_id,
                    timestamp=ev.timestamp,
                    kind=kind,
                    title=title or ev.summary,
                    outcome=outcome,
                    status=status,
                    marker=marker,  # type: ignore[arg-type]
                    event_id=ev.event_id,
                    lat=ev.lat,
                    lon=ev.lon,
                    target_id=ev.target_id,
                )
            )
    return milestones


def state_at(mission_id: str, time_iso: str) -> PlatformState:
    target = _parse_ts(time_iso)
    rows = sorted(_read_table(mission_id), key=lambda r: r["timestamp"])
    last_status: dict[str, Any] | None = None
    expended: list[dict[str, Any]] = []
    nearby: list[DebriefEvent] = []

    for row in rows:
        ts = _parse_ts(row["timestamp"])
        if ts > target:
            break
        if row["event_type"] == "systemStatus":
            last_status = row
        if row["event_type"] == "task" and (row.get("status") or "").upper() == "EXECUTED":
            payload = row.get("payload") or {}
            for mun in payload.get("munitions_released") or []:
                expended.append({"munition": mun, "timestamp": row["timestamp"], "target_id": row.get("target_id")})

    window_events = [
        row_to_event(r)
        for r in rows
        if abs((_parse_ts(r["timestamp"]) - target).total_seconds()) <= 180
    ]
    nearby = window_events[:12]

    if not last_status:
        return PlatformState(timestamp=time_iso, mission_id=mission_id, nearby_events=nearby)

    p = last_status.get("payload") or {}
    return PlatformState(
        timestamp=time_iso,
        mission_id=mission_id,
        callsign=p.get("callsign") or "HAWK-1",
        lat=last_status.get("lat"),
        lon=last_status.get("lon"),
        alt_ft=p.get("alt_ft"),
        heading_deg=p.get("heading_deg"),
        speed_kts=p.get("speed_kts"),
        fuel_percent=float(p.get("fuel_percent", 100)),
        datalink_up=bool(p.get("datalink_up", True)),
        datalink_mbps=p.get("datalink_mbps"),
        datalink_last_contact=last_status["timestamp"] if p.get("datalink_up") else last_status["timestamp"],
        payload_active=list(p.get("payload_active") or []),
        payload_mode=p.get("payload_mode"),
        weapons=dict(p.get("weapons") or {}),
        weapons_expended=expended,
        gear=p.get("gear") or "up",
        weapons_bay=p.get("weapons_bay") or "closed",
        readiness=last_status.get("status") or "GREEN",
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
