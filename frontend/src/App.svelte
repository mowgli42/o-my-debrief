<script>
  import { onMount } from 'svelte'
  import Timeline from './lib/Timeline.svelte'
  import Milestones from './lib/Milestones.svelte'
  import MissionMap from './lib/MissionMap.svelte'
  import VehicleStatus from './lib/VehicleStatus.svelte'
  import {
    fetchEvents,
    fetchMilestones,
    fetchMissions,
    fetchPositionAt,
    fetchStateAt,
    fetchSummary,
    fetchTrack,
    fetchWaypoints,
    formatTime,
    toMs,
  } from './lib/api.js'

  let missions = $state([])
  let missionId = $state('')
  let mission = $derived(missions.find((m) => m.mission_id === missionId) || null)
  let events = $state([])
  let milestones = $state([])
  let waypoints = $state([])
  let track = $state([])
  let platformState = $state(null)
  let position = $state(null)
  let currentTime = $state(null)
  let playing = $state(false)
  let error = $state('')
  let loading = $state(true)
  let summaryOpen = $state(false)
  let summaryText = $state('')
  let selectedEventId = $state(null)
  let playTimer = null

  async function loadMission(id) {
    loading = true
    error = ''
    try {
      const [ev, ms, wp, tr] = await Promise.all([
        fetchEvents(id),
        fetchMilestones(id),
        fetchWaypoints(id),
        fetchTrack(id),
      ])
      events = ev
      milestones = ms
      waypoints = wp
      track = tr
      const m = missions.find((x) => x.mission_id === id)
      currentTime = m?.start_time || ev[0]?.timestamp
      await refreshState()
    } catch (e) {
      error = String(e.message || e)
    } finally {
      loading = false
    }
  }

  async function refreshState() {
    if (!missionId || !currentTime) return
    try {
      const [st, pos] = await Promise.all([
        fetchStateAt(missionId, currentTime),
        fetchPositionAt(missionId, currentTime).catch(() => null),
      ])
      platformState = st
      position = pos
      // Prefer interpolated kinematics on platform panel when available
      if (pos && platformState) {
        platformState = {
          ...platformState,
          lat: pos.lat ?? platformState.lat,
          lon: pos.lon ?? platformState.lon,
          heading_deg: pos.heading_deg ?? platformState.heading_deg,
          alt_ft: pos.alt_ft ?? platformState.alt_ft,
          speed_kts: pos.speed_kts ?? platformState.speed_kts,
          roll_deg: pos.roll_deg ?? platformState.roll_deg,
          pitch_deg: pos.pitch_deg ?? platformState.pitch_deg,
        }
      }
    } catch (e) {
      error = String(e.message || e)
    }
  }

  function scrub(iso, eventId = null) {
    currentTime = iso
    selectedEventId = eventId
    refreshState()
  }

  function selectMilestone(m) {
    scrub(m.timestamp, m.event_id || null)
  }

  function togglePlay() {
    playing = !playing
  }

  $effect(() => {
    if (playTimer) {
      clearInterval(playTimer)
      playTimer = null
    }
    if (!playing || !mission) return
    const end = toMs(mission.end_time)
    // ~20× realtime with smooth map steps (~3s mission time / 200ms frame)
    playTimer = setInterval(() => {
      const cur = toMs(currentTime)
      const next = Math.min(end, cur + 3_000)
      currentTime = new Date(next).toISOString().replace(/\.\d{3}Z$/, 'Z')
      refreshState()
      if (next >= end) playing = false
    }, 200)
    return () => {
      if (playTimer) clearInterval(playTimer)
    }
  })

  function exportJson() {
    const bundle = {
      mission,
      exported_at: new Date().toISOString(),
      current_time: currentTime,
      milestones,
      state: platformState,
      summary: summaryText || null,
      event_count: events.length,
      events: events.map((e) => ({
        event_id: e.event_id,
        timestamp: e.timestamp,
        event_type: e.event_type,
        summary: e.summary,
        marker: e.marker,
        target_id: e.target_id,
      })),
    }
    const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${missionId || 'debrief'}-export.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  async function openSummary() {
    if (!missionId) return
    try {
      const s = await fetchSummary(missionId)
      summaryText = s.narrative || ''
      summaryOpen = true
    } catch (e) {
      error = String(e.message || e)
    }
  }

  async function onMissionChange(e) {
    missionId = e.currentTarget.value
    playing = false
    await loadMission(missionId)
  }

  onMount(async () => {
    try {
      missions = await fetchMissions()
      if (missions.length) {
        missionId = missions[0].mission_id
        await loadMission(missionId)
      } else {
        error = 'No missions in manifest — run make fixtures'
        loading = false
      }
    } catch (e) {
      error = String(e.message || e)
      loading = false
    }
  })
</script>

<div class="flex h-screen min-h-0 flex-col overflow-hidden">
  <header
    class="shrink-0 flex flex-wrap items-center gap-3 border-b border-[var(--line)] bg-[color-mix(in_srgb,var(--bg-panel)_90%,transparent)] px-4 py-3"
  >
    <div>
      <div class="text-[10px] tracking-[0.2em] uppercase text-[var(--muted)]">Open Arsenal · o-my</div>
      <h1 class="text-xl font-semibold tracking-wide text-[var(--text)]">Platform Debrief</h1>
    </div>

    <label class="ml-2 flex items-center gap-2 text-sm">
      <span class="text-[var(--muted)]">Mission</span>
      <select
        class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] px-2 py-1.5 mono text-sm"
        value={missionId}
        onchange={onMissionChange}
      >
        {#each missions as m}
          <option value={m.mission_id}>{m.name}</option>
        {/each}
      </select>
    </label>

    <div class="mono text-sm text-[var(--accent)]">{formatTime(currentTime)}</div>

    <div class="ml-auto flex items-center gap-2">
      <button
        type="button"
        class="rounded-sm border border-[var(--line)] bg-[var(--bg-elevated)] px-3 py-1.5 text-sm hover:border-[var(--accent)]"
        onclick={togglePlay}
      >
        {playing ? 'Pause' : 'Play'}
      </button>
      <button
        type="button"
        class="rounded-sm border border-[var(--line)] bg-[var(--bg-elevated)] px-3 py-1.5 text-sm hover:border-[var(--accent)]"
        onclick={openSummary}
      >
        AAR Summary
      </button>
      <button
        type="button"
        class="rounded-sm border border-[var(--accent)] bg-[rgba(61,214,198,0.12)] px-3 py-1.5 text-sm text-[var(--accent)]"
        onclick={exportJson}
      >
        Export Debrief Report
      </button>
    </div>
  </header>

  {#if error}
    <div class="border-b border-[var(--danger)] bg-[rgba(255,92,108,0.12)] px-4 py-2 text-sm text-[var(--danger)]">
      {error}
    </div>
  {/if}

  <div class="shrink-0 px-4 pt-3">
    <Timeline
      {events}
      start={mission?.start_time}
      end={mission?.end_time}
      {currentTime}
      highlightEventId={selectedEventId}
      onscrub={scrub}
    />
  </div>

  <main class="grid min-h-0 flex-1 grid-cols-1 gap-3 overflow-hidden p-4 lg:grid-cols-12">
    <div class="min-h-0 lg:col-span-3">
      <Milestones
        {milestones}
        {currentTime}
        selectedEventId={selectedEventId}
        onselect={selectMilestone}
      />
    </div>
    <div class="min-h-0 lg:col-span-6">
      <MissionMap
        {waypoints}
        {events}
        {track}
        platform={platformState}
        {position}
        {currentTime}
        highlightEventId={selectedEventId}
      />
    </div>
    <div class="min-h-0 lg:col-span-3">
      <VehicleStatus platform={platformState} />
    </div>
  </main>

  {#if summaryOpen}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div class="panel max-h-[80vh] w-full max-w-2xl overflow-auto rounded-sm p-4">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-sm font-semibold tracking-[0.12em] uppercase text-[var(--accent)]">
            After-action summary
          </h2>
          <button
            type="button"
            class="text-sm text-[var(--muted)] hover:text-[var(--text)]"
            onclick={() => (summaryOpen = false)}
          >
            Close
          </button>
        </div>
        <pre class="mono whitespace-pre-wrap text-sm text-[var(--text)]">{summaryText}</pre>
      </div>
    </div>
  {/if}

  {#if loading}
    <div class="pointer-events-none fixed inset-0 flex items-center justify-center bg-black/40">
      <div class="panel rounded-sm px-4 py-3 text-sm">Loading mission…</div>
    </div>
  {/if}
</div>
