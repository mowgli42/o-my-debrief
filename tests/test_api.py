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


def test_query_post(client: TestClient) -> None:
    r = client.post(
        "/api/query",
        json={"mission": MISSION_ID, "event_types": ["sensorCollect", "bda"]},
    )
    assert r.status_code == 200
    assert all(e["event_type"] in {"sensorCollect", "bda"} for e in r.json())
