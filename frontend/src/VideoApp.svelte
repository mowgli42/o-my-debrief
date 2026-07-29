<script>
  /**
   * Standalone pop-out video window. Syncs mission time from the main debrief
   * via BroadcastChannel — no local transport controls.
   */
  import { onMount } from 'svelte'
  import VideoViewer from './lib/VideoViewer.svelte'
  import { fetchMedia } from './lib/api.js'
  import { VIDEO_SYNC_CHANNEL, clipAtTime, clipById } from './lib/mediaUtil.js'

  let missionId = $state('')
  let media = $state([])
  let currentTime = $state(null)
  let playing = $state(false)
  let preferClipId = $state(null)
  let error = $state('')

  let clip = $derived(
    clipById(media, preferClipId) || clipAtTime(media, currentTime),
  )
  let classification = $derived(clip?.classification || media[0]?.classification || 'UNCLASSIFIED')

  onMount(async () => {
    const params = new URLSearchParams(window.location.search)
    missionId = params.get('mission') || ''
    if (!missionId) {
      error = 'Missing ?mission= — open from Platform Debrief.'
      return
    }
    try {
      media = await fetchMedia(missionId)
    } catch (e) {
      error = String(e.message || e)
    }

    const ch = new BroadcastChannel(VIDEO_SYNC_CHANNEL)
    ch.onmessage = (ev) => {
      const msg = ev.data || {}
      if (msg.type !== 'sync') return
      if (msg.missionId && msg.missionId !== missionId) return
      if (msg.currentTime != null) currentTime = msg.currentTime
      if (typeof msg.playing === 'boolean') playing = msg.playing
      if (msg.clipId !== undefined) preferClipId = msg.clipId
    }
    // Request initial state from opener
    ch.postMessage({ type: 'hello', missionId })
    return () => ch.close()
  })
</script>

<div class="h-screen w-screen bg-black">
  {#if error}
    <div class="p-4 text-sm text-red-400">{error}</div>
  {:else}
    <VideoViewer {clip} {currentTime} {playing} {classification} />
  {/if}
</div>
