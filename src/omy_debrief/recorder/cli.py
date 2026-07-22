"""OMS message recorder: Redis or JSONL → Parquet."""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from omy_debrief.demo.generate import SCHEMA, write_mission

DEFAULT_TOPICS = [
    "uci.platform.status",
    "uci.task",
    "uci.task.status",
    "uci.signal.report",
    "uci.engagement.result",
    "uci.commlink.status",
    "uci.platform.route",
    "uci.oms.state",
]


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_message(raw: dict[str, Any] | str, topic: str = "") -> dict[str, Any]:
    """Normalize a bus message or demo JSONL row into the Parquet schema dict."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = {"summary": raw, "payload": {"raw": raw}}

    assert isinstance(raw, dict)
    if "event_id" in raw and "event_type" in raw and "timestamp" in raw:
        # Already in debrief row shape
        row = dict(raw)
        if "payload_json" not in row:
            row["payload_json"] = json.dumps(row.get("payload") or {})
        row.setdefault("source_topic", topic or row.get("source_topic") or "")
        row.setdefault("marker", row.get("marker") or "none")
        return {f.name: row.get(f.name) for f in SCHEMA}

    # Heuristic from loose OMS/JSON
    payload = raw.get("payload") or raw
    event_type = raw.get("event_type") or raw.get("type") or "other"
    if "PlatformStatus" in str(raw.get("MessageType", "")) or topic.endswith("platform.status"):
        event_type = "systemStatus"
    elif "task" in topic:
        event_type = "task"
    elif "signal" in topic or "sensor" in str(raw).lower():
        event_type = "sensorCollect"

    return {
        "event_id": raw.get("event_id") or raw.get("MessageID") or f"REC-{int(time.time() * 1000)}",
        "mission_id": raw.get("mission_id") or "live-session",
        "timestamp": raw.get("timestamp") or raw.get("Timestamp") or _now(),
        "event_type": event_type,
        "source_topic": topic or raw.get("source_topic") or "",
        "summary": raw.get("summary") or raw.get("callsign") or str(event_type),
        "target_id": raw.get("target_id"),
        "lat": raw.get("lat") or raw.get("latitude"),
        "lon": raw.get("lon") or raw.get("longitude"),
        "sensor": raw.get("sensor"),
        "status": raw.get("status") or raw.get("readiness"),
        "payload_json": json.dumps(payload if isinstance(payload, dict) else {"value": payload}),
        "marker": raw.get("marker") or "none",
    }


def write_rows(out_dir: Path, mission_id: str, rows: list[dict[str, Any]]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    path = out_dir / f"{mission_id}.parquet"
    pq.write_table(table, path)

    times = sorted(r["timestamp"] for r in rows)
    manifest_path = out_dir / "manifest.json"
    entry = {
        "mission_id": mission_id,
        "name": mission_id,
        "description": f"Recorded session ({len(rows)} events)",
        "start_time": times[0] if times else _now(),
        "end_time": times[-1] if times else _now(),
        "platform_callsign": "UNKNOWN",
        "parquet_path": path.name,
        "event_count": len(rows),
        "waypoint_count": 0,
        "waypoints": [],
    }
    existing: list[dict[str, Any]] = []
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text())
        if isinstance(existing, dict):
            existing = [existing]
        existing = [m for m in existing if m.get("mission_id") != mission_id]
    existing.append(entry)
    manifest_path.write_text(json.dumps(existing, indent=2) + "\n")
    return path


def record_from_jsonl(jsonl_path: Path, out_dir: Path, mission_id: str) -> Path:
    rows = []
    with jsonl_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(normalize_message(json.loads(line)))
    return write_rows(out_dir, mission_id, rows)


def record_from_redis(
    redis_url: str,
    topics: list[str],
    out_dir: Path,
    mission_id: str,
    duration_sec: float = 30.0,
) -> Path:
    try:
        import redis
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("redis package required for live mode") from exc

    client = redis.Redis.from_url(redis_url, decode_responses=True)
    pubsub = client.pubsub()
    pubsub.subscribe(*topics)
    rows: list[dict[str, Any]] = []
    deadline = time.time() + duration_sec
    print(f"Recording from {redis_url} topics={topics} for {duration_sec}s …")
    while time.time() < deadline:
        msg = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        if not msg:
            continue
        topic = msg.get("channel") or ""
        data = msg.get("data")
        rows.append(normalize_message(data, topic=str(topic)))
        print(f"  + {topic} ({len(rows)})")
    pubsub.close()
    if not rows:
        print("No messages received; writing empty session skipped — generating demo instead")
        return write_mission(out_dir)
    return write_rows(out_dir, mission_id, rows)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="OMS → Parquet recorder")
    parser.add_argument("--mode", choices=["demo", "jsonl", "redis"], default="demo")
    parser.add_argument("--out", type=Path, default=Path("data/debrief"))
    parser.add_argument("--mission", default="live-session")
    parser.add_argument("--jsonl", type=Path, help="Input JSONL for --mode jsonl")
    parser.add_argument("--redis-url", default="redis://127.0.0.1:6379/0")
    parser.add_argument("--topics", default=",".join(DEFAULT_TOPICS))
    parser.add_argument("--duration", type=float, default=30.0)
    args = parser.parse_args(argv)

    if args.mode == "demo":
        path = write_mission(args.out)
    elif args.mode == "jsonl":
        if not args.jsonl:
            raise SystemExit("--jsonl required")
        path = record_from_jsonl(args.jsonl, args.out, args.mission)
    else:
        topics = [t.strip() for t in args.topics.split(",") if t.strip()]
        path = record_from_redis(args.redis_url, topics, args.out, args.mission, args.duration)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
