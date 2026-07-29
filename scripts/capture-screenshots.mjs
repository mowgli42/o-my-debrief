/**
 * Capture debrief UI into docs/screenshots/
 * Requires API (:8020 default) and Vite (:5173 default).
 */
import { chromium } from 'playwright'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const OUT = path.join(ROOT, 'docs', 'screenshots')
const BASE = process.env.DEMO_URL || 'http://127.0.0.1:5173'

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
  await videoPage.close()

  await browser.close()
  console.log('done')
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
