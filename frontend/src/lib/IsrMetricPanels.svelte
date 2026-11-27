<script>
  let { perspective = 'engineering', engineering = {}, operator = {} } = $props()

  function pct(v) {
    return v == null ? '—' : `${Number(v).toFixed(0)}%`
  }
  function num(v, digits = 2) {
    return v == null ? '—' : Number(v).toFixed(digits)
  }
</script>

{#if perspective === 'engineering'}
  <div class="panel space-y-2 rounded-sm p-3">
    <h3 class="text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
      Engineering · sensor performance
    </h3>
    <dl class="grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
      <div>
        <dt class="text-[var(--muted)]">Availability</dt>
        <dd class="mono text-[var(--text)]">{pct(engineering.uptime_pct)}</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Stabilization OK</dt>
        <dd class="mono text-[var(--text)]">{pct(engineering.stabilization_ok_pct)}</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Mean az error</dt>
        <dd class="mono text-[var(--text)]">{num(engineering.mean_az_error_deg)}°</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Mean quality</dt>
        <dd class="mono text-[var(--text)]">{num(engineering.mean_quality, 2)}</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Mean latency</dt>
        <dd class="mono text-[var(--text)]">{num(engineering.mean_latency_ms, 0)} ms</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Faults</dt>
        <dd class="mono text-[var(--text)]">
          {engineering.confirmed_faults ?? 0} confirmed / {engineering.fault_count ?? 0}
        </dd>
      </div>
    </dl>
    <p class="text-[10px] leading-snug text-[var(--muted)]">
      Correlate faults and quality dips with FOV/collection markers on the map. Confirmed faults
      vs potential concerns are tagged in the inspector.
    </p>
  </div>
{:else}
  <div class="panel space-y-2 rounded-sm p-3">
    <h3 class="text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
      Operator · utilization
    </h3>
    <dl class="grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
      <div>
        <dt class="text-[var(--muted)]">Observing share</dt>
        <dd class="mono text-[var(--text)]">{pct(operator.observe_pct)}</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Mission window</dt>
        <dd class="mono text-[var(--text)]">{num(operator.mission_duration_min, 1)} min</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Collections</dt>
        <dd class="mono text-[var(--text)]">{operator.collections ?? 0}</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Det → image</dt>
        <dd class="mono text-[var(--text)]">{pct(operator.detection_to_image_pct)}</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Unused opportunities</dt>
        <dd class="mono text-[var(--strike)]">{operator.opportunities_unused ?? 0}</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Revisit targets</dt>
        <dd class="mono text-[var(--text)]">{operator.revisits ?? 0}</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">Unplanned collects</dt>
        <dd class="mono text-[var(--text)]">{operator.unplanned_collects ?? 0}</dd>
      </div>
      <div>
        <dt class="text-[var(--muted)]">FOV samples</dt>
        <dd class="mono text-[var(--text)]">{operator.fov_samples ?? 0}</dd>
      </div>
    </dl>
    <p class="text-[10px] leading-snug text-[var(--muted)]">
      Unused opportunities are observable areas not imaged — not automatic deficiencies. Use them
      to judge employment choices against tasking.
    </p>
  </div>
{/if}