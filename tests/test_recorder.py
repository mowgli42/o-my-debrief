"""Recorder normalization vs o-my-sim-shaped OMS XML/JSON."""

from __future__ import annotations

from omy_debrief.recorder.cli import normalize_message

PLATFORM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<uci:Message xmlns:uci="urn:uci:standard:1.0" xmlns:gw="urn:omy:gulfwar:1.0">
  <uci:Header>
    <uci:MessageID>PLT-ABC123</uci:MessageID>
    <uci:Timestamp>2026-07-21T14:05:00Z</uci:Timestamp>
    <uci:Sender>platform-status-sim</uci:Sender>
    <uci:MessageType>PlatformStatusReport</uci:MessageType>
  </uci:Header>
  <gw:PlatformStatusReport>
    <gw:PlatformID>PLT-1</gw:PlatformID>
    <gw:Callsign>HAWK-1</gw:Callsign>
    <gw:PlatformType>UCAV</gw:PlatformType>
    <gw:Position>
      <gw:Latitude>36.92</gw:Latitude>
      <gw:Longitude>35.70</gw:Longitude>
    </gw:Position>
    <gw:FuelPercent>88.5</gw:FuelPercent>
    <gw:WeaponsRemaining>4</gw:WeaponsRemaining>
    <gw:Readiness>GREEN</gw:Readiness>
  </gw:PlatformStatusReport>
</uci:Message>
"""


def test_normalize_platform_status_xml() -> None:
    row = normalize_message(PLATFORM_XML, topic="uci.platform.status")
    assert row["event_type"] == "systemStatus"
    assert row["event_id"] == "PLT-ABC123"
    assert row["timestamp"] == "2026-07-21T14:05:00Z"
    assert abs(row["lat"] - 36.92) < 1e-6
    assert abs(row["lon"] - 35.70) < 1e-6
    assert row["status"] == "GREEN"
    assert "HAWK-1" in row["summary"]


def test_normalize_demo_jsonl_passthrough() -> None:
    raw = {
        "event_id": "EVT-1",
        "mission_id": "msn",
        "timestamp": "2026-07-21T14:00:00Z",
        "event_type": "sensorCollect",
        "source_topic": "uci.signal.report",
        "summary": "EO collect",
        "marker": "diamond",
        "payload": {"images": 3},
    }
    row = normalize_message(raw, topic="uci.signal.report")
    assert row["event_type"] == "sensorCollect"
    assert row["marker"] == "diamond"
    assert "images" in row["payload_json"]


def test_normalize_task_json_topic() -> None:
    row = normalize_message(
        {"MessageID": "T-1", "status": "EXECUTED", "target_id": "TGT-042", "summary": "strike"},
        topic="uci.task.status",
    )
    assert row["event_type"] == "task"
    assert row["target_id"] == "TGT-042"
