import { toMs } from './api.js'

/** BroadcastChannel name for debrief ↔ video viewer sync. */
export const VIDEO_SYNC_CHANNEL = 'omy-debrief-video'

/**
 * Clip active at mission time (inclusive window).
 * @param {Array} media
 * @param {string|null} currentTime
 */
export function clipAtTime(media, currentTime) {
  if (!media?.length || !currentTime) return null
  const t = toMs(currentTime)
  return (
    media.find((c) => {
      const a = toMs(c.start_time)
      const b = toMs(c.end_time)
      return t >= a && t <= b
    }) || null
  )
}

/**
 * Resolve clip by id from catalog.
 * @param {Array} media
 * @param {string|null} clipId
 */
export function clipById(media, clipId) {
  if (!clipId || !media?.length) return null
  return media.find((c) => c.clip_id === clipId) || null
}

/**
 * Seek fraction 0–1 within a clip for a mission timestamp.
 */
export function clipProgress(clip, currentTime) {
  if (!clip || !currentTime) return 0
  const a = toMs(clip.start_time)
  const b = toMs(clip.end_time)
  const span = Math.max(1, b - a)
  return Math.min(1, Math.max(0, (toMs(currentTime) - a) / span))
}
