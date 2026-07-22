<script>
  import { onMount } from 'svelte'
  import L from 'leaflet'
  import { sensorColor } from './api.js'

  let {
    waypoints = [],
    events = [],
    track = [],
    platform = null,
    position = null,
    currentTime = null,
  } = $props()

  let mapEl = $state(null)
  let map = null
  let routeLayer = null
  let trackLayer = null
  let eventLayer = null
  let platformMarker = null
  let fitted = false

  onMount(() => {
    map = L.map(mapEl, {
      zoomControl: true,
      attributionControl: true,
    }).setView([36.95, 35.85], 9)

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OSM &copy; CARTO',
      maxZoom: 18,
    }).addTo(map)

    routeLayer = L.layerGroup().addTo(map)
    trackLayer = L.layerGroup().addTo(map)
    eventLayer = L.layerGroup().addTo(map)

    return () => {
      map?.remove()
      map = null
    }
  })

  $effect(() => {
    if (!map || !routeLayer) return
    routeLayer.clearLayers()
    if (!waypoints.length) return
    const latlngs = waypoints.map((w) => [w.lat, w.lon])
    L.polyline(latlngs, { color: '#3dd6c6', weight: 2, opacity: 0.55, dashArray: '6 4' }).addTo(
      routeLayer,
    )
    waypoints.forEach((w, i) => {
      L.circleMarker([w.lat, w.lon], {
        radius: 5,
        color: '#8fa3c1',
        fillColor: '#1a2740',
        fillOpacity: 1,
        weight: 2,
      })
        .bindTooltip(`${i + 1}. ${w.label}`, { direction: 'top' })
        .addTo(routeLayer)
    })
    if (!fitted) {
      map.fitBounds(L.latLngBounds(latlngs).pad(0.25))
      fitted = true
    }
  })

  $effect(() => {
    if (!map || !trackLayer) return
    trackLayer.clearLayers()
    if (!track.length) return
    const t = currentTime ? new Date(currentTime).getTime() : Infinity
    const past = track.filter((s) => new Date(s.timestamp).getTime() <= t)
    const latlngs = past.map((s) => [s.lat, s.lon])
    if (latlngs.length >= 2) {
      L.polyline(latlngs, {
        color: '#f0c14a',
        weight: 3,
        opacity: 0.9,
      }).addTo(trackLayer)
    }
  })

  $effect(() => {
    if (!map || !eventLayer) return
    eventLayer.clearLayers()
    const t = currentTime ? new Date(currentTime).getTime() : Infinity
    for (const e of events) {
      if (e.lat == null || e.lon == null) continue
      if (!['sensorCollect', 'task', 'bda'].includes(e.event_type)) continue
      const past = new Date(e.timestamp).getTime() <= t
      const color =
        e.event_type === 'sensorCollect'
          ? sensorColor(e.sensor)
          : e.event_type === 'task'
            ? '#ff7a45'
            : '#5ddea0'
      L.circleMarker([e.lat, e.lon], {
        radius: e.event_type === 'task' ? 8 : 6,
        color,
        fillColor: color,
        fillOpacity: past ? 0.85 : 0.25,
        weight: past ? 2 : 1,
        opacity: past ? 1 : 0.4,
      })
        .bindTooltip(e.summary, { direction: 'top' })
        .addTo(eventLayer)
    }
  })

  $effect(() => {
    if (!map) return
    if (platformMarker) {
      map.removeLayer(platformMarker)
      platformMarker = null
    }
    const lat = position?.lat ?? platform?.lat
    const lon = position?.lon ?? platform?.lon
    const heading = position?.heading_deg ?? platform?.heading_deg
    if (lat != null && lon != null) {
      const rot = heading != null ? `transform:rotate(${heading}deg)` : ''
      platformMarker = L.marker([lat, lon], {
        icon: L.divIcon({
          className: '',
          html: `<div style="width:16px;height:16px;${rot}"><div style="width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;border-bottom:16px solid #3dd6c6;filter:drop-shadow(0 0 6px rgba(61,214,198,.9))"></div></div>`,
          iconSize: [16, 16],
          iconAnchor: [8, 8],
        }),
      }).addTo(map)
    }
  })
</script>

<div class="panel flex h-full min-h-0 flex-col rounded-sm overflow-hidden">
  <header class="border-b border-[var(--line)] px-3 py-2">
    <h2 class="text-sm font-semibold tracking-[0.12em] uppercase text-[var(--accent)]">
      Route & tasks
    </h2>
  </header>
  <div bind:this={mapEl} class="min-h-[280px] flex-1"></div>
</div>
