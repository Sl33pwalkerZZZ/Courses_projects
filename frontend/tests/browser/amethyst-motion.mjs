// Actual Firefox mouse/scroll/preference regression. All APIs are synthetic GETs.
// Evaluate this async function through Playwright MCP; no real user/database writes.
// eslint-disable-next-line no-unused-expressions
async (initialPage) => {
  const browser = initialPage.context().browser()
  if (browser.browserType().name() !== 'firefox') throw new Error('Firefox required')
  const directory = '/home/almas/Desktop/courses/Courses_projects/.playwright-mcp'
  const base = 'http://localhost:5173'
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'no-preference' })
  const errors = [], unexpected = [], passed = [], frames = [], evidence = {}
  let step = 'setup'
  const assert = (condition, message) => { if (!condition) throw new Error(message) }
  const course = { id: 998001, slug: 'amethyst-motion-fixture', title: 'Applied AI workflows', description: 'Synthetic browser-only material.', author: 'Fixture author', level: 'beginner', direction: { slug: 'applied-ai', name: 'Applied AI' }, enrollment_mode: 'approval', review_count: 0, average_rating: null, modules: [{ id: 998011, title: 'Explore and practice', order: 1, lessons: [{ id: 998101, title: 'A practical workflow', order: 1 }] }] }
  const second = { ...course, id: 998002, slug: 'automation-fixture', title: 'Automation for work', direction: { slug: 'automation', name: 'Automation' } }
  let longTitle = false
  await context.addInitScript(() => {
    localStorage.setItem('ai-courses-language', 'en'); localStorage.setItem('ai-courses-theme', 'light')
    window.__entryFrames = []
    let previous
    new MutationObserver(() => {
      const entry = document.querySelector('.entry-signal')
      if (entry && entry.dataset.entry !== previous) {
        previous = entry.dataset.entry
        window.__entryFrames.push({ mode: previous, time: performance.now(), readyHeading: Boolean(document.getElementById('hero-title')), pointer: getComputedStyle(entry).pointerEvents, actions: Boolean(document.querySelector('.signal-hero-actions a[href="#course-library"]')) })
      }
    }).observe(document, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-entry'] })
  })
  await context.route('**/api/**', async (route) => {
    const request = route.request(), path = new URL(request.url()).pathname
    const headers = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'GET, OPTIONS' }
    const json = (data) => route.fulfill({ status: 200, headers, contentType: 'application/json', body: JSON.stringify(data) })
    if (request.method() === 'OPTIONS') return route.fulfill({ status: 204, headers })
    if (request.method() !== 'GET') { unexpected.push(`${request.method()} ${path}`); return route.fulfill({ status: 405, headers, body: '{}' }) }
    if (path === '/api/courses/') return json([course, second])
    if (path === `/api/courses/${course.slug}/`) return json({ ...course, title: longTitle ? 'Қызығушылықтарыңыздыңбайланыстарынзерттеушілерге арналған курс' : course.title })
    if (path === `/api/courses/${course.slug}/reviews/`) return json({ reviews: [], my_review: null, review_count: 0, average_rating: null })
    unexpected.push(path); return route.fulfill({ status: 404, headers, body: '{}' })
  })
  const page = await context.newPage()
  page.setDefaultTimeout(10000)
  page.on('pageerror', (error) => errors.push(error.message))
  const frame = async (name) => { const path = `${directory}/amethyst-motion-${name}.png`; await page.screenshot({ path }); frames.push(path) }
  // Firefox caps/animates very large wheel deltas. Use human-sized wheel steps
  // and wait for actual document positions instead of assuming elapsed time.
  const wheelTo = async (requested) => {
    const desired = await page.evaluate((y) => Math.max(0, Math.min(y, document.scrollingElement.scrollHeight - innerHeight)), requested)
    for (let attempt = 0; attempt < 30; attempt++) {
      const current = await page.evaluate(() => scrollY)
      if (Math.abs(current - desired) < 4) return
      const delta = Math.sign(desired - current) * Math.min(500, Math.abs(desired - current))
      await page.mouse.wheel(0, delta)
      await page.waitForFunction((next) => Math.abs(scrollY - next) < 4, current + delta, { timeout: 5000 })
    }
    throw new Error('Document did not reach the requested wheel position')
  }

  const matrix = (selector) => page.locator(selector).first().evaluate((element) => {
    const m = new DOMMatrix(getComputedStyle(element).transform)
    return { x: m.m41, y: m.m42, a: m.a, b: m.b, d: m.d, scale: Math.hypot(m.a, m.b) }
  })
  try {
    step = 'opening sequence'
    await page.goto(base, { waitUntil: 'domcontentloaded' })
    await page.locator('#hero-title').waitFor()
    await frame('entry-0'); await page.waitForTimeout(180); await frame('entry-1')
    await page.waitForFunction(() => document.querySelector('.entry-signal')?.dataset.entry === 'ready')
    await frame('entry-2')
    evidence.entry = await page.evaluate(() => window.__entryFrames)
    assert(evidence.entry.some((item) => item.mode === 'first' && item.readyHeading && item.actions && item.pointer === 'none'), 'Entry blocked ready content')
    const first = evidence.entry.find((item) => item.mode === 'first'), ready = evidence.entry.find((item) => item.mode === 'ready')
    assert(ready && ready.time - first.time < 1800, 'Opening was an artificial delay')
    passed.push('nonblocking first entry and actual signal frame sequence')

    step = 'cursor-watching companion'
    await page.waitForFunction(() => document.querySelector('.ai-companion')?.dataset.tracking === 'pointer')
    const hero = await page.locator('.signal-hero').boundingBox()
    await page.mouse.move(hero.x + 40, hero.y + 100); await page.waitForTimeout(350)
    const left = await matrix('.companion-pupils'); await frame('eyes-left')
    await page.mouse.move(hero.x + hero.width - 30, hero.y + hero.height - 60); await page.waitForTimeout(350)
    const right = await matrix('.companion-pupils'); await frame('eyes-right')
    assert(Math.abs(right.x - left.x) > 3, 'Pupils did not follow real mouse movement')
    for (const pose of [left, right]) assert(Math.hypot(pose.x + 4, pose.y + 1) <= 10.5, 'Pupils escaped eye bounds')
    await page.locator('.signal-hero-actions a').first().hover(); await page.waitForTimeout(350)
    assert((await matrix('.companion-face')).scale > 1.01, 'Companion button expression missing')
    await page.mouse.move(5, 5); await page.waitForTimeout(650)
    const rest = await matrix('.companion-pupils')
    assert(Math.abs(rest.x + 4) < .15 && Math.abs(rest.y + 1) < .15, 'Companion continued tracking outside its UI')
    evidence.eyes = { left, right, rest }
    await page.waitForFunction(() => new DOMMatrix(getComputedStyle(document.querySelector('.companion-eyes')).transform).d < .6, null, { polling: 'raf', timeout: 6500 })
    await page.waitForTimeout(450)
    assert((await matrix('.companion-eyes')).d > .9, 'Idle blink did not reopen')
    passed.push('bounded eyes, spring head, nearby-button expression, outside-host rest and idle blink')

    step = 'interactive letters'
    const letter = page.locator('#hero-title .animated-letter').first()
    const bounds = await letter.boundingBox(), before = await page.locator('#hero-title').boundingBox()
    await page.mouse.move(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2); await page.waitForTimeout(300)
    const hover = await matrix('#hero-title .animated-letter')
    assert(hover.y < -1 && hover.y > -11, 'Letter spring did not respond within bounds')
    await frame('letters-hover')
    const after = await page.locator('#hero-title').boundingBox()
    assert(Math.abs(after.height - before.height) < 1 && Math.abs(after.width - before.width) < 1, 'Letter motion shifted layout')
    await page.mouse.move(5, 5); await page.waitForTimeout(800)
    const settled = await matrix('#hero-title .animated-letter')
    assert(Math.abs(settled.y) < .1 && Math.abs(settled.scale - 1) < .01, 'Letters did not settle')
    await frame('letters-rest')
    passed.push('real letter hover, bounded spring, return to rest without layout shift')

    step = 'theme and Canvas synchronization'
    await page.locator('.header-preferences .theme-toggle').click()
    await page.waitForFunction(() => document.documentElement.dataset.theme === 'dark')
    await page.waitForTimeout(150)
    const palette = await page.evaluate(() => {
      const canvas = document.querySelector('canvas.particle-field'), scratch = document.createElement('canvas').getContext('2d')
      scratch.fillStyle = getComputedStyle(canvas).getPropertyValue('--v2-particle-dot').trim()
      return { actual: canvas.getContext('2d').fillStyle, expected: scratch.fillStyle, background: getComputedStyle(document.body).backgroundColor }
    })
    assert(palette.actual === palette.expected && palette.background === 'rgb(13, 8, 24)', 'Canvas or body retained the previous palette')
    evidence.palette = palette; await frame('dark-home')
    passed.push('live theme change updates Canvas and page palette together')

    step = 'scroll-linked forward and backward story'
    const geometry = await page.locator('#signal-story').evaluate((element) => ({ start: element.getBoundingClientRect().top + scrollY, range: element.offsetHeight - innerHeight }))
    evidence.story = []
    for (const [index, fraction] of [.1, .5, .9, .5, .1].entries()) {
      const desired = Math.round(geometry.start + geometry.range * fraction)
      await wheelTo(desired)
      await page.waitForTimeout(350)
      const state = await page.evaluate(() => {
        const chapters = [...document.querySelectorAll('.signal-story-chapter')].map((element) => Number(getComputedStyle(element).opacity))
        return { y: scrollY, chapter: chapters.indexOf(Math.max(...chapters)), sticky: document.querySelector('.signal-story-sticky').getBoundingClientRect().top, header: document.querySelector('.site-header').getBoundingClientRect().bottom, connections: document.querySelector('.story-connections').getAttribute('stroke-dasharray') }
      })
      assert(state.chapter === [0,1,2,1,0][index], 'Story did not respond to scroll direction')
      assert(state.sticky >= state.header, 'Story hid under the header')
      evidence.story.push(state); await frame(`story-${index}`)
    }
    assert(evidence.story[0].connections !== evidence.story[2].connections, 'Constellation did not evolve with scroll')
    await wheelTo(geometry.start + geometry.range + 900)
    await page.waitForTimeout(500)
    assert(await page.locator('#course-library').evaluate((element) => element.getBoundingClientRect().top < innerHeight), 'Sticky story trapped document scrolling')
    assert(await page.locator('.ai-companion').getAttribute('data-motion-active') === 'false', 'Offscreen companion remained active')
    const snapshot = await page.locator('canvas.particle-field').evaluate((canvas) => canvas.toDataURL())
    await page.waitForTimeout(500)
    assert(await page.locator('canvas.particle-field').evaluate((canvas) => canvas.toDataURL()) === snapshot, 'Offscreen particles kept drawing')
    passed.push('real wheel forward/back progression, evolving constellation, normal scroll ending and offscreen pause')

    step = 'actual category filter controls'
    await page.locator('.discovery-directions button').nth(1).click()
    assert(await page.locator('.academic-course-card').count() === 1, 'Direction chip did not filter')
    assert(await page.locator('#course-direction').inputValue() === 'applied-ai', 'Chip/select state diverged')
    await page.locator('.discovery-directions button').first().click()
    assert(await page.locator('.academic-course-card').count() === 2, 'All-directions reset failed')
    passed.push('category sequence preserves shared existing filter state')

    step = 'live reduced motion'
    await page.emulateMedia({ reducedMotion: 'reduce' })
    await page.waitForFunction(() => !document.querySelector('canvas.particle-field') && Boolean(document.querySelector('.signal-story-static')) && !document.querySelector('.entry-signal'))
    assert(await page.locator('.animated-letter').count() === 0, 'Interactive letters remained active in reduced motion')
    assert(await page.evaluate(() => document.getAnimations().filter((animation) => animation.playState === 'running').length) === 0, 'Reduced motion still has running animations')
    passed.push('live reduced-motion change removes Canvas, letters, entry and sticky composition')

    step = 'mobile ambient behavior'
    await page.emulateMedia({ reducedMotion: 'no-preference' })
    await page.setViewportSize({ width: 375, height: 812 })
    await wheelTo(0); await page.waitForTimeout(350)
    await page.waitForFunction(() => document.querySelector('.ai-companion')?.dataset.motionActive === 'true')
    assert(await page.locator('.ai-companion').getAttribute('data-tracking') === 'ambient', 'Mobile retained cursor tracking')
    assert(await page.locator('.signal-story-static').count() === 1 && await page.locator('.animated-letter').count() === 0, 'Mobile did not simplify motion')
    const ambient = await matrix('.companion-pupils')
    await page.mouse.move(100, 300); await page.waitForTimeout(250)
    const ambientAfter = await matrix('.companion-pupils')
    assert(Math.abs(ambient.x - ambientAfter.x) < .1 && Math.abs(ambient.y - ambientAfter.y) < .1, 'Mobile pupils tracked cursor')
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Mobile overflow')
    await frame('mobile-ambient')
    passed.push('mobile static story, ambient companion without cursor tracking')

    step = 'dynamic long Kazakh course title'
    longTitle = true
    await page.setViewportSize({ width: 901, height: 650 })
    await page.goto(`${base}/courses/${course.slug}`)
    await page.locator('#course-overview-title .animated-letter').first().waitFor()
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Long Kazakh word overflowed animated heading')
    await frame('long-title-901')
    passed.push('grapheme-safe long Kazakh heading emergency wrapping')

    step = 'subsequent entry'
    await page.goto(base)
    await page.locator('#hero-title').waitFor()
    assert(await page.locator('.entry-signal').count() === 0, 'Opening replayed on subsequent entry')
    passed.push('short subsequent navigation without replaying the opening')
    assert(!errors.length && !unexpected.length, `Unexpected errors/APIs: ${errors.join(',')}/${unexpected.join(',')}`)
    return { passed, evidence, frames, realApiRequests: 0, errors, unexpected }
  } catch (error) {
    await page.screenshot({ path: `${directory}/amethyst-motion-failure.png`, fullPage: true }).catch(() => {})
    throw new Error(`${step}: ${error.message}`)
  } finally { await context.close() }
}
