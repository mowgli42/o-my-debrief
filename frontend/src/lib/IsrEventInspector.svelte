<script>
  import { formatTime } from './api.js'

  let { event = null } = $props()

  function kindLabel(k) {
    return (
      {
        collection: 'Image collection',
        detection: 'Detection',
        opportunity: 'Unused opportunity',
        fault: 'Fault / anomaly',
        fov: 'FOV sample',
      }[k] || k || 'Event'
    )
  }
</script>

<div class="panel flex min-h-0 flex-1 flex-col rounded-sm p-3">
  <h3 class="mb-2 text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
    Correlated event
  </h3>
  {#if !event}
    <p class="text-sm text-[var(--muted)]">
      Select a FOV, detection, collection, opportunity, or fault on the map.
    </p>
  {:else}
    <div class="space-y-2 overflow-auto text-xs">
      <div class="text-[10px] uppercase tracking-wide text-[var(--muted)]">
        {kindLabel(event.isr_kind)}
      </div>
      <div class="mono text-sm text-[var(--text)]">{formatTime(event.timestamp)}</div>
      <p class="text-[var(--text)]">{event.summary || `${event.sensor || ''} ${event.target_id || ''}`}</p>
      <dl class="grid grid-cols-2 gap-2">
        <div>
          <dt class="text-[var(--muted)]">Sensor</dt>
          <dd class="mono">{event.sensor || '—'}</dd>
        </div>
        <div>
          <dt class="text-[var(--muted)]">Status</dt>
          <dd class="mono">{event.status || event.outcome || '—'}</dd>
        </div>
        {#if event.lat != null}
          <div class="col-span-2">
            <dt class="text-[var(--muted)]">Position</dt>
            <dd class="mono">{Number(event.lat).toFixed(4)}, {Number(event.lon).toFixed(4)}</dd>
          </div>
        {/if}
        {#if event.pointing}
          <div class="col-span-2">
            <dt class="text-[var(--muted)]">Pointing cmd → act</dt>
            <dd class="mono">
              az {event.pointing.cmd_az_deg}→{event.pointing.act_az_deg} (err
              {event.pointing.az_error_deg}°)
            </dd>
          </div>
        {/if}
        {#if event.quality_score != null}
          <div>
            <dt class="text-[var(--muted)]">Quality</dt>
            <dd class="mono">{event.quality_score}</dd>
          </div>
        {/if}
        {#if event.sharpness != null}
          <div>
            <dt class="text-[var(--muted)]">Sharpness</dt>
            <dd class="mono">{event.sharpness}</dd>
          </div>
        {/if}
        {#if event.latency_ms != null}
          <div>
            <dt class="text-[var(--muted)]">Latency</dt>
            <dd class="mono">{event.latency_ms} ms</dd>
          </div>
        {/if}
        {#if event.health}
          <div>
            <dt class="text-[var(--muted)]">Health</dt>
            <dd class="mono">{event.health}</dd>
          </div>
        {/if}
        {#if event.isr_kind === 'fault'}
          <div>
            <dt class="text-[var(--muted)]">Subsystem</dt>
            <dd class="mono">{event.subsystem || '—'}</dd>
          </div>
          <div>
            <dt class="text-[var(--muted)]">Classification</dt>
            <dd class="mono {event.confirmed ? 'text-[var(--danger)]' : 'text-[var(--strike)]'}">
              {event.confirmed ? 'Confirmed issue' : 'Potential concern'}
            </dd>
          </div>
        {/if}
        {#if event.isr_kind === 'detection'}
          <div>
            <dt class="text-[var(--muted)]">Imaged</dt>
            <dd class="mono">{event.imaged ? 'yes' : 'no'}</dd>
          </div>
          <div>
            <dt class="text-[var(--muted)]">SNR</dt>
            <dd class="mono">{event.snr ?? '—'}</dd>
          </div>
        {/if}
        {#if event.isr_kind === 'opportunity'}
          <div class="col-span-2">
            <dt class="text-[var(--muted)]">Reason</dt>
            <dd class="mono">{event.reason || 'not_selected'}</dd>
          </div>
        {/if}
      </dl>
    </div>
  {/if}
</div>