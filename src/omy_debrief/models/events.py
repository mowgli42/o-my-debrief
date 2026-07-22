"""Shared Pydantic models for debrief events, milestones, and platform state."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


EventType = Literal[
    "systemStatus",
    "sensorCollect",
    "task",
    "dissemination",
    "bda",
    "waypoint",
    "other",
]

MarkerKind = Literal["diamond", "caret", "circle", "flag", "none"]


class DebriefEvent(BaseModel):
    event_id: str
    mission_id: str
    timestamp: str
    event_type: EventType
    source_topic: str = ""
    summary: str = ""
    target_id: str | None = None
    lat: float | None = None
    lon: float | None = None
    sensor: str | None = None
    status: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    marker: MarkerKind = "none"


class Milestone(BaseModel):
    milestone_id: str
    mission_id: str
    timestamp: str
    kind: str
    title: str
    outcome: str
    status: str = "completed"
    marker: MarkerKind = "diamond"
    event_id: str | None = None
    lat: float | None = None
    lon: float | None = None
    target_id: str | None = None
    linked_to_strike: bool = False
    linked_strike_event_id: str | None = None
    link_note: str | None = None


class TaskStatusEntry(BaseModel):
    task_id: str
    status: str
    timestamp: str
    target_id: str | None = None
    summary: str = ""
    lat: float | None = None
    lon: float | None = None


class PlatformState(BaseModel):
    timestamp: str
    mission_id: str
    callsign: str = "HAWK-1"
    lat: float | None = None
    lon: float | None = None
    alt_ft: float | None = None
    heading_deg: float | None = None
    speed_kts: float | None = None
    fuel_percent: float = 100.0
    datalink_up: bool = True
    datalink_mbps: float | None = 4.2
    datalink_last_contact: str | None = None
    payload_active: list[str] = Field(default_factory=list)
    payload_mode: str | None = None
    weapons: dict[str, int] = Field(default_factory=dict)
    weapons_expended: list[dict[str, Any]] = Field(default_factory=list)
    gear: Literal["up", "down"] = "up"
    weapons_bay: Literal["open", "closed"] = "closed"
    readiness: str = "GREEN"
    current_waypoint: str | None = None
    current_waypoint_index: int | None = None
    tasks: list[TaskStatusEntry] = Field(default_factory=list)
    nearby_events: list[DebriefEvent] = Field(default_factory=list)


class MissionManifest(BaseModel):
    mission_id: str
    name: str
    description: str = ""
    start_time: str
    end_time: str
    platform_callsign: str = "HAWK-1"
    parquet_path: str
    event_count: int = 0
    waypoint_count: int = 0
