<script>
  import * as d3 from 'd3'

  /** @type {{ samples?: object[], currentTime?: string | null }} */
  let { samples = [], currentTime = null } = $props()

  let rootEl = $state(null)
  let width = $state(520)
  const panelH = 72
  const margin = { left: 44, right: 12, top: 8, bottom: 22 }

  const continuous = [
    { key: 'fuel_percent', label: 'Fuel %', color: '#eab308' },
    { key: 'datalink_mbps', label: 'Datalink Mbps', color: '#4da3ff' },
    { key: 'temperature_c', label: 'Sensor °C', color: '#ff5c6c' },
    { key: 'signal_strength', label: 'Signal', color: '#5cd67e' },
  ]

  function parseRows() {
    return (samples || []).map((d) => ({
      ...d,
      _t: d3.isoParse(d.timestamp) || new Date(d.timestamp),
    }))
  }

  function render() {
    if (!rootEl) return
    const parsed = parseRows()
    d3.select(rootEl).selectAll('svg').remove()
    if (!parsed.length) return

    const innerW = width - margin.left - margin.right
    const x = d3
      .scaleTime()
      .domain(d3.extent(parsed, (d) => d._t))
      .range([0, innerW])

    const totalH = continuous.length * (panelH + 6) + 28
    const svg = d3.select(rootEl).append('svg').attr('width', width).attr('height', totalH)

    continuous.forEach((series, i) => {
      const vals = parsed.filter((d) => d[series.key] != null)
      if (!vals.length) return
      const y0 = i * (panelH + 6) + margin.top
      const g = svg
        .append('g')
        .attr('transform', `translate(${margin.left},${y0})`)
      const y = d3
        .scaleLinear()
        .domain(d3.extent(vals, (d) => Number(d[series.key])))
        .nice()
        .range([panelH - 8, 4])
      const line = d3
        .line()
        .x((d) => x(d._t))
        .y((d) => y(Number(d[series.key])))
        .curve(d3.curveMonotoneX)
      g.append('path')
        .datum(vals)
        .attr('fill', 'none')
        .attr('stroke', series.color)
        .attr('stroke-width', 1.5)
        .attr('d', line)
      g.append('text')
        .attr('x', -6)
        .attr('y', panelH / 2)
        .attr('text-anchor', 'end')
        .attr('fill', '#8b9cb0')
        .attr('font-size', 9)
        .text(series.label)
    })

    if (currentTime) {
      const ct = d3.isoParse(currentTime)
      if (ct) {
        const xPos = margin.left + x(ct)
        svg
          .append('line')
          .attr('x1', xPos)
          .attr('x2', xPos)
          .attr('y1', 0)
          .attr('y2', totalH - 20)
          .attr('stroke', 'var(--accent)')
          .attr('stroke-width', 1)
          .attr('opacity', 0.8)
      }
    }
  }

  $effect(() => {
    void samples
    void currentTime
    void width
    render()
  })

  $effect(() => {
    if (!rootEl) return
    const ro = new ResizeObserver(() => {
      width = Math.max(360, rootEl.clientWidth - 4)
      render()
    })
    ro.observe(rootEl)
    return () => ro.disconnect()
  })
</script>

<div class="panel flex min-h-0 flex-1 flex-col rounded-sm p-3 overflow-auto">
  <h3 class="mb-2 text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
    Sensor &amp; platform telemetry
  </h3>
  {#if !samples?.length}
    <p class="text-sm text-[var(--muted)]">No sensor telemetry rows for this mission.</p>
  {:else}
    <div bind:this={rootEl}></div>
  {/if}
</div>