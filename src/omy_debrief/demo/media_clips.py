"""Generate synthetic sensor-video clips for the demo debrief mission.

Clips are short H.264 MP4s (plain sensor-colored plates) keyed to mission time
windows. HUD text / reticle / REC live in the viewer as toggleable overlays.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

MISSION_ID = "msn-demo-strike-recon"
DEFAULT_CLASSIFICATION = "UNCLASSIFIED"

# (clip_id, sensor, label, mission_offset_min, duration_min, target)
CLIP_SPECS: list[tuple[str, str, str, float, float, str]] = [
    ("clip-eo-042", "EO", "EO collect — TGT-042", 7.5, 1.5, "TGT-042"),
    ("clip-ir-042", "IR", "IR collect — TGT-042", 10.0, 1.5, "TGT-042"),
    ("clip-sar-055", "SAR", "SAR strip — TGT-055", 11.5, 1.5, "TGT-055"),
    ("clip-eo-055", "EO", "EO revisit — TGT-055", 14.0, 1.5, "TGT-055"),
    ("clip-strike-042", "EO", "Strike FOV — STRK-01", 18.5, 2.0, "TGT-042"),
    ("clip-bda-eo-042", "EO", "Post-strike EO BDA — TGT-042", 21.5, 1.5, "TGT-042"),
    ("clip-bda-ir-042", "IR", "IR BDA confirm — TGT-042", 23.5, 1.5, "TGT-042"),
]

SENSOR_COLORS = {
    "EO": "0x0a1a2e",
    "IR": "0x2a0a0a",
    "SAR": "0x0a1a12",
}


def _ts(base: datetime, minutes: float) -> str:
    return (base + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _render_clip(
    out_path: Path,
    *,
    sensor: str,
    duration_s: float = 8.0,
) -> None:
    """Render a silent plate (no baked-in text — overlays are UI-only)."""
    bg = SENSOR_COLORS.get(sensor, "0x101820")
    # Subtle grid only — reticle/labels are HTML overlays
    vf = "drawgrid=w=40:h=40:t=1:c=white@0.06"
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={bg}:s=640x360:d={duration_s}:r=24",
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-an",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def build_media_catalog(base: datetime | None = None) -> list[dict[str, Any]]:
    base = base or datetime(2026, 7, 21, 14, 0, 0, tzinfo=UTC)
    catalog: list[dict[str, Any]] = []
    for clip_id, sensor, label, start_min, dur_min, target in CLIP_SPECS:
        catalog.append(
            {
                "clip_id": clip_id,
                "mission_id": MISSION_ID,
                "sensor": sensor,
                "label": label,
                "target_id": target,
                "classification": DEFAULT_CLASSIFICATION,
                "start_time": _ts(base, start_min),
                "end_time": _ts(base, start_min + dur_min),
                "filename": f"{clip_id}.mp4",
                "url": f"/api/media/file/{MISSION_ID}/{clip_id}.mp4",
                "duration_s": 8.0,
            }
        )
    return catalog


def write_media(out_dir: Path, base: datetime | None = None) -> Path:
    """Write catalog.json + MP4 clips under out_dir/media/<mission_id>/."""
    out_dir = Path(out_dir)
    media_root = out_dir / "media" / MISSION_ID
    media_root.mkdir(parents=True, exist_ok=True)
    catalog = build_media_catalog(base)

    if not _ffmpeg_available():
        for clip in catalog:
            clip["filename"] = None
            clip["url"] = None
            clip["synthetic"] = True
        catalog_path = media_root / "catalog.json"
        catalog_path.write_text(json.dumps(catalog, indent=2) + "\n")
        return catalog_path

    # Always regenerate so overlay bake-ins from older generators are cleared
    for clip in catalog:
        path = media_root / f"{clip['clip_id']}.mp4"
        _render_clip(
            path,
            sensor=clip["sensor"],
            duration_s=float(clip["duration_s"]),
        )
        clip["bytes"] = path.stat().st_size

    catalog_path = media_root / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n")
    return catalog_path
