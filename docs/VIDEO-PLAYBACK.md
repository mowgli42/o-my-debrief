# Sensor video playback (timeline-synced)

Debrief stations scrub mission time like a video player. This feature binds
**sensor / FOV clips** to mission time windows so Play and scrub drive both the
map and the sensor feed.

## Concept

| Piece | Role |
|-------|------|
| Demo catalog | `data/debrief/media/<mission>/catalog.json` — clip id, sensor, start/end ISO, MP4 filename |
| Demo MP4s | Synthetic lavfi clips (EO / IR / SAR / strike FOV) rendered by `ffmpeg` during `make fixtures` |
| API | `GET /api/media?mission=…` · `GET /api/media/file/{mission}/{file}.mp4` |
| UI | Center panel **Sensor video** tab — active clip follows scrub; clip list jumps timeline |

Collect and strike events carry `payload.media_clip_id` linking OMS messages to clips.

## Demo clips (HAWK-1)

| Clip | Sensor | Window (mission clock) |
|------|--------|------------------------|
| `clip-eo-042` | EO | Collect on TGT-042 |
| `clip-ir-042` | IR | Thermal collect |
| `clip-sar-055` | SAR | Strip on TGT-055 |
| `clip-eo-055` | EO | Revisit TGT-055 |
| `clip-strike-042` | EO | Strike FOV STRK-01 |
| `clip-bda-eo-042` / `clip-bda-ir-042` | EO / IR | Post-strike BDA |

## Sync rule

```
video.currentTime = (missionNow − clip.start) / (clip.end − clip.start) × video.duration
```

While **Play** is active the debrief clock advances and the `<video>` element seeks/plays in lockstep. Outside any clip window the panel shows “No sensor feed” and the clip list remains available.

## Code

- Generator: `src/omy_debrief/demo/media_clips.py` (called from `demo/generate.py`)
- Store: `store.list_media` / `store.media_file_path`
- UI: `frontend/src/lib/SensorVideo.svelte`
