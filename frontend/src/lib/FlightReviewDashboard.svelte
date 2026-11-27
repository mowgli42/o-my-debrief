<script>
  import MissionMap from './MissionMap.svelte'
  import FlightAirDataPanels from './FlightAirDataPanels.svelte'
  import { formatTime, flightPerformanceReportUrl } from './api.js'

  let {
    review = null,
    fleetTrends = null,
    missionId = '',
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
  let pva = $derived(review?.planned_vs_actual || {})
  let healthTimeline = $derived(review?.health_timeline || [])
  let exceedance = $derived(metrics.exceedance_stats || {})
  let exceedanceEntries = $derived(
    Object.entries(exceedance).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])),
  )
  let fleetRows = $derived(fleetTrends?.missions || [])
  let fleetAgg = $derived(fleetTrends?.aggregates || {})

  let healthAtScrub = $derived.by(() => {
    if (!healthTimeline.length || !currentTime) return null
    const t = new Date(currentTime).getTime()
    let best = healthTimeline[0]
    let bestD = Infinity
    for (const h of healthTimeline) {
      const d = Math.abs(new Date(h.timestamp).getTime() - t)
      if (d < bestD) {
        bestD = d
        best = h
      }
    }
    return best
  })

  function selectFoqa(ev) {
    selectedEventId = ev.source_event_id || ev.event_id
    onscrub(ev.timestamp, selectedEventId)
  }

  function openFlightReport() {
    if (!missionId) return
    const w = window.open(flightPerformanceReportUrl(missionId), '_blank', 'noopener')
    if (w) {
      w.onload = () => {
        try {
          w.focus()
          w.print()
        } catch {
          /* user can print manually */
        }
      }
    }
  }

  function flagClass(ok) {
    return ok === false ? 'text-[var(--danger)]' : 'text-[var(--text)]'
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
    {#if pva.available}
      <span class="mono">
        Plan vs actual · XTE μ {pva.mean_xte_nm ?? '—'} / max {pva.max_xte_nm ?? '—'} nm · |Δalt|
        {pva.mean_abs_alt_error_ft ?? '—'} ft · |Δspd| {pva.mean_abs_spd_error_kts ?? '—'} kts
      </span>
    {/if}
    <button
      type="button"
      class="ml-auto rounded-sm border border-[var(--line)] bg-[var(--bg-elevated)] px-2 py-1 text-xs hover:border-[var(--accent)]"
      onclick={openFlightReport}
    >
      Flight Performance Report
    </button>
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

      <div class="panel rounded-sm p-3 text-xs">
        <h3 class="mb-2 text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
          Health timeline
        </h3>
        {#if healthAtScrub}
          <dl class="mb-2 grid grid-cols-3 gap-2">
            <div>
              <dt class="text-[var(--muted)]">Datalink</dt>
              <dd class="mono {flagClass(healthAtScrub.datalink_up)}">
                {healthAtScrub.datalink_up ? 'UP' : 'DOWN'}
              </dd>
            </div>
            <div>
              <dt class="text-[var(--muted)]">Bus</dt>
              <dd class="mono {flagClass(healthAtScrub.bus_ok)}">
                {healthAtScrub.bus_ok ? 'OK' : 'LOW'}
              </dd>
            </div>
            <div>
              <dt class="text-[var(--muted)]">EGT</dt>
              <dd class="mono {flagClass(healthAtScrub.egt_ok)}">
                {healthAtScrub.egt_ok ? 'OK' : 'HOT'}
              </dd>
            </div>
            <div>
              <dt class="text-[var(--muted)]">Fuel</dt>
              <dd class="mono {healthAtScrub.fuel_band === 'bingo' ? 'text-[var(--danger)]' : ''}">
                {healthAtScrub.fuel_band}
              </dd>
            </div>
            <div>
              <dt class="text-[var(--muted)]">Gear</dt>
              <dd class="mono">{healthAtScrub.gear ?? '—'}</dd>
            </div>
            <div>
              <dt class="text-[var(--muted)]">Readiness</dt>
              <dd class="mono">{healthAtScrub.readiness ?? '—'}</dd>
            </div>
          </dl>
        {/if}
        <div class="flex flex-wrap gap-1">
          {#each healthTimeline as h}
            {@const bad =
              h.datalink_up === false || h.bus_ok === false || h.egt_ok === false || h.fuel_band === 'bingo'}
            <button
              type="button"
              class="h-2.5 w-2.5 rounded-sm border border-transparent"
              class:bg-[var(--danger)]={bad}
              class:bg-[var(--accent)]={!bad}
              class:opacity-40={!bad}
              class:ring-1={currentTime && Math.abs(new Date(h.timestamp) - new Date(currentTime)) < 90_000}
              class:ring-[var(--accent)]={currentTime &&
                Math.abs(new Date(h.timestamp) - new Date(currentTime)) < 90_000}
              title="{formatTime(h.timestamp)} · dl {h.datalink_up ? 'up' : 'down'} · bus {h.bus_ok
                ? 'ok'
                : 'low'}"
              onclick={() => onscrub(h.timestamp, null)}
            ></button>
          {:else}
            <span class="text-[var(--muted)]">No health samples.</span>
          {/each}
        </div>
      </div>
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

      <div class="panel rounded-sm p-3 text-xs">
        <h3 class="mb-2 text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
          Exceedance counts
        </h3>
        <ul class="space-y-1 mono">
          {#each exceedanceEntries as [rid, n]}
            <li class="flex justify-between gap-2">
              <span class="text-[var(--muted)]">{rid}</span>
              <span>{n}</span>
            </li>
          {:else}
            <li class="text-[var(--muted)]">None</li>
          {/each}
        </ul>
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

      <div class="panel rounded-sm p-3 text-xs">
        <h3 class="mb-2 text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
          Fleet trends
        </h3>
        {#if fleetRows.length}
          <p class="mb-2 mono text-[var(--muted)]">
            {fleetTrends.count} mission(s) · warns {fleetAgg.total_warns ?? '—'} · collections
            {fleetAgg.total_collections ?? '—'} · μ uptime {fleetAgg.mean_sensor_uptime_pct ?? '—'}%
          </p>
          <ul class="space-y-1">
            {#each fleetRows as row}
              <li class="flex justify-between gap-2 mono">
                <span class="truncate text-[var(--muted)]" title={row.name}>{row.mission_id}</span>
                <span
                  >{row.warn_count ?? 0}W · XTE {row.mean_xte_nm ?? '—'} · {row.sensor_uptime_pct ?? '—'}%</span
                >
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-[var(--muted)]">No fleet rollup.</p>
        {/if}
      </div>
    </div>
  </div>
</div>
