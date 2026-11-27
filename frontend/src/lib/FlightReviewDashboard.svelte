<script>
  import MissionMap from './MissionMap.svelte'
  import FlightAirDataPanels from './FlightAirDataPanels.svelte'
  import { formatTime } from './api.js'

  let {
    review = null,
    waypoints = [],
    events = [],
    track = [],
    plannedRoute = [],
    showPlannedRoute = $bindable(true),
    platform = null,
    position = null,
    currentTime = null,
    selectedEventId = $bindable(null),
    unmatchedActual = [],
    onscrub = () => {},
  } = $props()

  let metrics = $derived(review?.metrics || {})
  let sensorStrip = $derived(review?.sensor_strip || {})
  let foqaEvents = $derived(review?.events || [])

  function selectFoqa(ev) {
    selectedEventId = ev.source_event_id || ev.event_id
    onscrub(ev.timestamp, selectedEventId)
  }
</script>

<div class="flex h-full min-h-0 flex-col gap-2">
  <div class="flex flex-wrap items-center gap-3 text-xs text-[var(--muted)]">
    <span class="tracking-[0.14em] uppercase text-[var(--accent)]">Flight Review</span>
    <span class="mono">
      {metrics.duration_min ?? '—'} min · max alt {metrics.max_alt_ft ?? '—'} ft · fuel
      {metrics.fuel_start_pct ?? '—'}→{metrics.fuel_end_pct ?? '—'}% · FOQA events
      {metrics.event_count ?? 0}
      {#if metrics.warn_count}
        ({metrics.warn_count} WARN)
      {/if}
    </span>
    <span class="mono">
      Sensor · collects {sensorStrip.collections ?? '—'} · det {sensorStrip.detections ?? '—'} ·
      unused {sensorStrip.opportunities_unused ?? '—'} · uptime {sensorStrip.sensor_uptime_pct ?? '—'}%
    </span>
  </div>

  <div class="grid min-h-0 flex-1 gap-2 lg:grid-cols-12">
    <div class="min-h-0 lg:col-span-5">
      <MissionMap
        {waypoints}
        {events}
        {track}
        {plannedRoute}
        bind:showPlannedRoute
        {platform}
        {position}
        {currentTime}
        highlightEventId={selectedEventId}
        {unmatchedActual}
      />
    </div>
    <div class="flex min-h-0 flex-col gap-2 overflow-auto lg:col-span-4">
      <FlightAirDataPanels
        series={review?.air_series || []}
        {currentTime}
        events={foqaEvents}
      />
    </div>
    <div class="flex min-h-0 flex-col gap-2 lg:col-span-3">
      <div class="panel rounded-sm p-3 text-xs">
        <h3 class="mb-2 text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
          Systems at scrub
        </h3>
        {#if platform}
          <dl class="grid grid-cols-2 gap-2">
            <div>
              <dt class="text-[var(--muted)]">Fuel</dt>
              <dd class="mono">{platform.fuel_percent ?? '—'}%</dd>
            </div>
            <div>
              <dt class="text-[var(--muted)]">Datalink</dt>
              <dd class="mono">{platform.datalink_up ? 'UP' : 'DOWN'}</dd>
            </div>
            <div>
              <dt class="text-[var(--muted)]">Gear / bay</dt>
              <dd class="mono">{platform.gear} / {platform.weapons_bay}</dd>
            </div>
            <div>
              <dt class="text-[var(--muted)]">Readiness</dt>
              <dd class="mono">{platform.readiness}</dd>
            </div>
            <div>
              <dt class="text-[var(--muted)]">Alt / spd</dt>
              <dd class="mono">{platform.alt_ft ?? '—'} ft · {platform.speed_kts ?? '—'} kts</dd>
            </div>
            <div>
              <dt class="text-[var(--muted)]">Att</dt>
              <dd class="mono">
                R {platform.roll_deg ?? '—'}° P {platform.pitch_deg ?? '—'}°
              </dd>
            </div>
          </dl>
        {:else}
          <p class="text-[var(--muted)]">No platform state at scrub.</p>
        {/if}
      </div>

      <div class="panel flex min-h-0 flex-1 flex-col rounded-sm p-3">
        <h3 class="mb-2 text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
          FOQA events
        </h3>
        <ul class="min-h-0 flex-1 space-y-1 overflow-auto text-xs">
          {#each foqaEvents as ev}
            <li>
              <button
                type="button"
                class="w-full rounded-sm border border-transparent px-2 py-1.5 text-left hover:border-[var(--line)] hover:bg-[var(--bg-elevated)]"
                class:border-[var(--accent)]={selectedEventId === ev.source_event_id}
                onclick={() => selectFoqa(ev)}
              >
                <div class="flex items-center justify-between gap-2">
                  <span class="mono text-[var(--muted)]">{formatTime(ev.timestamp)}</span>
                  <span
                    class="text-[10px] uppercase"
                    class:text-[var(--danger)]={ev.severity === 'WARN'}
                    class:text-[var(--strike)]={ev.severity !== 'WARN'}
                  >
                    {ev.severity}
                  </span>
                </div>
                <div class="text-[var(--text)]">{ev.title}</div>
                <div class="text-[10px] text-[var(--muted)]">{ev.detail}</div>
              </button>
            </li>
          {:else}
            <li class="text-[var(--muted)]">No threshold events for this mission.</li>
          {/each}
        </ul>
      </div>
    </div>
  </div>
</div>