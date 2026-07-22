"""API smoke tests against demo parquet."""

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
    types = {e["event_type"] for e in events}
    assert "sensorCollect" in types
    assert "task" in types
    assert "bda" in types


def test_milestones(client: TestClient) -> None:
    r = client.get(f"/api/milestones?mission={MISSION_ID}")
    assert r.status_code == 200
    ms = r.json()
    kinds = {m["kind"] for m in ms}
    assert "sensor_collect" in kinds
    assert "strike_executed" in kinds
    assert "bda_positive" in kinds or "bda" in kinds


def test_state_at(client: TestClient) -> None:
    missions = client.get("/api/missions").json()
    m = next(x for x in missions if x["mission_id"] == MISSION_ID)
    # Mid-mission
    r = client.get(f"/api/state_at?mission={MISSION_ID}&time={m['start_time']}")
    assert r.status_code == 200
    state = r.json()
    assert "fuel_percent" in state
    assert state["fuel_percent"] <= 100
    assert "weapons" in state

    # Around strike
    mid = "2026-07-21T14:20:00Z"
    r2 = client.get(f"/api/state_at?mission={MISSION_ID}&time={mid}")
    assert r2.status_code == 200
    s2 = r2.json()
    assert s2["fuel_percent"] < 94


def test_query_post(client: TestClient) -> None:
    r = client.post(
        "/api/query",
        json={"mission": MISSION_ID, "event_types": ["sensorCollect", "bda"]},
    )
    assert r.status_code == 200
    assert all(e["event_type"] in {"sensorCollect", "bda"} for e in r.json())
