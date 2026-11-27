"""API + classifier + track + summary tests against demo parquet."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from omy_debrief.demo.generate import MISSION_ID, write_mission
from omy_debrief.store import clear_cache


@pytest.fixture(scope="module")
def data_root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("debrief")
    write_mission(root)
    os.environ["DEBRIEF_DATA_DIR"] = str(root)
    # Point at repo rules
    os.environ["DEBRIEF_RULES"] = str(
        Path(__file__).resolve().parents[1] / "config" / "milestone-rules.yaml"
    )
    clear_cache()
    return root


@pytest.fixture(scope="module")
def client(data_root: Path) -> TestClient:
    from omy_debrief.api.app import app

    return TestClient(app)


def test_health(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_missions(client: TestClient) -> None:
    r = client.get("/api/missions")
    assert r.status_code == 200
    missions = r.json()
    assert any(m["mission_id"] == MISSION_ID for m in missions)


def test_events_and_markers(client: TestClient) -> None:
    r = client.get(f"/api/events?mission={MISSION_ID}")
    assert r.status_code == 200
    events = r.json()
    assert len(events) > 10
    markers = {e["marker"] for e in events}
    assert "diamond" in markers
    assert "caret" in markers


def test_milestones_yaml_and_bda_link(client: TestClient) -> None:
    r = client.get(f"/api/milestones?mission={MISSION_ID}")
    assert r.status_code == 200
    ms = r.json()
    kinds = {m["kind"] for m in ms}
    assert "sensor_collect" in kinds
    assert "strike_executed" in kinds
    assert "bda_positive" in kinds or "bda" in kinds
    bdas = [m for m in ms if m["kind"] in {"bda", "bda_positive"}]
    assert bdas
    assert any(m.get("linked_to_strike") for m in bdas)
    assert any(m.get("linked_strike_event_id") for m in bdas)
    # Associated sensor video flagged on collects / strike FOV
    video_ms = [m for m in ms if m.get("has_video") and m.get("media_clip_id")]
    assert len(video_ms) >= 3


def test_state_at(client: TestClient) -> None:
    missions = client.get("/api/missions").json()
    m = next(x for x in missions if x["mission_id"] == MISSION_ID)
    r = client.get(f"/api/state_at?mission={MISSION_ID}&time={m['start_time']}")
    assert r.status_code == 200
    body0 = r.json()
    assert body0["fuel_percent"] <= 100
    assert "current_waypoint" in body0
    assert "tasks" in body0
    assert "roll_deg" in body0
    assert "pitch_deg" in body0

    mid = "2026-07-21T14:20:00Z"
    r2 = client.get(f"/api/state_at?mission={MISSION_ID}&time={mid}")
    assert r2.status_code == 200
    body = r2.json()
    assert body["fuel_percent"] < 94
    assert body["current_waypoint"]
    assert any(t["status"] == "EXECUTED" for t in body["tasks"])
    assert body["weapons_bay"] in {"open", "closed"}
    assert body["heading_deg"] is not None
    assert body["alt_ft"] is not None
    assert body["speed_kts"] is not None


def test_track_and_interpolate(client: TestClient) -> None:
    r = client.get(f"/api/track?mission={MISSION_ID}")
    assert r.status_code == 200
    samples = r.json()
    assert len(samples) >= 2
    mid = "2026-07-21T14:02:00Z"
    p = client.get(f"/api/position_at?mission={MISSION_ID}&time={mid}")
    assert p.status_code == 200
    body = p.json()
    assert body["lat"] is not None
    assert body["interpolated"] is True


def test_summary(client: TestClient) -> None:
    r = client.get(f"/api/summary?mission={MISSION_ID}")
    assert r.status_code == 200
    body = r.json()
    assert body["generator"] == "rule-based"
    assert "Strike" in body["narrative"] or "strike" in body["narrative"].lower()
    assert body["stats"]["strikes_executed"] >= 1


def test_milestone_rules(client: TestClient) -> None:
    r = client.get("/api/milestone-rules")
    assert r.status_code == 200
    assert "rules" in r.json()


def test_media_catalog_and_file(client: TestClient, data_root: Path) -> None:
    r = client.get(f"/api/media?mission={MISSION_ID}")
    assert r.status_code == 200
    clips = r.json()
    assert len(clips) >= 5
    assert all(c.get("clip_id") and c.get("start_time") for c in clips)
    # MP4 rendered when ffmpeg is available
    first = clips[0]
    if first.get("filename"):
        f = client.get(f"/api/media/file/{MISSION_ID}/{first['filename']}")
        assert f.status_code == 200
        assert f.headers["content-type"].startswith("video/")
        assert len(f.content) > 500
    catalog = data_root / "media" / MISSION_ID / "catalog.json"
    assert catalog.is_file()


def test_query_post(client: TestClient) -> None:
    r = client.post(
        "/api/query",
        json={"mission": MISSION_ID, "event_types": ["sensorCollect", "bda"]},
    )
    assert r.status_code == 200
    assert all(e["event_type"] in {"sensorCollect", "bda"} for e in r.json())


def test_plan_available(client: TestClient, data_root: Path) -> None:
    r = client.get(f"/api/plan?mission={MISSION_ID}")
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is True
    assert len(body["route"]) >= 2
    kinds = {e["event_type"] for e in body["events"]}
    assert "task" in kinds
    assert "sensorCollect" in kinds
    assert (data_root / f"{MISSION_ID}.plan.json").is_file()
    # Planned strike time differs from as-executed EXECUTED
    plan_strike = next(e for e in body["events"] if e["event_type"] == "task")
    actuals = client.get(f"/api/events?mission={MISSION_ID}&types=task").json()
    executed = next(e for e in actuals if (e.get("status") or "").upper() == "EXECUTED")
    assert plan_strike["timestamp"] != executed["timestamp"]


def test_analysis_sensor_collects(client: TestClient) -> None:
    r = client.get(f"/api/analysis/sensor-collects?mission={MISSION_ID}")
    assert r.status_code == 200
    body = r.json()
    assert len(body["points"]) >= 4
    assert body["points"][0].get("slant_range_nm") is not None
    assert 0 <= body["metrics"]["success_rate"] <= 1


def test_analysis_weapons_lar(client: TestClient) -> None:
    r = client.get(f"/api/analysis/weapons-lar?mission={MISSION_ID}")
    assert r.status_code == 200
    body = r.json()
    assert body["releases"]
    assert body["lar_summary"]["in_lar"] >= 1
    assert body["releases"][0]["within_lar"] is True


def test_analysis_sensor_telemetry(client: TestClient) -> None:
    r = client.get(f"/api/analysis/sensor-telemetry?mission={MISSION_ID}")
    assert r.status_code == 200
    samples = r.json()["samples"]
    assert len(samples) > 5
    assert any(s.get("health") for s in samples)


def test_report_pmr_html(client: TestClient) -> None:
    r = client.get(f"/api/report/pmr?mission={MISSION_ID}")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    html = r.text
    assert "Mission Overview" in html
    assert "Platform and Sensor Health" in html
    assert "page-3-fov-details" in html


def test_analysis_flight_review(client: TestClient) -> None:
    r = client.get(f"/api/analysis/flight-review?mission={MISSION_ID}")
    assert r.status_code == 200
    body = r.json()
    assert len(body["air_series"]) >= 2
    assert body["air_series"][0].get("alt_ft") is not None
    assert "fuel_percent" in body["air_series"][0]
    assert "duration_min" in body["metrics"]
    assert isinstance(body["events"], list)
    # Demo includes a datalink drop FOQA event
    assert any(e.get("rule_id") == "datalink_drop" for e in body["events"])
    # Phase 2: planned vs actual fields on air series
    sample = body["air_series"][0]
    assert sample.get("cmd_alt_ft") is not None
    assert sample.get("xte_nm") is not None
    assert body["planned_vs_actual"]["available"] is True
    assert body["planned_vs_actual"]["mean_xte_nm"] is not None
    # Phase 3: richer detectors + exceedance rollup
    assert any(e.get("rule_id") == "xte_exceed" for e in body["events"])
    assert "xte_exceed" in body["metrics"]["exceedance_stats"]
    # Phase 4: health timeline samples
    assert len(body["health_timeline"]) >= 2
    assert "datalink_up" in body["health_timeline"][0]


def test_analysis_fleet_trends(client: TestClient) -> None:
    r = client.get("/api/analysis/fleet-trends")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] >= 1
    assert any(m["mission_id"] == MISSION_ID for m in body["missions"])
    assert "mean_sensor_uptime_pct" in body["aggregates"]


def test_report_flight_performance(client: TestClient) -> None:
    r = client.get(f"/api/report/flight-performance?mission={MISSION_ID}")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    html = r.text
    assert "Aircraft Flight Performance Report" in html
    assert "Flight overview" in html
    assert "Aircraft performance" in html
    assert "Systems health" in html
    assert "Mission execution" in html
    assert "Post-flight assessment" in html


def test_analysis_sensor_isr(client: TestClient) -> None:
    r = client.get(f"/api/analysis/sensor-isr?mission={MISSION_ID}")
    assert r.status_code == 200
    body = r.json()
    assert body["fov_history"]
    assert body["collections"]
    assert body["detections"]
    assert body["opportunities"]
    assert "uptime_pct" in body["engineering"]
    assert "observe_pct" in body["operator"]
    assert any(e.get("isr_kind") == "fault" for e in body["faults"])


def test_summary_analysis_rollups(client: TestClient) -> None:
    r = client.get(f"/api/summary?mission={MISSION_ID}")
    body = r.json()
    assert "analysis" in body
    assert body["stats"].get("lar_total") is not None


def test_compare_fuzzy_and_unplanned(client: TestClient) -> None:
    r = client.get(f"/api/compare?mission={MISSION_ID}&tolerance_seconds=90")
    assert r.status_code == 200
    body = r.json()
    assert body["tolerance_seconds"] == 90
    strike_pairs = [p for p in body["pairs"] if p["kind"] == "strike"]
    assert strike_pairs
    assert all(p["delta_seconds"] <= 90 for p in strike_pairs)
    # Unplanned opportunistic collect on TGT-061 (not the detection cue)
    events = client.get(f"/api/events?mission={MISSION_ID}").json()
    unplanned = next(
        e
        for e in events
        if e.get("target_id") == "TGT-061" and e.get("event_type") == "sensorCollect"
    )
    assert unplanned["event_id"] in body["unmatched_actual"]
