<script>
  import { formatTime, markerGlyph, sensorColor, toMs } from './api.js'

  let {
    events = [],
    start = null,
    end = null,
    currentTime = null,
    onscrub = undefined,
  } = $props()

  let dragging = $state(false)
  let trackEl = $state(null)

  let startMs = $derived(start ? toMs(start) : 0)
  let endMs = $derived(end ? toMs(end) : 1)
  let span = $derived(Math.max(1, endMs - startMs))
  let currentMs = $derived(currentTime ? toMs(currentTime) : startMs)
  let playheadPct = $derived(((currentMs - startMs) / span) * 100)

  let markers = $derived(
    events
      .filter((e) => e.marker && e.marker !== 'none')
      .map((e) => ({
        ...e,
        pct: ((toMs(e.timestamp) - startMs) / span) * 100,
        color:
          e.marker === 'diamond'
            ? sensorColor(e.sensor)
            : e.marker === 'caret'
              ? '#ff7a45'
              : e.marker === 'flag'
                ? '#5ddea0'
                : '#8fa3c1',
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
    <span class="uppercase">Mission timeline · ◆ collect · ▶ strike</span>
    <span class="mono">{formatTime(end)}</span>
  </div>

  <div
    bind:this={trackEl}
    class="relative h-14 cursor-pointer select-none rounded-sm border border-[var(--line)] bg-[var(--bg-deep)]"
    role="slider"
    tabindex="0"
    aria-valuemin={0}
    aria-valuemax={100}
    aria-valuenow={playheadPct}
    aria-label="Mission time scrubber"
    onpointerdown={onPointerDown}
    onpointermove={onPointerMove}
    onpointerup={onPointerUp}
    onpointercancel={onPointerUp}
  >
    <div
      class="pointer-events-none absolute inset-y-0 left-0 bg-[linear-gradient(90deg,transparent,rgba(61,214,198,0.08))]"
      style={`width:${playheadPct}%`}
    ></div>

    {#each markers as m (m.event_id)}
      <button
        type="button"
        class="absolute top-1/2 -translate-x-1/2 -translate-y-1/2 text-lg leading-none transition-transform hover:scale-125"
        style={`left:${m.pct}%; color:${m.color}`}
        title={`${formatTime(m.timestamp)} — ${m.summary}`}
        onclick={(ev) => {
          ev.stopPropagation()
          onscrub?.(m.timestamp)
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

  <div class="mt-2 mono text-sm text-[var(--accent)]">{formatTime(currentTime)}</div>
</div>
