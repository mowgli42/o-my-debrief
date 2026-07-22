<script>
  import { onMount } from 'svelte'
  import L from 'leaflet'
  import { sensorColor } from './api.js'

  let {
    waypoints = [],
    events = [],
    platform = null,
    currentTime = null,
  } = $props()

  let mapEl = $state(null)
  let map = null
  let routeLayer = null
  let eventLayer = null
  let platformMarker = null

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
    L.polyline(latlngs, { color: '#3dd6c6', weight: 2, opacity: 0.85, dashArray: '6 4' }).addTo(
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
    map.fitBounds(L.latLngBounds(latlngs).pad(0.25))
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
    if (platform?.lat != null && platform?.lon != null) {
      platformMarker = L.marker([platform.lat, platform.lon], {
        icon: L.divIcon({
          className: '',
          html: `<div style="width:14px;height:14px;border-radius:50%;background:#3dd6c6;border:2px solid #e8eef8;box-shadow:0 0 10px rgba(61,214,198,.8)"></div>`,
          iconSize: [14, 14],
          iconAnchor: [7, 7],
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
