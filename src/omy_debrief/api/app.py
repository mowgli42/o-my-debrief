"""FastAPI Parquet reader for debrief queries."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from omy_debrief import __version__
from omy_debrief import store
from omy_debrief.models.events import DebriefEvent, Milestone, MissionManifest, PlatformState

app = FastAPI(
    title="o-my Platform Debrief API",
    description=(
        "Query OMS mission Parquet captures: events, milestones, and platform state-at-time. "
        "Part of Open Arsenal o-my ecosystem."
    ),
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "version": __version__, "data_dir": str(store.data_dir())}


@app.get("/api/missions", response_model=list[MissionManifest])
def missions() -> list[MissionManifest]:
    return store.load_manifest()


@app.get("/api/missions/{mission_id}/waypoints")
def waypoints(mission_id: str) -> list[dict[str, Any]]:
    try:
        store._read_table(mission_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return store.mission_waypoints(mission_id)


@app.get("/api/events", response_model=list[DebriefEvent])
def events(
    mission: str = Query(..., description="Mission id"),
    start: str | None = None,
    end: str | None = None,
    types: str | None = Query(None, description="Comma-separated event types"),
) -> list[DebriefEvent]:
    type_list = [t.strip() for t in types.split(",") if t.strip()] if types else None
    try:
        return store.list_events(mission, start=start, end=end, types=type_list)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/milestones", response_model=list[Milestone])
def milestones(mission: str = Query(...)) -> list[Milestone]:
    try:
        return store.extract_milestones(mission)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/state_at", response_model=PlatformState)
def state_at(
    mission: str = Query(...),
    time: str = Query(..., description="ISO-8601 timestamp"),
) -> PlatformState:
    try:
        return store.state_at(mission, time)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/track")
def track(mission: str = Query(...)) -> list[dict[str, Any]]:
    try:
        return store.track_samples(mission)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/position_at")
def position_at(
    mission: str = Query(...),
    time: str = Query(..., description="ISO-8601 timestamp"),
) -> dict[str, Any]:
    try:
        pos = store.interpolate_track(mission, time)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    if pos is None:
        raise HTTPException(404, "No track samples for mission")
    return pos


@app.get("/api/summary")
def summary(mission: str = Query(...)) -> dict[str, Any]:
    try:
        return store.mission_summary(mission)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/milestone-rules")
def milestone_rules() -> dict[str, Any]:
    return store.load_rules()


@app.post("/api/query")
def query(body: dict[str, Any]) -> list[DebriefEvent]:
    mission = body.get("mission")
    if not mission:
        raise HTTPException(400, "mission required")
    types = body.get("event_types") or body.get("types")
    try:
        return store.list_events(
            mission,
            start=body.get("start"),
            end=body.get("end"),
            types=types,
        )
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
