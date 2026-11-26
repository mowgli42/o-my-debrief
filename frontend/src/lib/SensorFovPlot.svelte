<script>
  import * as d3 from 'd3'
  import { sensorColor } from './api.js'

  /** @type {{ points?: object[] }} */
  let { points = [] } = $props()

  let rootEl = $state(null)
  let width = $state(520)
  const height = 220
  const margin = { top: 16, right: 16, bottom: 36, left: 48 }

  function render() {
    if (!rootEl || !points?.length) return
    const innerW = width - margin.left - margin.right
    const innerH = height - margin.top - margin.bottom
    d3.select(rootEl).selectAll('svg').remove()
    const svg = d3
      .select(rootEl)
      .append('svg')
      .attr('width', width)
      .attr('height', height)

    const xKey = (d) => d.slant_range_nm ?? d.ground_range_nm ?? 0
    const yKey = (d) =>
      d.footprint_diameter_m ?? (d.footprint_area_km2 ?? 0) * 1000 ?? (d.cone_angle_deg ?? 0) * 40

    const x = d3.scaleLinear().domain(d3.extent(points, xKey)).nice().range([0, innerW])
    const y = d3.scaleLinear().domain(d3.extent(points, yKey)).nice().range([innerH, 0])

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    g.append('g')
      .attr('transform', `translate(0,${innerH})`)
      .call(d3.axisBottom(x).ticks(6))
      .selectAll('text')
      .attr('fill', '#8b9cb0')

    g.append('g')
      .call(d3.axisLeft(y).ticks(5))
      .selectAll('text')
      .attr('fill', '#8b9cb0')

    g.selectAll('circle')
      .data(points)
      .join('circle')
      .attr('cx', (d) => x(xKey(d)))
      .attr('cy', (d) => y(yKey(d)))
      .attr('r', 7)
      .attr('fill', (d) => sensorColor(d.sensor))
      .attr('opacity', 0.9)
      .append('title')
      .text((d) => `${d.sensor} · ${d.target_id} · ${xKey(d).toFixed(1)} nm`)

    svg
      .append('text')
      .attr('x', margin.left)
      .attr('y', 12)
      .attr('fill', '#8b9cb0')
      .attr('font-size', 10)
      .text('Slant/ground range (nm)')

    svg
      .append('text')
      .attr('x', 8)
      .attr('y', height / 2)
      .attr('fill', '#8b9cb0')
      .attr('font-size', 10)
      .attr('transform', `rotate(-90 8,${height / 2})`)
      .text('Footprint (m)')
  }

  $effect(() => {
    void points
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

<div class="panel flex h-full min-h-0 flex-col rounded-sm p-3">
  <h3 class="mb-2 text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
    Sensor collect · range vs footprint
  </h3>
  {#if !points?.length}
    <p class="text-sm text-[var(--muted)]">No collect geometry in this mission.</p>
  {:else}
    <div class="min-h-0 flex-1 overflow-hidden" bind:this={rootEl}></div>
  {/if}
</div>