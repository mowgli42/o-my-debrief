/**
 * Capture debrief UI into docs/screenshots/
 * Requires API (:8020 default) and Vite (:5173 default).
 */
import { createRequire } from 'module'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const OUT = path.join(ROOT, 'docs', 'screenshots')
const BASE = process.env.DEMO_URL || 'http://127.0.0.1:8920'
// Resolve playwright from frontend/ even when this script lives under scripts/
const require = createRequire(path.join(ROOT, 'frontend', 'package.json'))
const { chromium } = require('playwright')

async function shot(page, name) {
  const file = path.join(OUT, name)
  await page.screenshot({ path: file, fullPage: false })
  console.log('wrote', file)
}

async function selectTab(page, name) {
  const tab = page.getByRole('tab', { name })
  await tab.click()
  await page.waitForTimeout(500)
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true })
  for (const name of fs.readdirSync(OUT)) {
    if (name.endsWith('.png')) fs.unlinkSync(path.join(OUT, name))
  }

  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(BASE, { waitUntil: 'networkidle' })
  await page.waitForSelector('text=Key milestones', { timeout: 30000 })
  await page.waitForTimeout(1200)

  const play = page.getByRole('button', { name: 'Play' })
  if (await play.count()) {
    await play.click()
    await page.waitForTimeout(2200)
    const pause = page.getByRole('button', { name: 'Pause' })
    if (await pause.count()) await pause.click()
  }
  await selectTab(page, /Mission/i)
  await page.waitForTimeout(400)
  await shot(page, '01-debrief-overview.png')
  await shot(page, '02-timeline-scrub.png')

  const strike = page.getByRole('button').filter({ hasText: /Strike EXECUTED/i }).first()
  if (await strike.count()) {
    await strike.click()
    await page.waitForTimeout(1000)
  }
  await selectTab(page, /Mission/i)
  await page.waitForTimeout(400)
  await shot(page, '03-strike-milestone.png')

  const bda = page.getByRole('button').filter({ hasText: /BDA/i }).first()
  if (await bda.count()) {
    await bda.click()
    await page.waitForTimeout(1000)
  }
  await selectTab(page, /Mission/i)
  await page.waitForTimeout(500)
  await shot(page, '04-mission-tab.png')

  await selectTab(page, /Launch\s*\/\s*Recovery/i)
  await page.waitForTimeout(800)
  await shot(page, '05-launch-recovery-tab.png')

  // Video association on main debrief (badges, no embedded player)
  const collect = page.getByRole('button').filter({ hasText: /EO collect/i }).first()
  if (await collect.count()) {
    await collect.click()
    await page.waitForTimeout(800)
  }
  await shot(page, '06-video-association.png')

  // Pop-out video viewer page (minimal)
  const mission = 'msn-demo-strike-recon'
  const videoPage = await browser.newPage({ viewport: { width: 720, height: 420 } })
  await videoPage.goto(`${BASE}/video.html?mission=${mission}`, { waitUntil: 'networkidle' })
  await videoPage.waitForTimeout(800)
  // Nudge via BroadcastChannel from a tiny evaluate after loading media
  await videoPage.evaluate(() => {
    const ch = new BroadcastChannel('omy-debrief-video')
    ch.postMessage({
      type: 'sync',
      missionId: 'msn-demo-strike-recon',
      currentTime: '2026-07-21T14:08:00Z',
      playing: false,
      clipId: 'clip-eo-042',
    })
  })
  await videoPage.waitForTimeout(1200)
  await shot(videoPage, '07-video-viewer.png')

  // Overlays off — classification remains
  await videoPage.evaluate(() => {
    localStorage.setItem('omy-debrief-video-overlays', '0')
  })
  await videoPage.reload({ waitUntil: 'networkidle' })
  await videoPage.waitForTimeout(600)
  await videoPage.evaluate(() => {
    const ch = new BroadcastChannel('omy-debrief-video')
    ch.postMessage({
      type: 'sync',
      missionId: 'msn-demo-strike-recon',
      currentTime: '2026-07-21T14:08:00Z',
      playing: false,
      clipId: 'clip-eo-042',
    })
  })
  await videoPage.waitForTimeout(1000)
  await shot(videoPage, '08-video-overlays-off.png')
  await videoPage.close()

  // Plan vs as-executed compare
  await page.bringToFront()
  const compare = page.getByRole('button', { name: 'Compare' })
  if (await compare.count()) {
    await compare.click()
    await page.waitForTimeout(900)
    await shot(page, '09-plan-vs-actual-compare.png')

    const hidePlan = page.getByRole('switch', { name: 'Hide mission plan' })
    if (await hidePlan.count()) {
      await hidePlan.click()
      await page.waitForTimeout(500)
      await shot(page, '10-compare-hide-plan.png')
      await hidePlan.click()
      await page.waitForTimeout(300)
    }

    const plannedRoute = page.getByRole('switch', { name: 'Show planned route' })
    if (await plannedRoute.count()) {
      await plannedRoute.click()
      await page.waitForTimeout(400)
      await shot(page, '11-planned-route-off.png')
      await plannedRoute.click()
    }
    // Leave compare so Analysis can take the center pane
    await compare.click()
    await page.waitForTimeout(400)
  }

  // Analysis mode: FOV scatter, LAR, sensor telemetry
  const analysis = page.getByRole('button', { name: 'Analysis' })
  if (await analysis.count()) {
    await analysis.click()
    await page.waitForTimeout(1200)
    await page.waitForSelector('text=Sensor collect', { timeout: 15000 })
    await shot(page, '12-analysis-fov-lar.png')
    // Scroll telemetry into view within center panel
    const telem = page.getByText('Sensor & platform telemetry')
    if (await telem.count()) {
      await telem.scrollIntoViewIfNeeded()
      await page.waitForTimeout(400)
      await shot(page, '13-analysis-sensor-telemetry.png')
    }
  }

  // Post Mission Report HTML (print-ready 3 pages)
  const apiBase = process.env.DEBRIEF_API || 'http://127.0.0.1:8020'
  const pmr = await browser.newPage({ viewport: { width: 900, height: 1100 } })
  await pmr.goto(`${apiBase}/api/report/pmr?mission=msn-demo-strike-recon`, {
    waitUntil: 'networkidle',
  })
  await pmr.waitForSelector('text=Mission Overview', { timeout: 15000 })
  await shot(pmr, '14-pmr-page1-overview.png')
  await pmr.locator('#page-2-platform-sensor-health').scrollIntoViewIfNeeded()
  await pmr.waitForTimeout(300)
  await shot(pmr, '15-pmr-page2-health.png')
  await pmr.locator('#page-3-fov-details').scrollIntoViewIfNeeded()
  await pmr.waitForTimeout(300)
  await shot(pmr, '16-pmr-page3-fov-details.png')
  await pmr.close()

  await browser.close()
  console.log('done')
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
