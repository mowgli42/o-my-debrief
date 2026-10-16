<script>
  import { formatTime, markerGlyph, sensorColor, toMs } from './api.js'

  let {
    planEvents = [],
    actualEvents = [],
    pairs = [],
    unmatchedActual = [],
    start = null,
    end = null,
    currentTime = null,
    highlightEventId = null,
    hidePlan = false,
    onscrub = undefined,
  } = $props()

  let dragging = $state(false)
  let trackEl = $state(null)

  let startMs = $derived(start ? toMs(start) : 0)
  let endMs = $derived(end ? toMs(end) : 1)
  let span = $derived(Math.max(1, endMs - startMs))
  let currentMs = $derived(currentTime ? toMs(currentTime) : startMs)
  let playheadPct = $derived(((currentMs - startMs) / span) * 100)

  let unmatchedSet = $derived(new Set(unmatchedActual))

  function pctOf(iso) {
    return ((toMs(iso) - startMs) / span) * 100
  }

  function colorFor(e) {
    if (e.marker === 'diamond') return sensorColor(e.sensor)
    if (e.marker === 'caret') return '#ff7a45'
    if (e.marker === 'flag') return '#5ddea0'
    return '#8fa3c1'
  }

  let planMarkers = $derived(
    (planEvents || [])
      .filter((e) => e.marker && e.marker !== 'none')
      .map((e) => ({
        id: e.plan_event_id,
        timestamp: e.timestamp,
        summary: e.summary,
        marker: e.marker,
        pct: pctOf(e.timestamp),
        color: colorFor(e),
      })),
  )

  let actualMarkers = $derived(
    (actualEvents || [])
      .filter((e) => e.marker && e.marker !== 'none')
      .map((e) => ({
        id: e.event_id,
        timestamp: e.timestamp,
        summary: e.summary,
        marker: e.marker,
        pct: pctOf(e.timestamp),
        color: colorFor(e),
        unplanned: unmatchedSet.has(e.event_id),
        highlighted: highlightEventId && e.event_id === highlightEventId,
      })),
  )

  let linkLines = $derived(
    hidePlan
      ? []
      : (pairs || [])
          .map((p) => {
            const plan = planMarkers.find((m) => m.id === p.plan_event_id)
            const act = actualMarkers.find((m) => m.id === p.actual_event_id)
            if (!plan || !act) return null
            return { key: `${p.plan_event_id}:${p.actual_event_id}`, x1: plan.pct, x2: act.pct }
          })
          .filter(Boolean),
  )

  function pctFromClientX(clientX) {
    if (!trackEl) return 0
    const rect = trackEl.getBoundingClientRect()
    return Math.min(1, Math.max(0, (clientX - rect.left) / rect.width))
  }

  function scrubTo(clientX) {
    const pct = pctFromClientX(clientX)
    const ms = startMs + pct * span
    onscrub?.(new Date(ms).toISOString().replace(/\.\d{3}Z$/, 'Z'))
  }

  function onPointerDown(e) {
    dragging = true
    scrubTo(e.clientX)
    e.currentTarget.setPointerCapture?.(e.pointerId)
  }

  function onPointerMove(e) {
    if (!dragging) return
    scrubTo(e.clientX)
  }

  function onPointerUp() {
    dragging = false
  }
</script>

<div class="timeline panel rounded-sm p-3">
  <div class="mb-2 flex items-center justify-between text-xs tracking-wide text-[var(--muted)]">
    <span class="mono">{formatTime(start)}</span>
    <span class="uppercase">Compare · plan above as-executed</span>
    <span class="mono">{formatTime(end)}</span>
  </div>

  <div
    bind:this={trackEl}
    class="relative cursor-pointer select-none rounded-sm border border-[var(--line)] bg-[var(--bg-deep)]"
    class:h-[7.5rem]={!hidePlan}
    class:h-[3.75rem]={hidePlan}
    role="slider"
    tabindex="0"
    aria-valuemin={0}
    aria-valuenow={playheadPct}
    aria-valuemax={100}
    aria-label="Compare mission time scrubber"
    onpointerdown={onPointerDown}
    onpointermove={onPointerMove}
    onpointerup={onPointerUp}
    onpointercancel={onPointerUp}
  >
    <div
      class="pointer-events-none absolute inset-y-0 left-0 bg-[linear-gradient(90deg,transparent,rgba(61,214,198,0.08))]"
      style={`width:${playheadPct}%`}
    ></div>

    {#if !hidePlan}
      <div class="pointer-events-none absolute inset-x-0 top-1/2 border-t border-[var(--line)]/50"></div>
      <div
        class="pointer-events-none absolute left-1 top-1 text-[8px] uppercase tracking-wider text-[var(--muted)]"
      >
        Plan
      </div>
      <div
        class="pointer-events-none absolute left-1 bottom-1 text-[8px] uppercase tracking-wider text-[var(--muted)]"
      >
        Actual
      </div>

      <svg class="pointer-events-none absolute inset-0 h-full w-full" aria-hidden="true">
        {#each linkLines as line (line.key)}
          <line
            x1={`${line.x1}%`}
            y1="28%"
            x2={`${line.x2}%`}
            y2="72%"
            stroke="rgba(143,163,193,0.55)"
            stroke-width="1.25"
            stroke-dasharray="3 3"
          />
        {/each}
      </svg>

      {#each planMarkers as m (m.id)}
        <button
          type="button"
          class="absolute -translate-x-1/2 -translate-y-1/2 min-h-6 min-w-6 text-base leading-none opacity-70 transition-transform hover:scale-125 hover:opacity-100"
          style={`left:${m.pct}%; top:28%; color:${m.color}`}
          title={`Plan ${formatTime(m.timestamp)} — ${m.summary}`}
          onclick={(ev) => {
            ev.stopPropagation()
            onscrub?.(m.timestamp)
          }}
        >
          {markerGlyph(m.marker)}
        </button>
      {/each}
    {/if}

    {#each actualMarkers as m (m.id)}
      <button
        type="button"
        class="absolute -translate-x-1/2 -translate-y-1/2 min-h-6 min-w-6 leading-none transition-transform hover:scale-125"
        class:text-base={!m.highlighted}
        class:text-lg={m.highlighted}
        class:scale-125={m.highlighted}
        class:unplanned-glow={m.unplanned}
        style={`left:${m.pct}%; top:${hidePlan ? 50 : 72}%; color:${m.color}; ${m.highlighted ? 'outline:2px solid var(--accent); outline-offset:2px; border-radius:2px;' : ''}`}
        title={`${m.unplanned ? 'Unplanned · ' : ''}${formatTime(m.timestamp)} — ${m.summary}`}
        data-event-id={m.id}
        aria-current={m.highlighted ? 'true' : undefined}
        onclick={(ev) => {
          ev.stopPropagation()
          onscrub?.(m.timestamp, m.id)
        }}
      >
        {markerGlyph(m.marker)}
      </button>
    {/each}

    <div
      class="pointer-events-none absolute top-0 bottom-0 w-0.5 bg-[var(--accent)] shadow-[0_0_8px_rgba(61,214,198,0.7)]"
      style={`left:${playheadPct}%`}
    ></div>
  </div>

  <div class="mt-1 flex items-center justify-between gap-2">
    <div class="mono text-sm text-[var(--accent)]">{formatTime(currentTime)}</div>
    <div class="text-[10px] text-[var(--muted)]">
      {pairs.length} paired · {unmatchedActual.length} unplanned
    </div>
  </div>
</div>

<style>
  :global(.unplanned-glow) {
    filter: drop-shadow(0 0 6px rgba(255, 193, 74, 0.95)) drop-shadow(0 0 12px rgba(255, 122, 69, 0.75));
    animation: unplanned-pulse 1.6s ease-in-out infinite;
  }

  @keyframes unplanned-pulse {
    0%,
    100% {
      filter: drop-shadow(0 0 4px rgba(255, 193, 74, 0.7)) drop-shadow(0 0 8px rgba(255, 122, 69, 0.5));
    }
    50% {
      filter: drop-shadow(0 0 10px rgba(255, 193, 74, 1)) drop-shadow(0 0 16px rgba(255, 122, 69, 0.9));
    }
  }
</style>
