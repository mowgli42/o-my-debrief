# Sensor video playback (separate viewer)

Debrief import **identifies** events/milestones that have associated sensor video.
Playback itself runs in a **separate pop-out window** with almost no chrome — the main
debrief stays map / milestones / platform status only.

## Concept

| Surface | Role |
|---------|------|
| Main debrief | Detect `media_clip_id` / `has_video`; badge milestones & timeline dots; header chip when a clip covers the scrub time; **Open video viewer** |
| Pop-out (`/video.html`) | Minimal feed. **Overlays** toggle (reticle / REC / labels). Classification badge top-left (always on). Synced via `BroadcastChannel` |
| Catalog | `data/debrief/media/<mission>/catalog.json` + MP4s from `make fixtures` |
| API | `GET /api/media?mission=…` · `GET /api/media/file/{mission}/{file}.mp4` |

## Association

OMS events carry `payload.media_clip_id`. Milestone extraction copies that onto:

- `has_video: true`
- `media_clip_id: "clip-eo-042"`

Timeline markers with a clip show a small collect-colored dot under the glyph.

## Viewer chrome

- **Classification** — small green badge top-left on the picture (and in the title bar); always visible.
- **Overlays** switch — toggles reticle, sensor/target labels, REC, feed name, and clock. Preference saved in `localStorage`.
- Demo MP4s are plain sensor-colored plates (no baked-in text) so the toggle fully controls HUD.

```
BroadcastChannel('omy-debrief-video')
  main → { type: 'sync', missionId, currentTime, playing, clipId }
  pop-out → { type: 'hello' }  // requests immediate sync
```

Seek rule in the viewer:

```
video.currentTime = (missionNow − clip.start) / (clip.end − clip.start) × duration
```

## Code

- Generator: `src/omy_debrief/demo/media_clips.py`
- Milestone fields: `models/events.py` · `store._media_fields`
- Main: `App.svelte` header chip + `Milestones` VIDEO badge
- Viewer: `frontend/video.html` · `VideoApp.svelte` · `VideoViewer.svelte`
