# Shared dark map base (o-my suite convention)

All o-my displays draw their overlays on the same key-free dark base map so
the plan, battlespace, and debrief consoles look and behave alike in demos.
This repo (`frontend/src/lib/MissionMap.svelte` + `frontend/src/lib/basemap.js`)
is the reference implementation; the sibling repos copy the same values.

## The convention

| Setting | Value |
| --- | --- |
| Library | Leaflet 1.9.x |
| Tiles | Esri World Dark Gray Canvas — base layer + reference (labels) layer |
| Base URL | `https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}` |
| Labels URL | `https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}` |
| `maxZoom` | **12** — regional demo scale, no street-level detail |
| Opacity | base `0.65`, labels `0.45`, over a dark container background (`#0b1220` / `#0e1626`) |
| Attribution | `© Esri, HERE, Garmin, © OpenStreetMap contributors` |
| API key | none; no paid provider (Mapbox, Google, Stadia, …) |

Note the Esri tile scheme is `{z}/{y}/{x}` (row before column), there is no
`{s}` subdomain and no `{r}` retina suffix.

Copy-paste form (dependency-free; keep it that way so non-Leaflet code such as
static tile snapshots can share it):

```js
export const SUITE_DARK_TILES = Object.freeze({
  url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
  attribution: '&copy; Esri, HERE, Garmin, &copy; OpenStreetMap contributors',
  maxZoom: 12,
  opacity: 0.65,
})
export const SUITE_DARK_LABELS = Object.freeze({
  url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
  maxZoom: SUITE_DARK_TILES.maxZoom,
  opacity: 0.45,
})

const map = L.map(el, { maxZoom: SUITE_DARK_TILES.maxZoom })
L.tileLayer(SUITE_DARK_TILES.url, SUITE_DARK_TILES).addTo(map)
L.tileLayer(SUITE_DARK_LABELS.url, SUITE_DARK_LABELS).addTo(map)
```

Set `maxZoom` on **both** the map and the tile layers: the layer cap keeps us
from requesting tiles at street scale, and the map cap keeps `fitBounds` /
scroll-zoom from zooming past the tiles. Give `.leaflet-container` a dark
background; the tile opacity blends Esri's mid-gray canvas into it.

Frozen (non-Leaflet) snapshots that paint tiles directly — for example
battlespace-manager's `staticTiles.js` — must expand the same base URL
template so a snapshot and the live map look identical.

## Why not CartoDB Dark Matter?

Dark Matter (`https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`)
was the original suite pick and is the look we are matching. Since September
2026 CARTO serves an "API KEY REQUIRED" watermark on every un-keyed tile
(keys registered before 23 Sep 2026 keep working until 30 Nov 2026; new keys
are free for non-commercial use but must be appended as `?key=…`). Keeping the
suite key-free matters more than the specific provider, so the standard moved
to Esri's dark gray canvas, which serves from any origin without a key. If the
suite ever adopts a keyed provider, change the reference constant here first,
inject the key from the environment (never commit it), and update the copies.

## Where it lives

| Repo | Map(s) |
| --- | --- |
| `o-my-debrief` (reference) | `frontend/src/lib/MissionMap.svelte`, constants in `frontend/src/lib/basemap.js` |
| `o-my-mission-plan` | Plan tab + route-details maps, constants at the top of `src/omy_mission_plan/static/app.js` |
| `battlespace-manager` | `services/battlespace-display`, `services/entity-display`, `services/rf-display` web UIs (`web/src/lib/basemap.js` each) and `staticTiles.js` |

## Changing it

If the suite moves to a different tile set or zoom cap, change the reference
constants here first, then open matching issues in the sibling repos. There is
intentionally no shared npm package yet; a documented pattern is enough at the
current scale.
