<script>
  import * as d3 from 'd3'

  /** @type {{ releases?: object[], larSummary?: object }} */
  let { releases = [], larSummary = {} } = $props()

  let rootEl = $state(null)
  let width = $state(520)
  const size = 240
  const margin = 12

  function render() {
    if (!rootEl || !releases?.length) return
    d3.select(rootEl).selectAll('svg').remove()
    const svg = d3.select(rootEl).append('svg').attr('width', width).attr('height', size + 40)

    const r = releases[0]
    const radius = Number(r.lar_radius_nm) || 10
    const inner = Math.min(width, size) - margin * 2
    const cx = width / 2
    const cy = size / 2
    const scale = (inner / 2) / (radius * 1.15)

    const g = svg.append('g').attr('transform', `translate(${cx},${cy})`)

    g.append('circle')
      .attr('r', radius * scale)
      .attr('fill', 'rgba(61,214,198,0.08)')
      .attr('stroke', 'var(--accent)')
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '4 3')

    g.append('circle').attr('r', 3).attr('fill', '#e8ecf4')

    releases.forEach((rel) => {
      const range = Number(rel.release_slant_range_nm) || 0
      const az = ((Number(rel.release_azimuth_deg) || 0) * Math.PI) / 180
      const px = Math.sin(az) * range * scale
      const py = -Math.cos(az) * range * scale
      g.append('circle')
        .attr('cx', px)
        .attr('cy', py)
        .attr('r', 8)
        .attr('fill', rel.within_lar ? 'var(--strike)' : 'var(--danger)')
        .attr('stroke', '#0d1219')
        .attr('stroke-width', 1)
        .append('title')
        .text(`${rel.task_id} · ${range} nm · ${rel.within_lar ? 'in LAR' : 'outside LAR'}`)
    })

    svg
      .append('text')
      .attr('x', margin)
      .attr('y', size + 28)
      .attr('fill', '#8b9cb0')
      .attr('font-size', 11)
      .text(
        `LAR R=${radius} nm · ${larSummary.in_lar ?? 0}/${larSummary.total ?? 0} in envelope`,
      )
  }

  $effect(() => {
    void releases
    void larSummary
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

<div class="panel rounded-sm p-3">
  <h3 class="mb-2 text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
    Weapons release vs LAR
  </h3>
  {#if !releases?.length}
    <p class="text-sm text-[var(--muted)]">No weapon releases with LAR data.</p>
  {:else}
    <div bind:this={rootEl}></div>
  {/if}
</div>