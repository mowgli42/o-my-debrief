<script>
  /**
   * jQuery Flight Indicators (Sébastien Matton / GPLv3)
   * https://sebmatton.github.io/flightindicators/
   * https://github.com/sebmatton/jQuery-Flight-Indicators
   */
  import { onMount, onDestroy } from 'svelte'
  import jQuery from 'jquery'

  let {
    airspeed = 0,
    altitude = 0,
    heading = 0,
    roll = 0,
    pitch = 0,
    size = 108,
  } = $props()

  let host = $state(null)
  let elAir = $state(null)
  let elAtt = $state(null)
  let elAlt = $state(null)
  let elHdg = $state(null)

  let gauges = null
  let pluginReady = $state(false)
  let loadError = $state('')

  const IMG_DIR = '/flightindicators/img/'

  async function ensurePlugin() {
    if (typeof window === 'undefined') return
    window.jQuery = window.jQuery || jQuery
    window.$ = window.$ || jQuery
    if (typeof jQuery.fn.flightIndicator === 'function') return
    await new Promise((resolve, reject) => {
      const existing = document.querySelector('script[data-flight-indicators]')
      if (existing) {
        existing.addEventListener('load', () => resolve())
        existing.addEventListener('error', () => reject(new Error('flightindicators script failed')))
        if (typeof jQuery.fn.flightIndicator === 'function') resolve()
        return
      }
      const s = document.createElement('script')
      s.src = '/flightindicators/js/jquery.flightindicators.js'
      s.async = true
      s.dataset.flightIndicators = '1'
      s.onload = () => resolve()
      s.onerror = () => reject(new Error('Could not load jquery.flightindicators.js'))
      document.head.appendChild(s)
    })
  }

  function clampAirspeed(kts) {
    // Classic ASI face is ~0–160; keep needle on scale, show true value digitally.
    const v = Number(kts) || 0
    return Math.max(0, Math.min(160, v))
  }

  onMount(async () => {
    try {
      // CSS
      if (!document.querySelector('link[data-flight-indicators-css]')) {
        const link = document.createElement('link')
        link.rel = 'stylesheet'
        link.href = '/flightindicators/css/flightindicators.css'
        link.dataset.flightIndicatorsCss = '1'
        document.head.appendChild(link)
      }
      await ensurePlugin()
      const opts = { size, showBox: true, img_directory: IMG_DIR }
      // API: $.flightIndicator(placeholder, type, options) → instance with setters
      gauges = {
        airspeed: jQuery.flightIndicator(elAir, 'airspeed', {
          ...opts,
          airspeed: clampAirspeed(airspeed),
        }),
        attitude: jQuery.flightIndicator(elAtt, 'attitude', {
          ...opts,
          roll: roll || 0,
          pitch: pitch || 0,
        }),
        altimeter: jQuery.flightIndicator(elAlt, 'altimeter', {
          ...opts,
          altitude: altitude || 0,
          pressure: 1013,
        }),
        heading: jQuery.flightIndicator(elHdg, 'heading', {
          ...opts,
          heading: heading || 0,
        }),
      }
      pluginReady = true
    } catch (e) {
      loadError = String(e.message || e)
    }
  })

  $effect(() => {
    if (!gauges || !pluginReady) return
    gauges.airspeed.setAirSpeed(clampAirspeed(airspeed))
    gauges.attitude.setRoll(roll || 0)
    gauges.attitude.setPitch(pitch || 0)
    gauges.altimeter.setAltitude(altitude || 0)
    gauges.heading.setHeading(((heading % 360) + 360) % 360)
  })

  onDestroy(() => {
    gauges = null
  })
</script>

<section class="fi-panel rounded-sm border border-[var(--line)] bg-[var(--bg-deep)] p-2" bind:this={host}>
  <div class="mb-2 flex items-center justify-between gap-2">
    <div class="text-[10px] uppercase tracking-wider text-[var(--muted)]">Flight instruments</div>
    <a
      class="text-[10px] text-[var(--accent)] hover:underline"
      href="https://sebmatton.github.io/flightindicators/"
      target="_blank"
      rel="noopener noreferrer"
    >
      Flight Indicators
    </a>
  </div>

  {#if loadError}
    <p class="text-xs text-[var(--danger)]">{loadError}</p>
  {/if}

  <div class="fi-grid">
    <div class="fi-cell">
      <div class="fi-label">Airspeed</div>
      <span bind:this={elAir} class="fi-host"></span>
      <div class="fi-readout mono">{Math.round(airspeed || 0)} kts</div>
    </div>
    <div class="fi-cell">
      <div class="fi-label">Attitude</div>
      <span bind:this={elAtt} class="fi-host"></span>
      <div class="fi-readout mono">
        R {Math.round(roll || 0)}° · P {Math.round(pitch || 0)}°
      </div>
    </div>
    <div class="fi-cell">
      <div class="fi-label">Altimeter</div>
      <span bind:this={elAlt} class="fi-host"></span>
      <div class="fi-readout mono">{Math.round(altitude || 0).toLocaleString()} ft</div>
    </div>
    <div class="fi-cell">
      <div class="fi-label">Heading</div>
      <span bind:this={elHdg} class="fi-host"></span>
      <div class="fi-readout mono">{String(Math.round(((heading % 360) + 360) % 360)).padStart(3, '0')}°</div>
    </div>
  </div>
</section>

<style>
  .fi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }
  .fi-cell {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 0;
  }
  .fi-label {
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.25rem;
  }
  .fi-host {
    display: block;
    line-height: 0;
  }
  .fi-readout {
    margin-top: 0.25rem;
    font-size: 11px;
    color: var(--accent);
  }
  /* Keep instrument chrome tight in the narrow panel */
  .fi-panel :global(div.instrument) {
    width: 108px !important;
    height: 108px !important;
  }
</style>
