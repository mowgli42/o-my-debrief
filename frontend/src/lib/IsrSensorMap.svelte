<script>
  import { onMount } from 'svelte'
  import L from 'leaflet'
  import { sensorColor } from './api.js'
  import { SUITE_DARK_LABELS, SUITE_DARK_TILES } from './basemap.js'

  let {
    track = [],
    fovHistory = [],
    collections = [],
    detections = [],
    opportunities = [],
    faults = [],
    currentTime = null,
    selectedEventId = null,
    perspective = 'engineering',
    onselect = () => {},
  } = $props()

  let mapEl = $state(null)
  let map = null
  let layers = null
  let fitted = false

  function metersToLatLngRadius(lat, meters) {
    return meters / 111320
  }

  function activeFov() {
    if (!currentTime || !fovHistory?.length) return null
    const t = new Date(currentTime).getTime()
    let best = null
    let bestDt = Infinity
    for (const f of fovHistory) {
      const dt = Math.abs(new Date(f.timestamp).getTime() - t)
      if (dt < bestDt) {
        bestDt = dt
        best = f
      }
    }
    return bestDt < 180_000 ? best : null
  }

  function render() {
    if (!map || !layers) return
    layers.clearLayers()

    if (track?.length) {
      const latlngs = track.filter((p) => p.lat != null).map((p) => [p.lat, p.lon])
      if (latlngs.length) {
        L.polyline(latlngs, { color: '#3dd6c6', weight: 2.5, opacity: 0.75 }).addTo(layers)
      }
    }

    const histOpacity = perspective === 'operator' ? 0.12 : 0.08
    for (const f of fovHistory || []) {
      if (f.lat == null || !f.fov_radius_m) continue
      L.circle([f.lat, f.lon], {
        radius: f.fov_radius_m,
        color: sensorColor(f.sensor),
        weight: 1,
        opacity: histOpacity + 0.15,
        fillOpacity: histOpacity,
        interactive: true,
      })
        .bindTooltip(`FOV ${f.sensor} · ${f.timestamp}`, { sticky: true })
        .on('click', () => onselect(f.event_id, f.timestamp))
        .addTo(layers)
    }

    for (const o of opportunities || []) {
      if (o.lat == null) continue
      const r = o.fov_radius_m || 180
      L.circle([o.lat, o.lon], {
        radius: r,
        color: '#eab308',
        weight: 1.5,
        dashArray: '4 4',
        opacity: 0.85,
        fillOpacity: perspective === 'operator' ? 0.18 : 0.06,
      })
        .bindTooltip(`Unused opportunity · ${o.summary || ''}`, { sticky: true })
        .on('click', () => onselect(o.event_id, o.timestamp))
        .addTo(layers)
    }

    for (const c of collections || []) {
      if (c.lat == null) continue
      const r = c.fov_radius_m || (c.footprint_diameter_m || 400) / 2
      const selected = c.event_id === selectedEventId
      L.circle([c.lat, c.lon], {
        radius: r,
        color: sensorColor(c.sensor),
        weight: selected ? 3 : 2,
        opacity: 0.95,
        fillOpacity: selected ? 0.35 : 0.22,
      })
        .bindTooltip(
          `Collect ${c.sensor} ${c.target_id || ''} · Q=${c.quality_score ?? '—'}`,
          { sticky: true },
        )
        .on('click', () => onselect(c.event_id, c.timestamp))
        .addTo(layers)
      L.circleMarker([c.lat, c.lon], {
        radius: selected ? 7 : 5,
        color: '#0d1219',
        weight: 1,
        fillColor: sensorColor(c.sensor),
        fillOpacity: 1,
      })
        .on('click', () => onselect(c.event_id, c.timestamp))
        .addTo(layers)
    }

    for (const d of detections || []) {
      if (d.lat == null) continue
      const selected = d.event_id === selectedEventId
      L.circleMarker([d.lat, d.lon], {
        radius: selected ? 8 : 6,
        color: d.imaged ? '#5cd67e' : '#ff7a45',
        weight: 2,
        fillColor: d.imaged ? '#5cd67e' : '#ff7a45',
        fillOpacity: 0.85,
      })
        .bindTooltip(
          `Detection ${d.sensor} ${d.target_id || ''} · ${d.imaged ? 'imaged' : 'uncollected'}`,
          { sticky: true },
        )
        .on('click', () => onselect(d.event_id, d.timestamp))
        .addTo(layers)
    }

    if (perspective === 'engineering') {
      for (const f of faults || []) {
        if (f.lat == null) continue
        L.marker([f.lat, f.lon], {
          icon: L.divIcon({
            className: '',
            html: `<div style="color:${f.confirmed ? '#ff5c6c' : '#eab308'};font-size:14px;text-shadow:0 0 4px #000">⚠</div>`,
            iconSize: [16, 16],
            iconAnchor: [8, 8],
          }),
        })
          .bindTooltip(f.summary || 'Fault', { sticky: true })
          .on('click', () => onselect(f.event_id, f.timestamp))
          .addTo(layers)
      }
    }

    const fov = activeFov()
    if (fov?.lat != null) {
      if (fov.for_radius_m) {
        L.circle([fov.lat, fov.lon], {
          radius: fov.for_radius_m,
          color: '#8b9cb0',
          weight: 1,
          dashArray: '6 4',
          opacity: 0.5,
          fillOpacity: 0.03,
        }).addTo(layers)
      }
      if (fov.fov_radius_m) {
        L.circle([fov.lat, fov.lon], {
          radius: fov.fov_radius_m,
          color: '#3dd6c6',
          weight: 2.5,
          opacity: 0.95,
          fillOpacity: 0.2,
        }).addTo(layers)
      }
      const az = Number(fov.pointing?.act_az_deg ?? fov.pointing?.cmd_az_deg)
      if (!Number.isNaN(az) && fov.fov_radius_m) {
        const rad = ((az - 90) * Math.PI) / 180
        const dLat = metersToLatLngRadius(fov.lat, fov.fov_radius_m * 1.4) * Math.sin(rad)
        const dLon =
          (fov.fov_radius_m * 1.4) /
          (111320 * Math.cos((fov.lat * Math.PI) / 180)) *
          Math.cos(rad)
        L.polyline(
          [
            [fov.lat, fov.lon],
            [fov.lat + dLat, fov.lon + dLon],
          ],
          { color: '#3dd6c6', weight: 2, opacity: 0.9 },
        ).addTo(layers)
      }
      L.circleMarker([fov.lat, fov.lon], {
        radius: 6,
        color: '#fff',
        weight: 2,
        fillColor: '#3dd6c6',
        fillOpacity: 1,
      }).addTo(layers)
    }

    if (!fitted && track?.length) {
      const bounds = L.latLngBounds(track.filter((p) => p.lat != null).map((p) => [p.lat, p.lon]))
      if (bounds.isValid()) {
        map.fitBounds(bounds.pad(0.25))
        fitted = true
      }
    }
  }

  onMount(() => {
    map = L.map(mapEl, {
      zoomControl: true,
      maxZoom: SUITE_DARK_TILES.maxZoom,
    }).setView([36.95, 35.85], 10)
    L.tileLayer(SUITE_DARK_TILES.url, SUITE_DARK_TILES).addTo(map)
    L.tileLayer(SUITE_DARK_LABELS.url, SUITE_DARK_LABELS).addTo(map)
    layers = L.layerGroup().addTo(map)
    render()
    return () => {
      map?.remove()
      map = null
    }
  })

  $effect(() => {
    void track
    void fovHistory
    void collections
    void detections
    void opportunities
    void faults
    void currentTime
    void selectedEventId
    void perspective
    render()
  })
</script>

<div class="relative h-full min-h-[280px] w-full overflow-hidden rounded-sm border border-[var(--line)]">
  <div bind:this={mapEl} class="h-full w-full"></div>
  <div
    class="pointer-events-none absolute bottom-2 left-2 rounded-sm border border-[var(--line)] bg-[color-mix(in_srgb,var(--bg-panel)_92%,transparent)] px-2 py-1 text-[10px] text-[var(--muted)]"
  >
    <span class="text-[var(--accent)]">●</span> flight ·
    <span style="color:#4da3ff">○</span> FOV hist ·
    <span style="color:#5cd67e">●</span> imaged det ·
    <span style="color:#ff7a45">●</span> uncollected det ·
    <span style="color:#eab308">◌</span> unused opp
    {#if perspective === 'engineering'}
      · <span style="color:#ff5c6c">⚠</span> fault
    {/if}
  </div>
</div>