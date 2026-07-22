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
    fetchStateAt,
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
  let platformState = $state(null)
  let currentTime = $state(null)
  let playing = $state(false)
  let error = $state('')
  let loading = $state(true)
  let playTimer = null

  async function loadMission(id) {
    loading = true
    error = ''
    try {
      const [ev, ms, wp] = await Promise.all([
        fetchEvents(id),
        fetchMilestones(id),
        fetchWaypoints(id),
      ])
      events = ev
      milestones = ms
      waypoints = wp
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
      platformState = await fetchStateAt(missionId, currentTime)
    } catch (e) {
      error = String(e.message || e)
    }
  }

  function scrub(iso) {
    currentTime = iso
    refreshState()
  }

  function selectMilestone(m) {
    scrub(m.timestamp)
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
    const start = toMs(mission.start_time)
    const end = toMs(mission.end_time)
    playTimer = setInterval(() => {
      const cur = toMs(currentTime)
      const next = Math.min(end, cur + 15_000)
      currentTime = new Date(next).toISOString().replace(/\.\d{3}Z$/, 'Z')
      refreshState()
      if (next >= end) playing = false
    }, 400)
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

<div class="flex h-full min-h-screen flex-col">
  <header
    class="flex flex-wrap items-center gap-3 border-b border-[var(--line)] bg-[color-mix(in_srgb,var(--bg-panel)_90%,transparent)] px-4 py-3"
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

  <div class="px-4 pt-3">
    <Timeline
      {events}
      start={mission?.start_time}
      end={mission?.end_time}
      {currentTime}
      onscrub={scrub}
    />
  </div>

  <main class="grid min-h-0 flex-1 grid-cols-1 gap-3 p-4 lg:grid-cols-12">
    <div class="min-h-[320px] lg:col-span-3">
      <Milestones {milestones} {currentTime} onselect={selectMilestone} />
    </div>
    <div class="min-h-[320px] lg:col-span-6">
      <MissionMap {waypoints} {events} platform={platformState} {currentTime} />
    </div>
    <div class="min-h-[320px] lg:col-span-3">
      <VehicleStatus platform={platformState} />
    </div>
  </main>

  {#if loading}
    <div class="pointer-events-none fixed inset-0 flex items-center justify-center bg-black/40">
      <div class="panel rounded-sm px-4 py-3 text-sm">Loading mission…</div>
    </div>
  {/if}
</div>
