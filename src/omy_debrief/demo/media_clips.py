"""Generate synthetic sensor-video clips for the demo debrief mission.

Clips are short H.264 MP4s (lavfi + drawtext) keyed to mission time windows so
the UI can scrub/play them in sync with the debrief timeline.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

MISSION_ID = "msn-demo-strike-recon"

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
    label: str,
    target: str,
    duration_s: float = 8.0,
) -> None:
    """Render a silent synthetic sensor feed MP4 via ffmpeg lavfi."""
    bg = SENSOR_COLORS.get(sensor, "0x101820")
    # Escape drawtext special chars
    safe_label = label.replace(":", "\\:").replace("'", "")
    safe_target = target.replace(":", "\\:")
    vf = (
        f"drawbox=x=iw/2-40:y=ih/2-40:w=80:h=80:color=white@0.35:t=2,"
        f"drawgrid=w=40:h=40:t=1:c=white@0.08,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:"
        f"text='{sensor}  {safe_target}':x=24:y=20:fontsize=22:fontcolor=white,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:"
        f"text='{safe_label}':x=24:y=52:fontsize=14:fontcolor=0x3dd6c6,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:"
        f"text='REC  %{{pts\\:hms}}':x=24:y=h-36:fontsize=14:fontcolor=0xff5c6c,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:"
        f"text='HAWK-1 DEMO FEED':x=w-220:y=h-36:fontsize=12:fontcolor=white@0.7"
    )
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
    # Fallback without custom font if fontfile missing
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        vf_simple = (
            f"drawbox=x=iw/2-40:y=ih/2-40:w=80:h=80:color=white@0.35:t=2,"
            f"drawtext=text='{sensor} {safe_target}':x=24:y=24:fontsize=22:fontcolor=white,"
            f"drawtext=text='DEMO SENSOR FEED':x=24:y=h-40:fontsize=14:fontcolor=0x3dd6c6"
        )
        cmd[cmd.index("-vf") + 1] = vf_simple
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
        # Still write catalog so API works; UI falls back to canvas HUD
        for clip in catalog:
            clip["filename"] = None
            clip["url"] = None
            clip["synthetic"] = True
        catalog_path = media_root / "catalog.json"
        catalog_path.write_text(json.dumps(catalog, indent=2) + "\n")
        return catalog_path

    for clip in catalog:
        path = media_root / f"{clip['clip_id']}.mp4"
        if not path.exists() or path.stat().st_size < 1000:
            _render_clip(
                path,
                sensor=clip["sensor"],
                label=clip["label"],
                target=clip["target_id"],
                duration_s=float(clip["duration_s"]),
            )
        clip["bytes"] = path.stat().st_size

    catalog_path = media_root / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n")
    return catalog_path
