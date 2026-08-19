<script>
  /**
   * Altitude-vs-time profile for launch / recovery.
   * Auto-zooms takeoff (first ~12% of time) or landing (last ~12%) when scrubbing
   * near those segments; Full / Takeoff / Landing can override.
   */
  let { track = [], currentTime = null, altitude = null, gear = null } = $props()

  const W = 320
  const H = 120
  const PAD = { l: 36, r: 10, t: 12, b: 22 }
  const EDGE = 0.12
  const WINDOW = 0.2

  /** @type {'auto' | 'full' | 'takeoff' | 'landing'} */
  let zoomMode = $state('auto')

  let profile = $derived.by(() => {
    const pts = (track || [])
      .filter((s) => s?.timestamp && s.alt_ft != null && Number.isFinite(Number(s.alt_ft)))
      .map((s) => ({
        t: new Date(s.timestamp).getTime(),
        alt: Number(s.alt_ft),
      }))
      .filter((p) => Number.isFinite(p.t))
    if (pts.length < 2) return null

    const t0 = pts[0].t
    const t1 = pts[pts.length - 1].t
    const span = Math.max(1, t1 - t0)

    let cursorFrac = 0
    let cursorAlt = altitude
    if (currentTime) {
      const ct = new Date(currentTime).getTime()
      if (Number.isFinite(ct)) {
        cursorFrac = Math.min(1, Math.max(0, (ct - t0) / span))
        if (cursorAlt == null || !Number.isFinite(Number(cursorAlt))) {
          for (let i = 0; i < pts.length - 1; i++) {
            if (ct >= pts[i].t && ct <= pts[i + 1].t) {
              const f = (ct - pts[i].t) / Math.max(1, pts[i + 1].t - pts[i].t)
              cursorAlt = pts[i].alt + (pts[i + 1].alt - pts[i].alt) * f
              break
            }
          }
          if (cursorAlt == null) cursorAlt = pts[pts.length - 1].alt
        }
      }
    }

    let phase = 'full'
    if (zoomMode === 'takeoff' || zoomMode === 'landing' || zoomMode === 'full') {
      phase = zoomMode
    } else if (cursorFrac <= EDGE) {
      phase = 'takeoff'
    } else if (cursorFrac >= 1 - EDGE) {
      phase = 'landing'
    }

    let view0 = t0
    let view1 = t1
    if (phase === 'takeoff') {
      view1 = t0 + span * WINDOW
    } else if (phase === 'landing') {
      view0 = t1 - span * WINDOW
    }
    const viewSpan = Math.max(1, view1 - view0)

    const viewPts = pts.filter((p) => p.t >= view0 - 1 && p.t <= view1 + 1)
    const alts = (viewPts.length ? viewPts : pts).map((p) => p.alt)
    const amin = Math.min(0, ...alts)
    const amax = Math.max(...alts, amin + 200)
    const arange = Math.max(1, amax - amin)

    const innerW = W - PAD.l - PAD.r
    const innerH = H - PAD.t - PAD.b

    const xy = pts
      .filter((p) => p.t >= view0 && p.t <= view1)
      .map((p) => ({
        x: PAD.l + ((p.t - view0) / viewSpan) * innerW,
        y: PAD.t + (1 - (p.alt - amin) / arange) * innerH,
        t: p.t,
        alt: p.alt,
      }))

    if (xy.length < 2) return null

    const d = xy.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')

    const ct = currentTime ? new Date(currentTime).getTime() : NaN
    let cursorX = null
    let cursorY = null
    if (Number.isFinite(ct) && ct >= view0 && ct <= view1) {
      cursorX = PAD.l + ((ct - view0) / viewSpan) * innerW
      cursorY = PAD.t + (1 - (Number(cursorAlt) - amin) / arange) * innerH
    }

    const phases = []
    for (let i = 0; i < xy.length - 1; i++) {
      const da = xy[i + 1].alt - xy[i].alt
      const kind = da > 800 ? 'climb' : da < -800 ? 'descent' : 'level'
      phases.push({ x0: xy[i].x, x1: xy[i + 1].x, kind })
    }

    const ticks = [amin, amin + arange / 2, amax].map((a) => ({
      alt: Math.round(a),
      y: PAD.t + (1 - (a - amin) / arange) * innerH,
    }))

    const overview = pts.map((p) => ({
      x: PAD.l + ((p.t - t0) / span) * innerW,
      alt: p.alt,
    }))
    const winX0 = PAD.l + ((view0 - t0) / span) * innerW
    const winX1 = PAD.l + ((view1 - t0) / span) * innerW

    return {
      d,
      xy,
      cursorX,
      cursorY,
      cursorAlt,
      phases,
      ticks,
      amin,
      amax,
      phase,
      overview,
      winX0,
      winX1,
    }
  })

  function phaseFill(kind) {
    if (kind === 'climb') return 'rgba(93,222,160,0.12)'
    if (kind === 'descent') return 'rgba(255,122,69,0.12)'
    return 'rgba(77,163,255,0.06)'
  }

  const zoomButtons = [
    ['auto', 'Auto'],
    ['full', 'Full'],
    ['takeoff', 'Takeoff'],
    ['landing', 'Landing'],
  ]
</script>

<section class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2">
  <div class="mb-1 flex items-center justify-between gap-2 text-[10px] uppercase tracking-wider text-[var(--muted)]">
    <span>Altitude profile</span>
    <span class="mono normal-case tracking-normal">
      {profile?.cursorAlt != null ? `${Math.round(profile.cursorAlt).toLocaleString()} ft` : '—'}
      {#if gear}
        · gear {gear}
      {/if}
      {#if profile?.phase && profile.phase !== 'full'}
        · {profile.phase}
      {/if}
    </span>
  </div>

  <div class="mb-1.5 flex flex-wrap gap-1" role="group" aria-label="Altitude zoom">
    {#each zoomButtons as [id, label]}
      <button
        type="button"
        class="rounded-sm border px-1.5 py-0.5 text-[10px] uppercase tracking-wider"
        class:border-[var(--accent)]={zoomMode === id}
        class:bg-[rgba(61,214,198,0.12)]={zoomMode === id}
        class:text-[var(--accent)]={zoomMode === id}
        class:border-[var(--line)]={zoomMode !== id}
        class:text-[var(--muted)]={zoomMode !== id}
        onclick={() => (zoomMode = id)}
      >
        {label}
      </button>
    {/each}
  </div>

  {#if !profile}
    <p class="text-xs text-[var(--muted)]">No altitude track for this mission.</p>
  {:else}
    <svg viewBox={`0 0 ${W} ${H}`} class="h-auto w-full" role="img" aria-label="Altitude versus time">
      {#each profile.phases as ph}
        <rect
          x={ph.x0}
          y={PAD.t}
          width={Math.max(0, ph.x1 - ph.x0)}
          height={H - PAD.t - PAD.b}
          fill={phaseFill(ph.kind)}
        />
      {/each}

      {#each profile.ticks as tick}
        <line
          x1={PAD.l}
          x2={W - PAD.r}
          y1={tick.y}
          y2={tick.y}
          stroke="var(--line)"
          stroke-width="0.75"
          stroke-dasharray="3 3"
        />
        <text x={PAD.l - 4} y={tick.y + 3} text-anchor="end" fill="var(--muted)" font-size="8" font-family="ui-monospace, monospace">
          {tick.alt}
        </text>
      {/each}

      <line
        x1={PAD.l}
        x2={W - PAD.r}
        y1={PAD.t + (H - PAD.t - PAD.b)}
        y2={PAD.t + (H - PAD.t - PAD.b)}
        stroke="rgba(255,255,255,0.25)"
        stroke-width="1"
      />

      <path d={profile.d} fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" />

      {#if profile.cursorX != null}
        <line
          x1={profile.cursorX}
          x2={profile.cursorX}
          y1={PAD.t}
          y2={H - PAD.b}
          stroke="var(--warn)"
          stroke-width="1.25"
          stroke-dasharray="2 2"
        />
        <circle cx={profile.cursorX} cy={profile.cursorY} r="4" fill="var(--warn)" stroke="var(--bg-deep)" stroke-width="1.5" />
      {/if}

      <text x={PAD.l} y={H - 6} fill="var(--muted)" font-size="8">
        {profile.phase === 'landing' ? 'final' : 'takeoff'}
      </text>
      <text x={W - PAD.r} y={H - 6} text-anchor="end" fill="var(--muted)" font-size="8">
        {profile.phase === 'takeoff' ? 'climb' : 'landing'}
      </text>
    </svg>

    {#if profile.phase !== 'full'}
      <svg viewBox={`0 0 ${W} 18`} class="mt-1 h-4 w-full" aria-hidden="true">
        <rect x={PAD.l} y="4" width={W - PAD.l - PAD.r} height="10" fill="rgba(255,255,255,0.06)" />
        <rect
          x={profile.winX0}
          y="4"
          width={Math.max(2, profile.winX1 - profile.winX0)}
          height="10"
          fill="rgba(61,214,198,0.35)"
          stroke="var(--accent)"
          stroke-width="0.75"
        />
      </svg>
    {/if}

    <div class="mt-1 flex flex-wrap gap-2 text-[10px] text-[var(--muted)]">
      <span class="inline-flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-sm" style="background:rgba(93,222,160,0.45)"></span> Climb</span>
      <span class="inline-flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-sm" style="background:rgba(77,163,255,0.35)"></span> Level</span>
      <span class="inline-flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-sm" style="background:rgba(255,122,69,0.45)"></span> Descent</span>
    </div>
  {/if}
</section>
