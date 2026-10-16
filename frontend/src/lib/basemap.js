/**
 * o-my suite shared dark base map (reference implementation).
 *
 * Every o-my display (o-my-debrief, o-my-mission-plan, battlespace-manager)
 * draws its overlays on the same key-free dark raster tiles so the plan /
 * battlespace / debrief consoles look alike in demos.
 *
 * Suite convention (see docs/SHARED-DARK-MAP.md):
 *   - Tiles        Esri World Dark Gray Canvas: base + reference (labels)
 *   - maxZoom      12  (regional demo scale; no street-level detail)
 *   - opacity      0.65 base / 0.45 labels over a dark (#0b1220-ish) container
 *   - attribution  "© Esri, HERE, Garmin, © OpenStreetMap contributors"
 *   - no API key, no paid provider
 *
 * CartoDB Dark Matter was the original pick, but CARTO watermarks every
 * un-keyed tile ("API KEY REQUIRED") since September 2026.
 *
 * Usage (Leaflet):
 *   const map = L.map(el, { maxZoom: SUITE_DARK_TILES.maxZoom })
 *   L.tileLayer(SUITE_DARK_TILES.url, SUITE_DARK_TILES).addTo(map)
 *   L.tileLayer(SUITE_DARK_LABELS.url, SUITE_DARK_LABELS).addTo(map)
 *
 * Other repos copy these constants rather than importing them; keep the values
 * in sync when changing them. Intentionally dependency-free.
 */
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
