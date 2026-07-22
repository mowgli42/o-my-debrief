<script>
  import { formatTime, markerGlyph } from './api.js'

  let { milestones = [], currentTime = null, onselect = undefined } = $props()

  function isActive(m) {
    if (!currentTime) return false
    return Math.abs(new Date(m.timestamp) - new Date(currentTime)) < 90_000
  }
</script>

<aside class="panel flex h-full min-h-0 flex-col rounded-sm">
  <header class="border-b border-[var(--line)] px-3 py-2">
    <h2 class="text-sm font-semibold tracking-[0.12em] uppercase text-[var(--accent)]">
      Key milestones
    </h2>
  </header>
  <div class="min-h-0 flex-1 overflow-y-auto p-2">
    {#each milestones as m (m.milestone_id)}
      <button
        type="button"
        class="mb-2 w-full rounded-sm border px-2 py-2 text-left transition-colors"
        class:border-[var(--accent)]={isActive(m)}
        class:bg-[var(--bg-elevated)]={isActive(m)}
        class:border-[var(--line)]={!isActive(m)}
        onclick={() => onselect?.(m)}
      >
        <div class="flex items-center gap-2 text-xs text-[var(--muted)]">
          <span class="text-[var(--collect)]">{markerGlyph(m.marker)}</span>
          <span class="mono">{formatTime(m.timestamp)}</span>
          <span
            class="ml-auto rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wider"
            class:bg-[rgba(93,222,160,0.15)]={m.status === 'completed' || m.status === 'VERIFIED' || m.status === 'EXECUTED' || m.status === 'success' || m.status === 'delivered'}
            class:text-[var(--verify)]={m.status === 'completed' || m.status === 'VERIFIED' || m.status === 'EXECUTED' || m.status === 'success' || m.status === 'delivered'}
            class:bg-[rgba(240,193,74,0.15)]={m.status === 'pending'}
            class:text-[var(--warn)]={m.status === 'pending'}
          >
            {m.status}
          </span>
        </div>
        <div class="mt-1 text-sm font-medium">{m.title}</div>
        <div class="mt-0.5 text-xs text-[var(--muted)] line-clamp-2">{m.outcome}</div>
        {#if m.linked_to_strike && m.link_note}
          <div class="mt-1 text-[11px] text-[var(--verify)]">↳ {m.link_note}</div>
        {/if}
      </button>
    {:else}
      <p class="p-3 text-sm text-[var(--muted)]">No milestones yet.</p>
    {/each}
  </div>
</aside>
