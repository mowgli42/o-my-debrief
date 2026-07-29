<script>
  /**
   * Minimal sensor-video display — no clip list, no transport chrome.
   * Driven by parent sync (scrub/play from main debrief).
   * HUD overlays are toggleable; classification stays visible top-left.
   */
  import { onMount } from 'svelte'
  import { formatTime, sensorColor } from './api.js'
  import { clipProgress } from './mediaUtil.js'

  let {
    clip = null,
    currentTime = null,
    playing = false,
    classification = 'UNCLASSIFIED',
    showClose = false,
    onclose = null,
  } = $props()

  let videoEl = $state(null)
  let lastSeek = 0
  let overlaysOn = $state(true)

  const OVERLAY_KEY = 'omy-debrief-video-overlays'

  let progress = $derived(clipProgress(clip, currentTime))

  onMount(() => {
    try {
      const saved = localStorage.getItem(OVERLAY_KEY)
      if (saved === '0' || saved === '1') overlaysOn = saved === '1'
    } catch {
      /* ignore */
    }
  })

  function setOverlays(next) {
    overlaysOn = next
    try {
      localStorage.setItem(OVERLAY_KEY, next ? '1' : '0')
    } catch {
      /* ignore */
    }
  }

  $effect(() => {
    const el = videoEl
    if (!el || !clip?.url) return

    if (el.getAttribute('data-clip') !== clip.clip_id) {
      el.setAttribute('data-clip', clip.clip_id)
      el.src = clip.url
      el.load()
    }

    const duration = el.duration && Number.isFinite(el.duration) ? el.duration : clip.duration_s || 8
    const seekTo = progress * duration
    if (Math.abs(seekTo - lastSeek) > 0.12 || !playing) {
      try {
        if (Math.abs((el.currentTime || 0) - seekTo) > 0.15) {
          el.currentTime = seekTo
        }
        lastSeek = seekTo
      } catch {
        /* metadata not ready */
      }
    }

    if (playing) el.play().catch(() => {})
    else el.pause()
  })
</script>

<section class="flex h-full min-h-0 flex-col overflow-hidden bg-black text-[var(--text)]">
  <header class="flex shrink-0 items-center gap-2 border-b border-white/10 px-3 py-1.5 text-[11px]">
    <span
      class="rounded border border-green-700/80 bg-green-950/80 px-1.5 py-0.5 font-semibold uppercase tracking-wider text-green-400"
      title="Classification"
    >
      {classification}
    </span>
    <span class="uppercase tracking-wider text-white/40">Sensor feed</span>
    <label class="ml-auto flex cursor-pointer items-center gap-2 text-white/60 select-none">
      <span class="text-[10px] uppercase tracking-wider">Overlays</span>
      <button
        type="button"
        role="switch"
        aria-checked={overlaysOn}
        aria-label="Toggle video overlays"
        class="relative h-5 w-9 rounded-full border transition-colors"
        style={overlaysOn
          ? 'border-color: var(--accent); background: rgba(61,214,198,0.35)'
          : 'border-color: rgba(255,255,255,0.2); background: rgba(255,255,255,0.1)'}
        onclick={() => setOverlays(!overlaysOn)}
      >
        <span
          class="absolute top-0.5 h-3.5 w-3.5 rounded-full bg-white transition-transform"
          style={`left: ${overlaysOn ? '18px' : '2px'}`}
        ></span>
      </button>
    </label>
    {#if showClose}
      <button
        type="button"
        class="text-white/50 hover:text-white"
        onclick={() => onclose?.()}
        aria-label="Close video viewer"
      >
        ✕
      </button>
    {/if}
  </header>

  <div class="relative min-h-0 flex-1">
    {#if clip?.url}
      <video
        bind:this={videoEl}
        class="h-full w-full object-contain"
        playsinline
        muted
        preload="auto"
        controls={false}
      ></video>
    {:else if clip}
      <div
        class="h-full w-full"
        style="background: radial-gradient(circle at 50% 45%, rgba(61,214,198,0.08), #05080c 70%)"
      ></div>
    {:else}
      <div class="flex h-full items-center justify-center p-6 text-center text-sm text-white/40">
        Scrub the debrief timeline to a collect or strike with associated video.
      </div>
    {/if}

    <!-- Classification always visible on the picture (top-left) -->
    {#if clip}
      <div
        class="pointer-events-none absolute left-2 top-2 rounded border border-green-700/70 bg-black/55 px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wider text-green-400"
      >
        {classification}
      </div>
    {/if}

    {#if clip && overlaysOn}
      <!-- Reticle -->
      <div
        class="pointer-events-none absolute left-1/2 top-1/2 h-16 w-16 -translate-x-1/2 -translate-y-1/2 border border-white/35"
        aria-hidden="true"
      ></div>
      <div
        class="pointer-events-none absolute left-2 top-8 mono text-[11px] text-white"
        style={`text-shadow:0 0 4px #000`}
      >
        <div style={`color:${sensorColor(clip.sensor)}`}>{clip.sensor} · {clip.target_id || '—'}</div>
        <div class="text-[10px] text-[var(--accent)]">{clip.label}</div>
      </div>
      <div class="pointer-events-none absolute left-2 bottom-2 mono text-[10px] text-red-400">
        REC ● {formatTime(currentTime)}
      </div>
      <div class="pointer-events-none absolute right-2 bottom-2 mono text-[10px] text-white/60">
        HAWK-1 DEMO FEED
      </div>
      <div class="pointer-events-none absolute right-2 top-2 mono text-[10px] text-white/50">
        {formatTime(currentTime)}
      </div>
    {/if}
  </div>
</section>
