<script>
  import SensorFovPlot from './SensorFovPlot.svelte'
  import WeaponsLarPlot from './WeaponsLarPlot.svelte'
  import SensorStatePanels from './SensorStatePanels.svelte'

  let {
    collectPoints = [],
    collectMetrics = {},
    releases = [],
    larSummary = {},
    telemetry = [],
    currentTime = null,
  } = $props()
</script>

<div class="flex h-full min-h-0 flex-col gap-3 overflow-auto">
  <div class="grid gap-3 lg:grid-cols-2">
    <SensorFovPlot points={collectPoints} />
    <WeaponsLarPlot {releases} {larSummary} />
  </div>
  {#if collectMetrics && Object.keys(collectMetrics).length}
    <div class="panel rounded-sm px-3 py-2 text-xs text-[var(--muted)]">
      Collects {collectMetrics.collected}/{collectMetrics.attempted} · success
      {(Number(collectMetrics.success_rate || 0) * 100).toFixed(0)}% · tasked
      {collectMetrics.tasked_planned} · unplanned {collectMetrics.unplanned}
    </div>
  {/if}
  <SensorStatePanels samples={telemetry} {currentTime} />
</div>