const API = import.meta.env.VITE_API_BASE || ''

async function get(path) {
  const r = await fetch(`${API}${path}`)
  if (!r.ok) throw new Error(`${r.status} ${path}`)
  return r.json()
}

export function fetchMissions() {
  return get('/api/missions')
}

export function fetchEvents(mission) {
  return get(`/api/events?mission=${encodeURIComponent(mission)}`)
}

export function fetchMilestones(mission) {
  return get(`/api/milestones?mission=${encodeURIComponent(mission)}`)
}

export function fetchStateAt(mission, time) {
  return get(
    `/api/state_at?mission=${encodeURIComponent(mission)}&time=${encodeURIComponent(time)}`,
  )
}

export function fetchWaypoints(mission) {
  return get(`/api/missions/${encodeURIComponent(mission)}/waypoints`)
}

export function fetchTrack(mission) {
  return get(`/api/track?mission=${encodeURIComponent(mission)}`)
}

export function fetchPositionAt(mission, time) {
  return get(
    `/api/position_at?mission=${encodeURIComponent(mission)}&time=${encodeURIComponent(time)}`,
  )
}

export function fetchSummary(mission) {
  return get(`/api/summary?mission=${encodeURIComponent(mission)}`)
}

export function sensorColor(sensor) {
  const s = (sensor || '').toUpperCase()
  if (s === 'EO') return '#4da3ff'
  if (s === 'IR') return '#ff5c6c'
  if (s === 'SAR') return '#5ddea0'
  return '#3dd6c6'
}

export function markerGlyph(marker) {
  if (marker === 'diamond') return '◆'
  if (marker === 'caret') return '▼'
  if (marker === 'flag') return '⚑'
  if (marker === 'circle') return '●'
  return '·'
}

export function formatTime(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toISOString().slice(11, 19) + 'Z'
  } catch {
    return iso
  }
}

export function toMs(iso) {
  return new Date(iso).getTime()
}
