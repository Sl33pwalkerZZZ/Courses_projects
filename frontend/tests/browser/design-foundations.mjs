// Run with Playwright MCP browser_run_code_unsafe({ filename: <this file> }).
// All API responses are synthetic; no real account or database mutations.
// eslint-disable-next-line no-unused-expressions -- The MCP VM evaluates this function as its entry point.
async (initialPage) => {
  const browser = initialPage.context().browser()
  if (browser.browserType().name() !== 'firefox') throw new Error('Firefox is required')
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' })
  await context.addInitScript(() => {
    localStorage.setItem('ai-courses-language', 'en')
    localStorage.setItem('ai-courses-theme', 'light')
  })
  const page = await context.newPage()
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  const first = { id: 990001, slug: 'foundation-fixture', title: 'Signal basics', description: 'Synthetic practical material.', author: 'Fixture',
    level: 'beginner', direction: { slug: 'signals', name: 'Signals' }, review_count: 0, average_rating: null, modules: [], enrollment_mode: 'approval' }
  const second = { ...first, id: 990002, slug: 'automation-fixture', title: 'Workflow practice', level: 'advanced', direction: { slug: 'automation', name: 'Automation' } }
  let mode = 'ok'
  let courseRequests = 0
  const blocked = []
  const unexpected = []
  await context.route('**/api/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    const headers = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'GET, OPTIONS' }
    const json = (body, status = 200) => route.fulfill({ status, headers, contentType: 'application/json', body: JSON.stringify(body) })
    if (request.method() === 'OPTIONS') return route.fulfill({ status: 204, headers })
    if (request.method() !== 'GET') { blocked.push(path); return json({}, 405) }
    if (path === '/api/courses/') {
      courseRequests++
      if (mode === 'error') return json({ detail: 'Synthetic server failure' }, 500)
      return json(mode === 'empty' ? [] : [first, second])
    }
    if (path === `/api/courses/${first.slug}/`) return json(first)
    if (path === `/api/courses/${first.slug}/reviews/`) return json({ reviews: [], my_review: null, average_rating: null, review_count: 0 })
    unexpected.push(path)
    return json({}, 404)
  })
  const require = (condition, message) => { if (!condition) throw new Error(message) }
  const landed = async () => {
    await page.waitForFunction(() => {
      const target = document.querySelector('#course-library')
      const header = document.querySelector('.site-header')
      return target && target.getBoundingClientRect().top >= header.getBoundingClientRect().bottom
        && target.getBoundingClientRect().top < innerHeight
    })
  }
  try {
    await page.goto('http://127.0.0.1:5175/')
    await page.locator('.academic-course-card').nth(1).waitFor()
    require(await page.locator('.academic-course-card').count() === 2, 'Initial course count')
    const requests = courseRequests
    await page.locator('#course-search').fill('Workflow')
    require(await page.locator('.academic-course-card').count() === 1, 'Search preserved')
    await page.locator('#course-level').selectOption('beginner')
    await page.locator('.catalog-state').waitFor()
    await page.locator('.filter-reset').click()
    await page.locator('#course-direction').selectOption('signals')
    require(await page.locator('.academic-course-card').count() === 1, 'Direction filter preserved')
    await page.locator('.filter-reset').click()
    require(courseRequests === requests, 'Filters should not request API data')
    await page.evaluate(() => scrollTo(0, 0))
    await page.locator('.header-nav .catalog-nav-link').click()
    await landed()
    await page.evaluate(() => scrollTo(0, 0))
    await page.locator('.header-nav .catalog-nav-link').click()
    await landed()
    await page.locator(`a[href="/courses/${first.slug}"]`).click()
    await page.locator('h1').filter({ hasText: first.title }).waitFor()
    await page.locator('.header-nav .catalog-nav-link').click()
    await landed()

    await page.setViewportSize({ width: 320, height: 812 })
    await page.evaluate(() => scrollTo(0, 0))
    const menu = page.locator('.header-menu-toggle')
    await menu.focus()
    await page.keyboard.press('Enter')
    await page.locator('dialog[open]').waitFor()
    require(await page.evaluate(() => document.querySelector('dialog').contains(document.activeElement)), 'Focus enters menu')
    await page.keyboard.press('Escape')
    await page.waitForFunction(() => !document.querySelector('dialog'))
    require(await menu.evaluate((element) => document.activeElement === element), 'Escape restores menu focus')
    await menu.click()
    await page.getByRole('button', { name: 'Қазақша', exact: true }).click()
    require(await page.locator('html').getAttribute('lang') === 'kk', 'Mobile Kazakh switching')
    await page.keyboard.press('Escape')
    require(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), '320px overflow')

    mode = 'error'
    await page.reload()
    await page.locator('.catalog-state[role="alert"]').waitFor()
    mode = 'ok'
    await page.locator('.catalog-state button').click()
    await page.locator('.academic-course-card').nth(1).waitFor()
    mode = 'empty'
    await page.reload()
    await page.locator('.catalog-state').waitFor()
    require(await page.locator('.academic-course-card').count() === 0, 'Empty response has no fake cards')
    require(blocked.length === 0 && unexpected.length === 0 && errors.length === 0, 'Unexpected API call or runtime error')
    return { passed: ['search/direction/level/reset without refetch', 'no-results', 'same-hash repeat scrolling', 'cross-page catalog navigation', 'menu focus/Escape/return', 'mobile localization', '320px overflow', 'error/retry', 'empty API response'], realApiRequests: 0 }
  } finally {
    await context.close()
  }
}
