<script>
  import { formatTime, sensorColor, toMs } from './api.js'

  let {
    media = [],
    currentTime = null,
    playing = false,
    onselectClip = null,
  } = $props()

  let videoEl = $state(null)
  let pinnedClipId = $state(null)
  let lastSeek = 0

  let active = $derived.by(() => {
    if (!media?.length || !currentTime) return null
    const t = toMs(currentTime)
    if (pinnedClipId) {
      const pinned = media.find((c) => c.clip_id === pinnedClipId)
      if (pinned) {
        const a = toMs(pinned.start_time)
        const b = toMs(pinned.end_time)
        if (t >= a - 5_000 && t <= b + 5_000) return pinned
      }
    }
    return (
      media.find((c) => {
        const a = toMs(c.start_time)
        const b = toMs(c.end_time)
        return t >= a && t <= b
      }) || null
    )
  })

  let progress = $derived.by(() => {
    if (!active || !currentTime) return 0
    const a = toMs(active.start_time)
    const b = toMs(active.end_time)
    const span = Math.max(1, b - a)
    return Math.min(1, Math.max(0, (toMs(currentTime) - a) / span))
  })

  $effect(() => {
    const clip = active
    const el = videoEl
    if (!el || !clip?.url) return

    const wantSrc = clip.url
    const srcName = el.getAttribute('data-clip')
    if (srcName !== clip.clip_id) {
      el.setAttribute('data-clip', clip.clip_id)
      el.src = wantSrc
      el.load()
    }

    const duration = el.duration && Number.isFinite(el.duration) ? el.duration : clip.duration_s || 8
    const seekTo = progress * duration
    // Avoid thrashing seek during play
    if (Math.abs(seekTo - lastSeek) > 0.12 || !playing) {
      try {
        if (Math.abs((el.currentTime || 0) - seekTo) > 0.15) {
          el.currentTime = seekTo
        }
        lastSeek = seekTo
      } catch {
        /* ignore seek before metadata */
      }
    }

    if (playing) {
      el.play().catch(() => {})
    } else {
      el.pause()
    }
  })

  function pickClip(clip) {
    pinnedClipId = clip.clip_id
    onselectClip?.(clip)
  }
</script>

<section class="panel flex h-full min-h-0 flex-col overflow-hidden rounded-sm">
  <header class="flex shrink-0 items-center justify-between gap-2 border-b border-[var(--line)] px-3 py-2">
    <div>
      <h2 class="text-sm font-semibold tracking-[0.12em] uppercase text-[var(--accent)]">
        Sensor video
      </h2>
      <div class="mono text-xs text-[var(--muted)]">
        {#if active}
          {active.sensor} · {active.label} · {formatTime(active.start_time)}–{formatTime(active.end_time)}
        {:else}
          Timeline-synced FOV / collect feeds
        {/if}
      </div>
    </div>
    {#if active}
      <span
        class="rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wider"
        style={`color:${sensorColor(active.sensor)}; background:color-mix(in srgb, ${sensorColor(active.sensor)} 18%, transparent)`}
      >
        {active.sensor}
      </span>
    {/if}
  </header>

  <div class="relative min-h-0 flex-1 bg-black">
    {#if active?.url}
      <video
        bind:this={videoEl}
        class="h-full w-full object-contain"
        playsinline
        muted
        preload="auto"
      ></video>
      <div class="pointer-events-none absolute inset-x-0 top-0 flex justify-between p-2 text-[10px] mono text-white/80">
        <span>REC ● {formatTime(currentTime)}</span>
        <span>{Math.round(progress * 100)}%</span>
      </div>
      <div class="absolute inset-x-3 bottom-3 h-1 overflow-hidden rounded-sm bg-white/15">
        <div class="h-full bg-[var(--accent)]" style={`width:${progress * 100}%`}></div>
      </div>
    {:else if active}
      <!-- Catalog without rendered MP4: synthetic HUD frame -->
      <div
        class="flex h-full flex-col items-center justify-center gap-2 p-4"
        style={`background: radial-gradient(circle at 50% 45%, rgba(61,214,198,0.12), #05080c 70%)`}
      >
        <div class="text-xs uppercase tracking-wider text-[var(--muted)]">Synthetic HUD (no MP4)</div>
        <div class="text-lg font-semibold" style={`color:${sensorColor(active.sensor)}`}>
          {active.sensor} · {active.target_id}
        </div>
        <div class="mono text-sm text-[var(--text)]">{active.label}</div>
        <div class="mono text-xs text-[var(--muted)]">{formatTime(currentTime)}</div>
      </div>
    {:else}
      <div class="flex h-full flex-col items-center justify-center gap-2 p-4 text-center">
        <div class="text-sm text-[var(--muted)]">No sensor feed at this mission time.</div>
        <div class="text-xs text-[var(--muted)]">
          Scrub to a collect / strike window, or pick a clip below.
        </div>
      </div>
    {/if}
  </div>

  <div class="shrink-0 border-t border-[var(--line)] max-h-28 overflow-y-auto p-2">
    <div class="mb-1 text-[10px] uppercase tracking-wider text-[var(--muted)]">
      Clips ({media.length})
    </div>
    <ul class="space-y-1">
      {#each media as clip}
        <li>
          <button
            type="button"
            class="flex w-full items-center gap-2 rounded-sm border px-2 py-1 text-left text-xs transition-colors"
            class:border-[var(--accent)]={active?.clip_id === clip.clip_id}
            class:bg-[rgba(61,214,198,0.1)]={active?.clip_id === clip.clip_id}
            class:border-[var(--line)]={active?.clip_id !== clip.clip_id}
            onclick={() => pickClip(clip)}
          >
            <span class="mono" style={`color:${sensorColor(clip.sensor)}`}>{clip.sensor}</span>
            <span class="flex-1 truncate">{clip.label}</span>
            <span class="mono text-[10px] text-[var(--muted)]">{formatTime(clip.start_time)}</span>
          </button>
        </li>
      {/each}
    </ul>
  </div>
</section>
