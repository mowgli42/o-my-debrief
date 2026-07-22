<script>
  import { formatTime } from './api.js'
  import FlightInstruments from './FlightInstruments.svelte'
  import AltitudeProfile from './AltitudeProfile.svelte'

  let { platform = null, track = [], currentTime = null } = $props()

  /** @type {'mission' | 'launch'} */
  let tab = $state('mission')
  let userPickedTab = $state(false)

  let fuel = $derived(platform?.fuel_percent ?? 0)
  let fuelColor = $derived(
    fuel > 60 ? 'var(--verify)' : fuel > 35 ? 'var(--warn)' : 'var(--danger)',
  )
  let gearDown = $derived((platform?.gear || '').toLowerCase() === 'down')

  // Soft nudge: when gear is down and user hasn't chosen a tab, open Launch/Recovery
  $effect(() => {
    if (userPickedTab || !platform) return
    if (gearDown) tab = 'launch'
    else tab = 'mission'
  })

  function selectTab(next) {
    userPickedTab = true
    tab = next
  }

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

    <div class="mt-2 flex gap-1" role="tablist" aria-label="Platform panel views">
      <button
        type="button"
        role="tab"
        aria-selected={tab === 'mission'}
        class="flex-1 rounded-sm border px-2 py-1 text-[11px] uppercase tracking-wider transition-colors"
        class:border-[var(--accent)]={tab === 'mission'}
        class:bg-[rgba(61,214,198,0.12)]={tab === 'mission'}
        class:text-[var(--accent)]={tab === 'mission'}
        class:border-[var(--line)]={tab !== 'mission'}
        class:text-[var(--muted)]={tab !== 'mission'}
        onclick={() => selectTab('mission')}
      >
        Mission
      </button>
      <button
        type="button"
        role="tab"
        aria-selected={tab === 'launch'}
        class="relative flex-1 rounded-sm border px-2 py-1 text-[11px] uppercase tracking-wider transition-colors"
        class:border-[var(--accent)]={tab === 'launch'}
        class:bg-[rgba(61,214,198,0.12)]={tab === 'launch'}
        class:text-[var(--accent)]={tab === 'launch'}
        class:border-[var(--line)]={tab !== 'launch'}
        class:text-[var(--muted)]={tab !== 'launch'}
        onclick={() => selectTab('launch')}
      >
        Launch / Recovery
        {#if gearDown && tab !== 'launch'}
          <span
            class="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-[var(--warn)]"
            title="Gear down"
            aria-hidden="true"
          ></span>
        {/if}
      </button>
    </div>
  </header>

  <div class="min-h-0 flex-1 space-y-3 overflow-y-auto p-3">
    {#if !platform}
      <p class="text-sm text-[var(--muted)]">Select a mission to load status.</p>
    {:else if tab === 'mission'}
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
    {:else}
      <!-- Launch / Recovery: instruments, profile, gear & systems -->
      <AltitudeProfile
        {track}
        {currentTime}
        altitude={platform.alt_ft}
        gear={platform.gear}
      />

      <section class="grid grid-cols-2 gap-2">
        <div class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2 text-center">
          <div class="mb-1 flex items-center justify-center gap-1 text-[10px] uppercase tracking-wider text-[var(--muted)]">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M6 10h12v2H6z" fill="var(--muted)" />
              <circle cx="8" cy="16" r="2.5" stroke={gearDown ? 'var(--warn)' : 'var(--verify)'} stroke-width="1.5" fill="none" />
              <circle cx="16" cy="16" r="2.5" stroke={gearDown ? 'var(--warn)' : 'var(--verify)'} stroke-width="1.5" fill="none" />
              <path d="M8 12v2M16 12v2" stroke={gearDown ? 'var(--warn)' : 'var(--verify)'} stroke-width="1.5" />
            </svg>
            Gear
          </div>
          <div
            class="mt-1 text-lg font-semibold uppercase"
            class:text-[var(--warn)]={gearDown}
            class:text-[var(--verify)]={!gearDown}
          >
            {platform.gear}
          </div>
        </div>
        <div class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2 text-center">
          <div class="mb-1 flex items-center justify-center gap-1 text-[10px] uppercase tracking-wider text-[var(--muted)]">
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
        <div class="mb-2 text-[10px] uppercase tracking-wider text-[var(--muted)]">Aircraft systems</div>
        <ul class="space-y-1.5 text-sm">
          <li class="flex items-center justify-between gap-2">
            <span class="text-[var(--muted)]">Fuel</span>
            <span class="mono font-semibold" style={`color:${fuelColor}`}>{fuel.toFixed(1)}%</span>
          </li>
          <li class="flex items-center justify-between gap-2">
            <span class="text-[var(--muted)]">Datalink</span>
            <span
              class="font-semibold"
              class:text-[var(--verify)]={platform.datalink_up}
              class:text-[var(--danger)]={!platform.datalink_up}
            >
              {platform.datalink_up ? `UP · ${platform.datalink_mbps ?? '—'} Mbps` : 'DOWN'}
            </span>
          </li>
          <li class="flex items-center justify-between gap-2">
            <span class="text-[var(--muted)]">Readiness</span>
            <span class="font-semibold text-[var(--verify)]">{platform.readiness}</span>
          </li>
          <li class="flex items-center justify-between gap-2">
            <span class="text-[var(--muted)]">Payload</span>
            <span class="text-right text-xs">
              {(platform.payload_active || []).join(', ') || '—'}
              {#if platform.payload_mode}
                <span class="text-[var(--muted)]"> · {platform.payload_mode}</span>
              {/if}
            </span>
          </li>
        </ul>
      </section>

      <FlightInstruments
        airspeed={platform.speed_kts ?? 0}
        altitude={platform.alt_ft ?? 0}
        heading={platform.heading_deg ?? 0}
        roll={platform.roll_deg ?? 0}
        pitch={platform.pitch_deg ?? 0}
      />

      <section class="text-xs text-[var(--muted)] mono">
        {#if platform.lat != null}
          {platform.lat.toFixed(4)}, {platform.lon.toFixed(4)} · WP {platform.current_waypoint || '—'}
        {/if}
      </section>
    {/if}
  </div>
</aside>
