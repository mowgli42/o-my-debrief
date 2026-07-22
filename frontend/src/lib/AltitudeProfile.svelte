<script>
  /**
   * Simple altitude-vs-time profile for launch / recovery.
   * Shows climb-out / cruise / descent with a scrub cursor.
   */
  let { track = [], currentTime = null, altitude = null, gear = null } = $props()

  const W = 320
  const H = 120
  const PAD = { l: 36, r: 10, t: 12, b: 22 }

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
    const alts = pts.map((p) => p.alt)
    const amin = Math.min(0, ...alts)
    const amax = Math.max(...alts, amin + 500)
    const arange = Math.max(1, amax - amin)

    const innerW = W - PAD.l - PAD.r
    const innerH = H - PAD.t - PAD.b

    const xy = pts.map((p) => ({
      x: PAD.l + ((p.t - t0) / span) * innerW,
      y: PAD.t + (1 - (p.alt - amin) / arange) * innerH,
      t: p.t,
      alt: p.alt,
    }))

    const d = xy.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')

    let cursorX = null
    let cursorY = null
    let cursorAlt = altitude
    if (currentTime) {
      const ct = new Date(currentTime).getTime()
      if (Number.isFinite(ct)) {
        const frac = Math.min(1, Math.max(0, (ct - t0) / span))
        cursorX = PAD.l + frac * innerW
        if (cursorAlt == null || !Number.isFinite(Number(cursorAlt))) {
          // interpolate alt at cursor
          for (let i = 0; i < pts.length - 1; i++) {
            if (ct >= pts[i].t && ct <= pts[i + 1].t) {
              const f = (ct - pts[i].t) / Math.max(1, pts[i + 1].t - pts[i].t)
              cursorAlt = pts[i].alt + (pts[i + 1].alt - pts[i].alt) * f
              break
            }
          }
          if (cursorAlt == null) cursorAlt = pts[pts.length - 1].alt
        }
        cursorY = PAD.t + (1 - (Number(cursorAlt) - amin) / arange) * innerH
      }
    }

    // Phase bands from slope: climb / level / descent
    const phases = []
    for (let i = 0; i < pts.length - 1; i++) {
      const da = pts[i + 1].alt - pts[i].alt
      const kind = da > 800 ? 'climb' : da < -800 ? 'descent' : 'level'
      phases.push({
        x0: xy[i].x,
        x1: xy[i + 1].x,
        kind,
      })
    }

    const ticks = [amin, amin + arange / 2, amax].map((a) => ({
      alt: Math.round(a),
      y: PAD.t + (1 - (a - amin) / arange) * innerH,
    }))

    return { d, xy, cursorX, cursorY, cursorAlt, phases, ticks, amin, amax }
  })

  function phaseFill(kind) {
    if (kind === 'climb') return 'rgba(93,222,160,0.12)'
    if (kind === 'descent') return 'rgba(255,122,69,0.12)'
    return 'rgba(77,163,255,0.06)'
  }
</script>

<section class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2">
  <div class="mb-1 flex items-center justify-between text-[10px] uppercase tracking-wider text-[var(--muted)]">
    <span>Altitude profile</span>
    <span class="mono normal-case tracking-normal">
      {profile?.cursorAlt != null ? `${Math.round(profile.cursorAlt).toLocaleString()} ft` : '—'}
      {#if gear}
        · gear {gear}
      {/if}
    </span>
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

      <!-- runway / ground baseline -->
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

      <text x={PAD.l} y={H - 6} fill="var(--muted)" font-size="8">takeoff</text>
      <text x={W - PAD.r} y={H - 6} text-anchor="end" fill="var(--muted)" font-size="8">landing</text>
    </svg>
    <div class="mt-1 flex flex-wrap gap-2 text-[10px] text-[var(--muted)]">
      <span class="inline-flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-sm" style="background:rgba(93,222,160,0.45)"></span> Climb</span>
      <span class="inline-flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-sm" style="background:rgba(77,163,255,0.35)"></span> Level</span>
      <span class="inline-flex items-center gap-1"><span class="inline-block h-2 w-2 rounded-sm" style="background:rgba(255,122,69,0.45)"></span> Descent</span>
    </div>
  {/if}
</section>
