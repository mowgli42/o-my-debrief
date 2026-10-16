"""Generate a demo strike-recon mission as Parquet + manifest."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from omy_debrief.demo.media_clips import write_media
from omy_debrief.models.events import DebriefEvent

MISSION_ID = "msn-demo-strike-recon"
CALLSIGN = "HAWK-1"

# Rough route over a fictional AO (Mediterranean-ish coords for basemap)
WAYPOINTS = [
    (36.80, 35.40, "WP1 Takeoff"),
    (36.85, 35.55, "WP2 Climb"),
    (36.92, 35.70, "WP3 Collect-1"),
    (36.98, 35.82, "WP4 Collect-2"),
    (37.05, 35.95, "WP5 Strike IP"),
    (37.10, 36.05, "WP6 Strike"),
    (37.00, 36.20, "WP7 Approach"),
    (36.85, 36.10, "WP8 Landing"),
]

SCHEMA = pa.schema(
    [
        ("event_id", pa.string()),
        ("mission_id", pa.string()),
        ("timestamp", pa.string()),
        ("event_type", pa.string()),
        ("source_topic", pa.string()),
        ("summary", pa.string()),
        ("target_id", pa.string()),
        ("lat", pa.float64()),
        ("lon", pa.float64()),
        ("sensor", pa.string()),
        ("status", pa.string()),
        ("payload_json", pa.string()),
        ("marker", pa.string()),
    ]
)


def _ts(base: datetime, minutes: float) -> str:
    return (base + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _event(
    *,
    eid: str,
    base: datetime,
    minutes: float,
    event_type: str,
    summary: str,
    topic: str,
    marker: str = "none",
    target_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    sensor: str | None = None,
    status: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "event_id": eid,
        "mission_id": MISSION_ID,
        "timestamp": _ts(base, minutes),
        "event_type": event_type,
        "source_topic": topic,
        "summary": summary,
        "target_id": target_id,
        "lat": lat,
        "lon": lon,
        "sensor": sensor,
        "status": status,
        "payload_json": json.dumps(payload or {}),
        "marker": marker,
    }


def build_demo_events(base: datetime | None = None) -> list[dict[str, Any]]:
    base = base or datetime(2026, 7, 21, 14, 0, 0, tzinfo=UTC)
    events: list[dict[str, Any]] = []
    n = 0

    def add(**kwargs: Any) -> None:
        nonlocal n
        n += 1
        kwargs.setdefault("eid", f"EVT-{n:04d}")
        events.append(_event(base=base, **kwargs))

    # Status samples along route: climb-out → cruise → descent, with gear at field
    weapons = {"GBU-39": 4, "AIM-120": 2}
    fuel = 94.0
    n_wp = len(WAYPOINTS)
    # Altitude / speed / pitch shaped for launch & recovery profile graph
    alt_profile = [200, 4500, 12000, 17500, 18000, 17800, 6500, 800]
    speed_profile = [145, 280, 380, 420, 430, 420, 260, 155]
    pitch_profile = [8.0, 6.0, 2.5, 0.5, 0.0, -0.5, -4.5, -5.5]
    for i, (lat, lon, label) in enumerate(WAYPOINTS):
        t = i * 4.0
        fuel = max(55.0, 94.0 - i * 4.5)
        bay = "open" if 4 <= i <= 5 else "closed"
        # Gear down on takeoff and final approach / landing
        gear = "down" if i == 0 or i >= n_wp - 2 else "up"
        if i == 5:
            weapons = {"GBU-39": 2, "AIM-120": 2}
        add(
            minutes=t,
            event_type="systemStatus",
            topic="uci.platform.status",
            summary=f"{CALLSIGN} status at {label}",
            lat=lat,
            lon=lon,
            status="GREEN",
            payload={
                "callsign": CALLSIGN,
                "fuel_percent": fuel,
                "datalink_up": i != 3,  # brief flicker at WP4
                "datalink_mbps": 0.0 if i == 3 else 4.2,
                "payload_active": ["EO", "IR"] if i < 6 else ["EO"],
                "payload_mode": "search" if i < 5 else "track",
                "weapons": dict(weapons),
                "gear": gear,
                "weapons_bay": bay,
                "alt_ft": alt_profile[i],
                "heading_deg": 55 + i * 8,
                "speed_kts": speed_profile[i],
                "roll_deg": round(6 * ((i % 3) - 1), 1),
                "pitch_deg": pitch_profile[i],
                "waypoint": label,
            },
        )
        add(
            minutes=t + 0.1,
            event_type="waypoint",
            topic="uci.platform.route",
            summary=f"Reached {label}",
            lat=lat,
            lon=lon,
            status="reached",
            payload={"waypoint": label, "index": i},
            marker="circle",
        )

    # Sensor collects (diamonds) — each links a timeline-synced sensor video clip
    # Last entry is intentionally unplanned (no peer in mission plan) for compare glow.
    collects = [
        (8.0, WAYPOINTS[2][0], WAYPOINTS[2][1], "EO", "TGT-042", "EO collected 3-image set on TGT-042", "clip-eo-042"),
        (10.5, 36.94, 35.74, "IR", "TGT-042", "IR collect on TGT-042 (thermal)", "clip-ir-042"),
        (12.0, WAYPOINTS[3][0], WAYPOINTS[3][1], "SAR", "TGT-055", "SAR strip collect on TGT-055", "clip-sar-055"),
        (14.5, 37.00, 35.88, "EO", "TGT-055", "EO revisit on TGT-055", "clip-eo-055"),
        (22.0, WAYPOINTS[6][0], WAYPOINTS[6][1], "EO", "TGT-042", "Post-strike EO BDA collect on TGT-042", "clip-bda-eo-042"),
        (24.0, 37.02, 36.18, "IR", "TGT-042", "IR BDA confirmation pass", "clip-bda-ir-042"),
        (17.2, 37.03, 35.98, "EO", "TGT-061", "Unplanned opportunistic EO collect on TGT-061", None),
    ]
    for minutes, lat, lon, sensor, tgt, summary, clip_id in collects:
        payload: dict[str, Any] = {
            "images": 3 if sensor == "EO" else 1,
            "size_gb": 2.1 if sensor == "EO" else 0.4,
            "mode": "spot",
        }
        if clip_id:
            payload["media_clip_id"] = clip_id
        if tgt == "TGT-061":
            payload["unplanned"] = True
        add(
            minutes=minutes,
            event_type="sensorCollect",
            topic="uci.signal.report",
            summary=summary,
            target_id=tgt,
            lat=lat,
            lon=lon,
            sensor=sensor,
            status="success",
            marker="diamond",
            payload=payload,
        )

    # Dissemination
    add(
        minutes=9.0,
        event_type="dissemination",
        topic="uci.commlink.status",
        summary="Disseminated EO product set for TGT-042 to ground (2.1GB)",
        target_id="TGT-042",
        status="delivered",
        marker="circle",
        payload={"product": "EO-SET-042", "mbps": 4.2, "size_gb": 2.1},
    )
    add(
        minutes=13.0,
        event_type="dissemination",
        topic="uci.commlink.status",
        summary="Disseminated SAR strip for TGT-055",
        target_id="TGT-055",
        status="delivered",
        marker="circle",
        payload={"product": "SAR-055", "mbps": 3.8, "size_gb": 0.9},
    )

    # Strike tasks (carets)
    add(
        minutes=16.0,
        event_type="task",
        topic="uci.task",
        summary="Strike task STRK-01 assigned on TGT-042",
        target_id="TGT-042",
        lat=WAYPOINTS[5][0],
        lon=WAYPOINTS[5][1],
        status="ASSIGNED",
        marker="caret",
        payload={"task_id": "STRK-01", "munitions": ["GBU-39", "GBU-39"], "effects": "destroy"},
    )
    add(
        minutes=19.5,
        event_type="task",
        topic="uci.task.status",
        summary="Strike task STRK-01 EXECUTED — 2× GBU-39 released",
        target_id="TGT-042",
        lat=WAYPOINTS[5][0],
        lon=WAYPOINTS[5][1],
        status="EXECUTED",
        marker="caret",
        payload={
            "task_id": "STRK-01",
            "munitions_released": ["GBU-39", "GBU-39"],
            "weapons_bay": "open",
            "effects_reported": True,
            "media_clip_id": "clip-strike-042",
        },
    )

    # BDA
    add(
        minutes=25.5,
        event_type="bda",
        topic="uci.engagement.result",
        summary="BDA report: TGT-042 neutralized — verified",
        target_id="TGT-042",
        lat=WAYPOINTS[6][0],
        lon=WAYPOINTS[6][1],
        status="VERIFIED",
        marker="flag",
        payload={
            "task_id": "STRK-01",
            "assessment": "neutralized",
            "confidence": 0.92,
            "linked_collects": ["EVT-sensor-bda-eo", "EVT-sensor-bda-ir"],
        },
    )

    return events


def build_demo_plan(base: datetime | None = None) -> dict[str, Any]:
    """Planned route + events with intentional time skew vs as-executed."""
    base = base or datetime(2026, 7, 21, 14, 0, 0, tzinfo=UTC)
    # Planned route: slight offset so map shows plan under / beside actual track
    route = [
        {
            "lat": lat + 0.012,
            "lon": lon - 0.008,
            "label": label,
            "index": i,
        }
        for i, (lat, lon, label) in enumerate(WAYPOINTS)
    ]
    planned: list[dict[str, Any]] = []

    def add_plan(
        *,
        pid: str,
        minutes: float,
        event_type: str,
        summary: str,
        marker: str = "none",
        target_id: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        sensor: str | None = None,
        status: str | None = "PLANNED",
    ) -> None:
        planned.append(
            {
                "plan_event_id": pid,
                "timestamp": _ts(base, minutes),
                "event_type": event_type,
                "summary": summary,
                "target_id": target_id,
                "lat": lat,
                "lon": lon,
                "sensor": sensor,
                "status": status,
                "marker": marker,
                "payload": {},
            }
        )

    # Collects planned ~45–75s earlier than as-executed peers (no TGT-061 — unplanned actual)
    add_plan(
        pid="PLAN-COL-EO-042",
        minutes=7.0,
        event_type="sensorCollect",
        summary="Planned EO collect on TGT-042",
        marker="diamond",
        target_id="TGT-042",
        lat=WAYPOINTS[2][0] + 0.012,
        lon=WAYPOINTS[2][1] - 0.008,
        sensor="EO",
    )
    add_plan(
        pid="PLAN-COL-IR-042",
        minutes=9.5,
        event_type="sensorCollect",
        summary="Planned IR collect on TGT-042",
        marker="diamond",
        target_id="TGT-042",
        lat=36.94 + 0.012,
        lon=35.74 - 0.008,
        sensor="IR",
    )
    add_plan(
        pid="PLAN-COL-SAR-055",
        minutes=11.0,
        event_type="sensorCollect",
        summary="Planned SAR collect on TGT-055",
        marker="diamond",
        target_id="TGT-055",
        lat=WAYPOINTS[3][0] + 0.012,
        lon=WAYPOINTS[3][1] - 0.008,
        sensor="SAR",
    )
    add_plan(
        pid="PLAN-COL-EO-055",
        minutes=13.5,
        event_type="sensorCollect",
        summary="Planned EO revisit on TGT-055",
        marker="diamond",
        target_id="TGT-055",
        lat=37.00 + 0.012,
        lon=35.88 - 0.008,
        sensor="EO",
    )
    # Strike planned ~75s before as-executed EXECUTED at 19.5 min
    add_plan(
        pid="PLAN-STRK-01",
        minutes=18.25,
        event_type="task",
        summary="Planned strike STRK-01 on TGT-042",
        marker="caret",
        target_id="TGT-042",
        lat=WAYPOINTS[5][0] + 0.012,
        lon=WAYPOINTS[5][1] - 0.008,
        status="PLANNED",
    )
    add_plan(
        pid="PLAN-BDA-EO-042",
        minutes=21.0,
        event_type="sensorCollect",
        summary="Planned post-strike EO BDA collect on TGT-042",
        marker="diamond",
        target_id="TGT-042",
        lat=WAYPOINTS[6][0] + 0.012,
        lon=WAYPOINTS[6][1] - 0.008,
        sensor="EO",
    )
    add_plan(
        pid="PLAN-BDA-IR-042",
        minutes=23.0,
        event_type="sensorCollect",
        summary="Planned IR BDA confirmation pass",
        marker="diamond",
        target_id="TGT-042",
        lat=37.02 + 0.012,
        lon=36.18 - 0.008,
        sensor="IR",
    )
    add_plan(
        pid="PLAN-DISS-042",
        minutes=8.25,
        event_type="dissemination",
        summary="Planned dissemination of EO product for TGT-042",
        marker="circle",
        target_id="TGT-042",
        status="PLANNED",
    )
    add_plan(
        pid="PLAN-DISS-055",
        minutes=12.25,
        event_type="dissemination",
        summary="Planned dissemination of SAR strip for TGT-055",
        marker="circle",
        target_id="TGT-055",
        status="PLANNED",
    )
    add_plan(
        pid="PLAN-BDA-042",
        minutes=24.5,
        event_type="bda",
        summary="Planned BDA verification on TGT-042",
        marker="flag",
        target_id="TGT-042",
        lat=WAYPOINTS[6][0] + 0.012,
        lon=WAYPOINTS[6][1] - 0.008,
        status="PLANNED",
    )

    return {"mission_id": MISSION_ID, "route": route, "events": planned}


def write_mission(out_dir: Path, events: list[dict[str, Any]] | None = None) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    events = events or build_demo_events()

    # Validate via model
    for row in events:
        DebriefEvent(
            event_id=row["event_id"],
            mission_id=row["mission_id"],
            timestamp=row["timestamp"],
            event_type=row["event_type"],  # type: ignore[arg-type]
            source_topic=row["source_topic"],
            summary=row["summary"],
            target_id=row.get("target_id"),
            lat=row.get("lat"),
            lon=row.get("lon"),
            sensor=row.get("sensor"),
            status=row.get("status"),
            payload=json.loads(row["payload_json"]),
            marker=row.get("marker") or "none",  # type: ignore[arg-type]
        )

    table = pa.Table.from_pylist(events, schema=SCHEMA)
    parquet_path = out_dir / f"{MISSION_ID}.parquet"
    pq.write_table(table, parquet_path)

    plan = build_demo_plan()
    plan_name = f"{MISSION_ID}.plan.json"
    plan_path = out_dir / plan_name
    plan_path.write_text(json.dumps(plan, indent=2) + "\n")

    times = sorted(e["timestamp"] for e in events)
    manifest = {
        "mission_id": MISSION_ID,
        "name": "Demo Strike-Recon (HAWK-1)",
        "description": (
            "Synthetic recon-strike mission: EO/IR/SAR collects, dissemination, "
            "strike execution, and BDA verification on TGT-042. Includes mission "
            "plan sidecar for plan-vs-actual compare."
        ),
        "start_time": times[0],
        "end_time": times[-1],
        "platform_callsign": CALLSIGN,
        "parquet_path": parquet_path.name,
        "plan_path": plan_name,
        "event_count": len(events),
        "waypoint_count": len(WAYPOINTS),
        "waypoints": [
            {"lat": lat, "lon": lon, "label": label, "index": i}
            for i, (lat, lon, label) in enumerate(WAYPOINTS)
        ],
    }
    manifest_path = out_dir / "manifest.json"
    existing: list[dict[str, Any]] = []
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text())
        if isinstance(existing, dict):
            existing = [existing]
        existing = [m for m in existing if m.get("mission_id") != MISSION_ID]
    existing.append(manifest)
    manifest_path.write_text(json.dumps(existing, indent=2) + "\n")

    # Also write a JSONL copy for recorder replay demos
    jsonl_path = out_dir / f"{MISSION_ID}.jsonl"
    with jsonl_path.open("w") as f:
        for row in events:
            f.write(json.dumps(row) + "\n")

    media_catalog = write_media(out_dir)
    print(f"Wrote media catalog {media_catalog}")
    print(f"Wrote plan {plan_path}")

    return parquet_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate demo debrief Parquet mission")
    parser.add_argument("--out", type=Path, default=Path("data/debrief"))
    args = parser.parse_args(argv)
    path = write_mission(args.out)
    print(f"Wrote {path} (+ manifest.json, jsonl, media clips)")


if __name__ == "__main__":
    main()
