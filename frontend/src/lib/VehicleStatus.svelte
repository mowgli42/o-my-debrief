<script>
  import { formatTime } from './api.js'

  let { platform = null } = $props()

  let fuel = $derived(platform?.fuel_percent ?? 0)
  let fuelColor = $derived(
    fuel > 60 ? 'var(--verify)' : fuel > 35 ? 'var(--warn)' : 'var(--danger)',
  )

  function taskStatusColor(status) {
    const s = (status || '').toUpperCase()
    if (s === 'EXECUTED' || s === 'COMPLETED' || s === 'VERIFIED') return 'var(--verify)'
    if (s === 'ASSIGNED' || s === 'PENDING' || s === 'IN_PROGRESS') return 'var(--warn)'
    if (s === 'FAILED' || s === 'ABORTED') return 'var(--danger)'
    return 'var(--muted)'
  }
</script>

<aside class="panel flex h-full min-h-0 flex-col rounded-sm overflow-hidden">
  <header class="shrink-0 border-b border-[var(--line)] px-3 py-2">
    <h2 class="text-sm font-semibold tracking-[0.12em] uppercase text-[var(--accent)]">
      Platform status
    </h2>
    <div class="mono text-xs text-[var(--muted)]">
      {platform?.callsign || '—'} · {formatTime(platform?.timestamp)}
    </div>
  </header>

  <div class="min-h-0 flex-1 space-y-3 overflow-y-auto p-3">
    {#if !platform}
      <p class="text-sm text-[var(--muted)]">Select a mission to load status.</p>
    {:else}
      <section class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2">
        <div class="text-[10px] uppercase tracking-wider text-[var(--muted)]">Current waypoint</div>
        <div class="mt-1 flex items-center gap-2">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 2L4 20h5l3-7 3 7h5L12 2z" fill="var(--accent)" opacity="0.9" />
          </svg>
          <div>
            <div class="text-sm font-semibold">{platform.current_waypoint || '—'}</div>
            {#if platform.current_waypoint_index != null}
              <div class="mono text-[10px] text-[var(--muted)]">
                WP{platform.current_waypoint_index + 1}
              </div>
            {/if}
          </div>
        </div>
      </section>

      <section>
        <div class="mb-1 flex justify-between text-xs uppercase tracking-wider text-[var(--muted)]">
          <span>Fuel</span>
          <span class="mono" style={`color:${fuelColor}`}>{fuel.toFixed(1)}%</span>
        </div>
        <div class="h-2 overflow-hidden rounded-sm bg-[var(--bg-deep)]">
          <div class="h-full transition-all duration-300" style={`width:${fuel}%; background:${fuelColor}`}></div>
        </div>
      </section>

      <section class="grid grid-cols-2 gap-2">
        <div class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2">
          <div class="text-[10px] uppercase tracking-wider text-[var(--muted)]">Datalink</div>
          <div
            class="mt-1 text-sm font-semibold"
            class:text-[var(--verify)]={platform.datalink_up}
            class:text-[var(--danger)]={!platform.datalink_up}
          >
            {platform.datalink_up ? `LINK UP · ${platform.datalink_mbps ?? '—'} Mbps` : 'LINK DOWN'}
          </div>
        </div>
        <div class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2">
          <div class="text-[10px] uppercase tracking-wider text-[var(--muted)]">Readiness</div>
          <div class="mt-1 text-sm font-semibold text-[var(--verify)]">{platform.readiness}</div>
        </div>
      </section>

      <section class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2">
        <div class="text-[10px] uppercase tracking-wider text-[var(--muted)]">Payload</div>
        <div class="mt-1 flex flex-wrap gap-1">
          {#each platform.payload_active || [] as p}
            <span class="rounded px-1.5 py-0.5 text-xs" style="background:rgba(77,163,255,.15);color:var(--collect)">{p}</span>
          {:else}
            <span class="text-xs text-[var(--muted)]">None</span>
          {/each}
        </div>
        <div class="mt-1 text-xs text-[var(--muted)]">Mode: {platform.payload_mode || '—'}</div>
      </section>

      <section class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2">
        <div class="mb-1 flex items-center gap-2 text-[10px] uppercase tracking-wider text-[var(--muted)]">
          <!-- missile / weapons icon -->
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M4 12h12l4-2v4l-4-2H4z" stroke="var(--strike)" stroke-width="1.6" fill="rgba(255,122,69,0.2)" />
            <path d="M3 10v4" stroke="var(--strike)" stroke-width="1.6" />
            <circle cx="19" cy="12" r="1.5" fill="var(--strike)" />
          </svg>
          <span>Weapons</span>
        </div>
        <ul class="mt-1 space-y-1 text-sm">
          {#each Object.entries(platform.weapons || {}) as [name, qty]}
            <li class="flex items-center justify-between mono gap-2">
              <span class="flex items-center gap-1.5">
                <svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M3 12h14l4-3v6l-4-3H3z" fill="var(--strike)" opacity="0.85" />
                </svg>
                {name}
              </span>
              <span>{qty}</span>
            </li>
          {:else}
            <li class="text-xs text-[var(--muted)]">No loadout data</li>
          {/each}
        </ul>
        {#if platform.weapons_expended?.length}
          <div class="mt-2 border-t border-[var(--line)] pt-2 text-xs text-[var(--strike)]">
            Expended:
            {#each platform.weapons_expended as x}
              <div class="mono">{x.munition} @ {formatTime(x.timestamp)} → {x.target_id}</div>
            {/each}
          </div>
        {/if}
      </section>

      <section class="grid grid-cols-2 gap-2">
        <div class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2 text-center">
          <div class="mb-1 flex items-center justify-center gap-1 text-[10px] uppercase tracking-wider text-[var(--muted)]">
            <!-- landing gear icon -->
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M6 10h12v2H6z" fill="var(--muted)" />
              <circle cx="8" cy="16" r="2.5" stroke={platform.gear === 'down' ? 'var(--warn)' : 'var(--verify)'} stroke-width="1.5" fill="none" />
              <circle cx="16" cy="16" r="2.5" stroke={platform.gear === 'down' ? 'var(--warn)' : 'var(--verify)'} stroke-width="1.5" fill="none" />
              <path d="M8 12v2M16 12v2" stroke={platform.gear === 'down' ? 'var(--warn)' : 'var(--verify)'} stroke-width="1.5" />
            </svg>
            Gear
          </div>
          <div
            class="mt-1 text-lg font-semibold uppercase"
            class:text-[var(--warn)]={platform.gear === 'down'}
            class:text-[var(--verify)]={platform.gear !== 'down'}
          >
            {platform.gear}
          </div>
        </div>
        <div class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2 text-center">
          <div class="mb-1 flex items-center justify-center gap-1 text-[10px] uppercase tracking-wider text-[var(--muted)]">
            <!-- weapons bay doors icon -->
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              {#if platform.weapons_bay === 'open'}
                <path d="M4 8l4 4-4 4" stroke="var(--strike)" stroke-width="1.6" />
                <path d="M20 8l-4 4 4 4" stroke="var(--strike)" stroke-width="1.6" />
                <rect x="9" y="7" width="6" height="10" rx="1" stroke="var(--strike)" stroke-width="1.4" fill="rgba(255,122,69,0.15)" />
              {:else}
                <rect x="5" y="7" width="14" height="10" rx="1" stroke="var(--verify)" stroke-width="1.5" fill="rgba(93,222,160,0.12)" />
                <path d="M12 7v10" stroke="var(--verify)" stroke-width="1.4" />
              {/if}
            </svg>
            Bay
          </div>
          <div
            class="mt-1 text-lg font-semibold uppercase"
            class:text-[var(--strike)]={platform.weapons_bay === 'open'}
            class:text-[var(--verify)]={platform.weapons_bay !== 'open'}
          >
            {platform.weapons_bay}
          </div>
        </div>
      </section>

      <section class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2">
        <div class="text-[10px] uppercase tracking-wider text-[var(--muted)]">
          Assigned tasks ({platform.tasks?.length || 0})
        </div>
        {#if platform.tasks?.length}
          <ul class="mt-2 space-y-2">
            {#each platform.tasks as t}
              <li class="rounded-sm border border-[var(--line)] bg-[var(--bg-panel)] px-2 py-1.5">
                <div class="flex items-center justify-between gap-2">
                  <span class="mono text-xs font-semibold">{t.task_id}</span>
                  <span
                    class="rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wider"
                    style={`color:${taskStatusColor(t.status)}; background:color-mix(in srgb, ${taskStatusColor(t.status)} 18%, transparent)`}
                  >
                    {t.status}
                  </span>
                </div>
                <div class="mt-0.5 text-xs text-[var(--muted)] line-clamp-2">
                  {t.summary || t.target_id || '—'}
                </div>
                <div class="mono mt-0.5 text-[10px] text-[var(--muted)]">
                  {formatTime(t.timestamp)}
                  {#if t.target_id} · {t.target_id}{/if}
                </div>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="mt-1 text-xs text-[var(--muted)]">No tasks assigned yet at this time.</p>
        {/if}
      </section>

      <section class="text-xs text-[var(--muted)] mono">
        {#if platform.lat != null}
          {platform.lat.toFixed(4)}, {platform.lon.toFixed(4)} · {platform.alt_ft ?? '—'} ft ·
          {platform.heading_deg ?? '—'}° · {platform.speed_kts ?? '—'} kts
        {/if}
      </section>
    {/if}
  </div>
</aside>
