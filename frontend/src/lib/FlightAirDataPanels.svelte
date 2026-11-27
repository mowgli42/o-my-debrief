<script>
  import * as d3 from 'd3'

  /** @type {{ series?: object[], currentTime?: string | null, events?: object[] }} */
  let { series = [], currentTime = null, events = [] } = $props()

  let rootEl = $state(null)
  let width = $state(640)
  const panelH = 64
  const margin = { left: 48, right: 12, top: 6, bottom: 18 }

  const panels = [
    {
      id: 'perf',
      title: 'Altitude / speed',
      keys: [
        { key: 'alt_ft', label: 'Alt ft', color: '#4da3ff' },
        { key: 'speed_kts', label: 'Kts', color: '#5cd67e' },
        { key: 'vs_fpm', label: 'VS', color: '#eab308' },
      ],
    },
    {
      id: 'plan',
      title: 'Planned vs actual',
      keys: [
        { key: 'xte_nm', label: 'XTE nm', color: '#f59e0b' },
        { key: 'alt_error_ft', label: 'Δalt', color: '#4da3ff' },
        { key: 'spd_error_kts', label: 'Δspd', color: '#5cd67e' },
      ],
    },
    {
      id: 'att',
      title: 'Attitude',
      keys: [
        { key: 'roll_deg', label: 'Roll', color: '#ff7a45' },
        { key: 'pitch_deg', label: 'Pitch', color: '#a78bfa' },
      ],
    },
    {
      id: 'sys',
      title: 'Fuel / systems',
      keys: [
        { key: 'fuel_percent', label: 'Fuel %', color: '#eab308' },
        { key: 'fuel_flow_pph', label: 'FF pph', color: '#fb7185' },
        { key: 'bus_v', label: 'Bus V', color: '#3dd6c6' },
        { key: 'egt_c', label: 'EGT', color: '#ff5c6c' },
      ],
    },
  ]

  function render() {
    if (!rootEl) return
    d3.select(rootEl).selectAll('svg').remove()
    const parsed = (series || [])
      .map((d) => ({ ...d, _t: d3.isoParse(d.timestamp) || new Date(d.timestamp) }))
      .filter((d) => d._t)
    if (!parsed.length) return

    const innerW = width - margin.left - margin.right
    const x = d3.scaleTime().domain(d3.extent(parsed, (d) => d._t)).range([0, innerW])
    const totalH = panels.length * (panelH + 8) + 8
    const svg = d3.select(rootEl).append('svg').attr('width', width).attr('height', totalH)

    panels.forEach((panel, pi) => {
      const y0 = pi * (panelH + 8) + margin.top
      const g = svg.append('g').attr('transform', `translate(${margin.left},${y0})`)
      g.append('text')
        .attr('x', 0)
        .attr('y', 10)
        .attr('fill', '#8b9cb0')
        .attr('font-size', 10)
        .text(panel.title)

      panel.keys.forEach((s) => {
        const vals = parsed.filter((d) => d[s.key] != null)
        if (vals.length < 2) return
        const y = d3
          .scaleLinear()
          .domain(d3.extent(vals, (d) => Number(d[s.key])))
          .nice()
          .range([panelH - 4, 16])
        const line = d3
          .line()
          .x((d) => x(d._t))
          .y((d) => y(Number(d[s.key])))
          .curve(d3.curveMonotoneX)
        g.append('path')
          .datum(vals)
          .attr('fill', 'none')
          .attr('stroke', s.color)
          .attr('stroke-width', 1.4)
          .attr('d', line)
      })
    })

    if (currentTime) {
      const ct = d3.isoParse(currentTime)
      if (ct) {
        const xp = margin.left + x(ct)
        svg
          .append('line')
          .attr('x1', xp)
          .attr('x2', xp)
          .attr('y1', 0)
          .attr('y2', totalH)
          .attr('stroke', 'var(--accent)')
          .attr('stroke-width', 1.2)
          .attr('opacity', 0.85)
      }
    }

    for (const ev of events || []) {
      const t = d3.isoParse(ev.timestamp)
      if (!t) continue
      const xp = margin.left + x(t)
      svg
        .append('line')
        .attr('x1', xp)
        .attr('x2', xp)
        .attr('y1', 0)
        .attr('y2', totalH)
        .attr('stroke', ev.severity === 'WARN' ? '#ff5c6c' : '#eab308')
        .attr('stroke-dasharray', '2 2')
        .attr('opacity', 0.55)
    }
  }

  $effect(() => {
    void series
    void currentTime
    void events
    void width
    render()
  })

  $effect(() => {
    if (!rootEl) return
    const ro = new ResizeObserver(() => {
      width = Math.max(420, rootEl.clientWidth - 4)
      render()
    })
    ro.observe(rootEl)
    return () => ro.disconnect()
  })
</script>

<div class="panel rounded-sm p-3">
  <h3 class="mb-2 text-xs font-semibold tracking-[0.14em] uppercase text-[var(--accent)]">
    Air-data · synchronized
  </h3>
  {#if !series?.length}
    <p class="text-sm text-[var(--muted)]">No air-data series for this mission.</p>
  {:else}
    <div bind:this={rootEl}></div>
  {/if}
</div>