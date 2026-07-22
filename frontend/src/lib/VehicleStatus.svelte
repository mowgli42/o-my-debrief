<script>
  import { formatTime } from './api.js'

  let { platform = null } = $props()

  let fuel = $derived(platform?.fuel_percent ?? 0)
  let fuelColor = $derived(
    fuel > 60 ? 'var(--verify)' : fuel > 35 ? 'var(--warn)' : 'var(--danger)',
  )
</script>

<aside class="panel flex h-full min-h-0 flex-col rounded-sm">
  <header class="border-b border-[var(--line)] px-3 py-2">
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
        <div class="text-[10px] uppercase tracking-wider text-[var(--muted)]">Weapons</div>
        <ul class="mt-1 space-y-1 text-sm">
          {#each Object.entries(platform.weapons || {}) as [name, qty]}
            <li class="flex justify-between mono">
              <span>{name}</span>
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
          <div class="text-[10px] uppercase tracking-wider text-[var(--muted)]">Gear</div>
          <div class="mt-1 text-lg font-semibold uppercase">{platform.gear}</div>
        </div>
        <div class="rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2 text-center">
          <div class="text-[10px] uppercase tracking-wider text-[var(--muted)]">Weapons bay</div>
          <div
            class="mt-1 text-lg font-semibold uppercase"
            class:text-[var(--strike)]={platform.weapons_bay === 'open'}
            class:text-[var(--verify)]={platform.weapons_bay !== 'open'}
          >
            {platform.weapons_bay}
          </div>
        </div>
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
