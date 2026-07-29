<script>
  /**
   * Minimal sensor-video display — no clip list, no transport chrome.
   * Driven by parent sync (scrub/play from main debrief).
   */
  import { formatTime, sensorColor } from './api.js'
  import { clipProgress } from './mediaUtil.js'

  let {
    clip = null,
    currentTime = null,
    playing = false,
    showClose = false,
    onclose = null,
  } = $props()

  let videoEl = $state(null)
  let lastSeek = 0

  let progress = $derived(clipProgress(clip, currentTime))

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
    <span class="uppercase tracking-wider text-white/50">Sensor feed</span>
    {#if clip}
      <span class="mono" style={`color:${sensorColor(clip.sensor)}`}>{clip.sensor}</span>
      <span class="truncate text-white/80">{clip.label}</span>
      <span class="mono ml-auto text-white/50">{formatTime(currentTime)}</span>
    {:else}
      <span class="text-white/40">No associated video at this time</span>
    {/if}
    {#if showClose}
      <button
        type="button"
        class="ml-2 text-white/50 hover:text-white"
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
      <div class="pointer-events-none absolute left-2 top-2 mono text-[10px] text-red-400">
        REC ●
      </div>
    {:else if clip}
      <div
        class="flex h-full flex-col items-center justify-center gap-1 p-4"
        style="background: radial-gradient(circle at 50% 45%, rgba(61,214,198,0.1), #05080c 70%)"
      >
        <div class="text-sm font-semibold" style={`color:${sensorColor(clip.sensor)}`}>
          {clip.sensor} · {clip.target_id || '—'}
        </div>
        <div class="mono text-xs text-white/60">{clip.label}</div>
      </div>
    {:else}
      <div class="flex h-full items-center justify-center p-6 text-center text-sm text-white/40">
        Scrub the debrief timeline to a collect or strike with associated video.
      </div>
    {/if}
  </div>
</section>
