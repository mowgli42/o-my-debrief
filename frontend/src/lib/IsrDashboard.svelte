<script>
  import IsrSensorMap from './IsrSensorMap.svelte'
  import IsrMetricPanels from './IsrMetricPanels.svelte'
  import IsrEventInspector from './IsrEventInspector.svelte'

  let {
    isr = null,
    currentTime = null,
    selectedEventId = $bindable(null),
    perspective = $bindable('engineering'),
    onscrub = () => {},
  } = $props()

  let selectedEvent = $derived.by(() => {
    if (!isr?.events || !selectedEventId) return null
    return isr.events.find((e) => e.event_id === selectedEventId) || null
  })

  function onMapSelect(eventId, timestamp) {
    selectedEventId = eventId
    if (timestamp) onscrub(timestamp, eventId)
  }
</script>

<div class="flex h-full min-h-0 flex-col gap-2">
  <div class="flex flex-wrap items-center gap-2">
    <span class="text-[10px] tracking-[0.16em] uppercase text-[var(--muted)]">Perspective</span>
    <div class="flex rounded-sm border border-[var(--line)]">
      <button
        type="button"
        class="px-3 py-1 text-xs"
        class:bg-[rgba(61,214,198,0.15)]={perspective === 'engineering'}
        class:text-[var(--accent)]={perspective === 'engineering'}
        onclick={() => (perspective = 'engineering')}
      >
        Engineering
      </button>
      <button
        type="button"
        class="border-l border-[var(--line)] px-3 py-1 text-xs"
        class:bg-[rgba(61,214,198,0.15)]={perspective === 'operator'}
        class:text-[var(--accent)]={perspective === 'operator'}
        onclick={() => (perspective = 'operator')}
      >
        Operator
      </button>
    </div>
    <span class="text-[10px] text-[var(--muted)]">
      Shared map & scrub — switch modes without losing context
    </span>
  </div>

  <div class="grid min-h-0 flex-1 gap-2 lg:grid-cols-12">
    <div class="min-h-0 lg:col-span-8">
      <IsrSensorMap
        track={isr?.track || []}
        fovHistory={isr?.fov_history || []}
        collections={isr?.collections || []}
        detections={isr?.detections || []}
        opportunities={isr?.opportunities || []}
        faults={isr?.faults || []}
        {currentTime}
        {selectedEventId}
        {perspective}
        onselect={onMapSelect}
      />
    </div>
    <div class="flex min-h-0 flex-col gap-2 lg:col-span-4">
      <IsrMetricPanels
        {perspective}
        engineering={isr?.engineering || {}}
        operator={isr?.operator || {}}
      />
      <IsrEventInspector event={selectedEvent} />
    </div>
  </div>
</div>