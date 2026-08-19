<script>
  import { formatTime, markerGlyph, sensorColor, toMs } from './api.js'

  let {
    events = [],
    start = null,
    end = null,
    currentTime = null,
    highlightEventId = null,
    onscrub = undefined,
  } = $props()

  let dragging = $state(false)
  let trackEl = $state(null)

  let startMs = $derived(start ? toMs(start) : 0)
  let endMs = $derived(end ? toMs(end) : 1)
  let span = $derived(Math.max(1, endMs - startMs))
  let currentMs = $derived(currentTime ? toMs(currentTime) : startMs)
  let playheadPct = $derived(((currentMs - startMs) / span) * 100)

  /** Lane 0 waypoints (top) → 1 milestones → 2 collects → 3 strikes (bottom). */
  function laneFor(e) {
    if (e.event_type === 'waypoint') return 0
    if (e.marker === 'caret' || e.event_type === 'task') return 3
    if (e.marker === 'diamond' || e.event_type === 'sensorCollect') return 2
    return 1
  }

  const LANE_TOP = [16, 38, 60, 82]

  let markers = $derived(
    events
      .filter((e) => e.marker && e.marker !== 'none')
      .map((e) => ({
        ...e,
        pct: ((toMs(e.timestamp) - startMs) / span) * 100,
        lane: laneFor(e),
        hasVideo: Boolean(e.payload?.media_clip_id),
        color:
          e.marker === 'diamond'
            ? sensorColor(e.sensor)
            : e.marker === 'caret'
              ? '#ff7a45'
              : e.marker === 'flag'
                ? '#5ddea0'
                : '#8fa3c1',
        highlighted: highlightEventId && e.event_id === highlightEventId,
      })),
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
    <span class="uppercase">Mission timeline · lanes WP · MS · ◆ · ▼</span>
    <span class="mono">{formatTime(end)}</span>
  </div>

  <div class="flex items-stretch gap-1.5">
    <div
      class="flex w-7 shrink-0 flex-col justify-between py-0.5 text-[8px] uppercase leading-none tracking-wider text-[var(--muted)]"
      aria-hidden="true"
    >
      <span>WP</span>
      <span>MS</span>
      <span>◆</span>
      <span>▼</span>
    </div>
    <div
      bind:this={trackEl}
      class="relative h-[4.75rem] min-w-0 flex-1 cursor-pointer select-none rounded-sm border border-[var(--line)] bg-[var(--bg-deep)]"
      role="slider"
      tabindex="0"
      aria-valuemin={0}
      aria-valuenow={playheadPct}
      aria-valuemax={100}
      aria-label="Mission time scrubber"
      onpointerdown={onPointerDown}
      onpointermove={onPointerMove}
      onpointerup={onPointerUp}
      onpointercancel={onPointerUp}
    >
    <div class="pointer-events-none absolute inset-x-0 top-[27%] border-t border-[var(--line)]/40"></div>
    <div class="pointer-events-none absolute inset-x-0 top-[49%] border-t border-[var(--line)]/40"></div>
    <div class="pointer-events-none absolute inset-x-0 top-[71%] border-t border-[var(--line)]/40"></div>

    <div
      class="pointer-events-none absolute inset-y-0 left-0 bg-[linear-gradient(90deg,transparent,rgba(61,214,198,0.08))]"
      style={`width:${playheadPct}%`}
    ></div>

    {#each markers as m (m.event_id)}
      <button
        type="button"
        class="absolute -translate-x-1/2 -translate-y-1/2 min-h-6 min-w-6 leading-none transition-transform hover:scale-125"
        class:text-lg={!m.highlighted}
        class:text-xl={m.highlighted}
        class:scale-125={m.highlighted}
        class:drop-shadow-[0_0_8px_rgba(255,122,69,0.9)]={m.highlighted && m.marker === 'caret'}
        class:drop-shadow-[0_0_8px_rgba(61,214,198,0.9)]={m.highlighted && m.marker !== 'caret'}
        style={`left:${m.pct}%; top:${LANE_TOP[m.lane]}%; color:${m.color}; ${m.highlighted ? 'outline:2px solid var(--accent); outline-offset:2px; border-radius:2px;' : ''}`}
        title={`${formatTime(m.timestamp)} — ${m.summary}${m.hasVideo ? ' · video' : ''}`}
        data-event-id={m.event_id}
        data-lane={m.lane}
        aria-current={m.highlighted ? 'true' : undefined}
        onclick={(ev) => {
          ev.stopPropagation()
          onscrub?.(m.timestamp, m.event_id)
        }}
      >
        {markerGlyph(m.marker)}
        {#if m.hasVideo}
          <span
            class="absolute -bottom-0.5 left-1/2 h-1 w-1 -translate-x-1/2 rounded-full bg-[var(--collect)]"
            aria-hidden="true"
          ></span>
        {/if}
      </button>
    {/each}

    <div
      class="pointer-events-none absolute top-0 bottom-0 w-0.5 bg-[var(--accent)] shadow-[0_0_8px_rgba(61,214,198,0.7)]"
      style={`left:${playheadPct}%`}
    ></div>
    </div>
  </div>

  <div class="mt-1 mono text-sm text-[var(--accent)]">{formatTime(currentTime)}</div>
</div>
