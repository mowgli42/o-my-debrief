<script>
  import { onMount } from 'svelte'
  import L from 'leaflet'
  import { sensorColor } from './api.js'

  let {
    waypoints = [],
    events = [],
    track = [],
    plannedRoute = [],
    showPlannedRoute = $bindable(true),
    platform = null,
    position = null,
    currentTime = null,
    highlightEventId = null,
    unmatchedActual = [],
  } = $props()

  let mapEl = $state(null)
  let map = null
  let planRouteLayer = null
  let routeLayer = null
  let trackLayer = null
  let eventLayer = null
  let platformMarker = null
  let fitted = false

  let unmatchedSet = $derived(new Set(unmatchedActual || []))

  onMount(() => {
    map = L.map(mapEl, {
      zoomControl: true,
      attributionControl: true,
    }).setView([36.95, 35.85], 9)

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OSM &copy; CARTO',
      maxZoom: 18,
    }).addTo(map)

    // Plan under actual: insert plan pane below overlay
    map.createPane('plannedRoute')
    map.getPane('plannedRoute').style.zIndex = 350
    map.createPane('actualTrack')
    map.getPane('actualTrack').style.zIndex = 450

    planRouteLayer = L.layerGroup({ pane: 'plannedRoute' }).addTo(map)
    routeLayer = L.layerGroup().addTo(map)
    trackLayer = L.layerGroup({ pane: 'actualTrack' }).addTo(map)
    eventLayer = L.layerGroup().addTo(map)

    return () => {
      map?.remove()
      map = null
    }
  })

  $effect(() => {
    if (!map || !planRouteLayer) return
    planRouteLayer.clearLayers()
    if (!showPlannedRoute || !plannedRoute?.length) return
    const latlngs = plannedRoute.map((w) => [w.lat, w.lon])
    L.polyline(latlngs, {
      color: '#5a6f8c',
      weight: 3,
      opacity: 0.45,
      dashArray: '8 6',
      pane: 'plannedRoute',
    }).addTo(planRouteLayer)
  })

  $effect(() => {
    if (!map || !routeLayer) return
    routeLayer.clearLayers()
    if (!waypoints.length) return
    const latlngs = waypoints.map((w) => [w.lat, w.lon])
    L.polyline(latlngs, { color: '#3dd6c6', weight: 2, opacity: 0.35, dashArray: '6 4' }).addTo(
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
      const boundsPts = [
        ...latlngs,
        ...(showPlannedRoute && plannedRoute?.length
          ? plannedRoute.map((w) => [w.lat, w.lon])
          : []),
      ]
      map.fitBounds(L.latLngBounds(boundsPts).pad(0.25))
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
        pane: 'actualTrack',
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
      const highlighted = highlightEventId && e.event_id === highlightEventId
      const unplanned = unmatchedSet.has(e.event_id)
      const color =
        e.event_type === 'sensorCollect'
          ? sensorColor(e.sensor)
          : e.event_type === 'task'
            ? '#ff7a45'
            : '#5ddea0'
      const opacity = past || highlighted ? 1 : 0.4
      const glow = unplanned
        ? 'filter:drop-shadow(0 0 8px rgba(255,193,74,.95)) drop-shadow(0 0 14px rgba(255,122,69,.8));'
        : ''

      if (e.event_type === 'task' || e.marker === 'caret') {
        const size = highlighted || unplanned ? 22 : 18
        L.marker([e.lat, e.lon], {
          icon: L.divIcon({
            className: '',
            html: `<div style="font-size:${size}px;line-height:1;color:${color};text-shadow:0 0 6px rgba(0,0,0,.9);${glow}${highlighted ? 'outline:2px solid #3dd6c6;outline-offset:2px;border-radius:2px;' : ''}">▼</div>`,
            iconSize: [size, size],
            iconAnchor: [size / 2, size / 2],
          }),
          opacity,
        })
          .bindTooltip(`${unplanned ? 'Unplanned · ' : ''}${e.summary}`, { direction: 'top' })
          .addTo(eventLayer)
      } else {
        L.circleMarker([e.lat, e.lon], {
          radius: highlighted || unplanned ? 9 : e.event_type === 'bda' ? 7 : 6,
          color: unplanned ? '#f0c14a' : highlighted ? '#3dd6c6' : color,
          fillColor: color,
          fillOpacity: past || highlighted ? 0.85 : 0.25,
          weight: highlighted || unplanned ? 3 : past ? 2 : 1,
          opacity,
        })
          .bindTooltip(`${unplanned ? 'Unplanned · ' : ''}${e.summary}`, { direction: 'top' })
          .addTo(eventLayer)
      }
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
  <header class="flex items-center justify-between gap-2 border-b border-[var(--line)] px-3 py-2">
    <h2 class="text-sm font-semibold tracking-[0.12em] uppercase text-[var(--accent)]">
      Route & tasks
    </h2>
    <label class="flex cursor-pointer items-center gap-2 text-[11px] text-[var(--muted)]">
      <span>Planned route</span>
      <button
        type="button"
        class="slide-toggle"
        class:on={showPlannedRoute}
        role="switch"
        aria-checked={showPlannedRoute}
        aria-label="Show planned route"
        onclick={() => (showPlannedRoute = !showPlannedRoute)}
      ></button>
    </label>
  </header>
  <div bind:this={mapEl} class="min-h-[280px] flex-1"></div>
</div>
