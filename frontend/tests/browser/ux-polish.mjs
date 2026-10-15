// Run through Playwright MCP browser_run_code_unsafe with filename set to this file.
// Self-contained for the MCP VM: no imports, installations, or real API mutations.

// eslint-disable-next-line no-unused-expressions -- Playwright MCP evaluates this function as its entry point.
async (initialPage) => {
  const browser = initialPage.context().browser()
  if (browser.browserType().name() !== 'firefox') throw new Error('Run this fixture in Firefox')
  // An about:blank MCP page may override this for an isolated Vite test server.
  const baseURL = await initialPage.evaluate(() => window.__uxPolishBaseURL || 'http://localhost:5173')
  const screenshotDirectory = '/home/almas/Desktop/courses/Courses_projects/.playwright-mcp'
  const assert = {
    equal(actual, expected) { if (actual !== expected) throw new Error('UX fixture equality assertion failed') },
    ok(value) { if (!value) throw new Error('UX fixture assertion failed') },
    deepEqual(actual, expected) { if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error('UX fixture collection assertion failed') },
  }
  const english = { course: {"loadError": "The course could not be loaded", "notFound": "Course not found."} }
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' })
  const page = await context.newPage()
  const course = {
    id: 900001, slug: 'ux-polish-fixture', title: 'UX regression fixture', description: 'Synthetic test material.',
    author: 'Fixture author', level: 'beginner', enrollment_mode: 'approval', direction: { name: 'Fixture', slug: 'fixture' },
    review_count: 0, average_rating: null,
    modules: [{ id: 900011, title: 'Fixture module', order: 1, lessons: [{ id: 900101, title: 'Fixture lesson', order: 1 }] }],
  }
  const alternatives = { en: 'Authored diagram description', ru: 'Авторское описание схемы', kk: 'Сызбаның авторлық сипаттамасы' }
  let courseMode = 'server-error'
  let rejected = false
  let enrolled = false
  let courseRequests = 0
  const imageRequests = []
  const mutations = []
  const unexpected = []
  const pageErrors = []
  page.on('pageerror', (error) => pageErrors.push(error.message))
  const tokens = await page.evaluate(() => {
    const token = (type) => {
      const claims = btoa(JSON.stringify({ user_id: 900001, token_type: type, exp: Math.floor(Date.now() / 1000) + 3600 })).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_')
      return `fixture.${claims}.fixture`
    }
    return { access: token('access'), refresh: token('refresh') }
  })
  await context.route('**/api/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    const headers = { 'access-control-allow-origin': '*', 'access-control-allow-headers': 'authorization, content-type', 'access-control-allow-methods': 'GET, HEAD, POST, OPTIONS' }
    if (request.method() === 'OPTIONS') return route.fulfill({ status: 204, headers })
    const json = (body, status = 200) => route.fulfill({ status, headers, contentType: 'application/json', body: JSON.stringify(body) })
    if (path === '/api/auth/token/' && request.method() === 'POST') {
      return json(tokens)
    }
    if (!['GET', 'HEAD'].includes(request.method())) {
      mutations.push(path)
      return json({ detail: 'Mutation blocked by regression fixture' }, 405)
    }
    if (path === `/api/courses/${course.slug}/`) {
      courseRequests++
      if (courseMode === 'server-error') return json({ detail: 'Fixture failure' }, 500)
      if (courseMode === 'not-found') return json({ detail: 'Not found' }, 404)
      if (courseMode === 'network-error') return route.abort('failed')
      return json(course)
    }
    if (path === '/api/courses/') return json([course])
    if (path === `/api/courses/${course.slug}/reviews/`) return json({ reviews: [], average_rating: null, review_count: 0, my_review: null })
    if (path === '/api/my/enrollments/') return json(enrolled ? [{
      id: 900201, course, total_lessons: 1, completed_lessons: 0, progress_percent: 0,
      is_completed: false, next_lesson_id: 900101, completed_lesson_ids: [],
    }] : [])
    if (path === '/api/my/enrollment-requests/') return json(rejected ? [{
      id: 900301, course, status: 'rejected', admin_note: 'Fixture decision', created_at: '2026-01-01T00:00:00Z',
    }] : [])
    if (path === '/api/lessons/900101/') return json({
      id: 900101, title: 'Fixture lesson', order: 1, text_content: 'Synthetic material.', course_slug: course.slug,
      completed_at: null, assignments: [], images: [
        { id: 900401, image: '/api/lesson-images/900401/', order: 1, alt_text: alternatives },
        { id: 900402, image: '/api/lesson-images/900402/', order: 2, alt_text: {} },
      ],
    })
    if (path === '/api/lessons/900101/quiz/') return json({ quiz: null })
    if (/^\/api\/lesson-images\/90040[12]\/$/.test(path)) {
      imageRequests.push({ path, authenticated: Boolean(request.headers().authorization) })
      return route.fulfill({ status: 200, headers, contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4"><rect width="4" height="4"/></svg>' })
    }
    unexpected.push(path)
    return json({ detail: 'Unrecognized fixture endpoint' }, 404)
  })

  const wait = (predicate) => page.waitForFunction(predicate)
  const screenshot = async (name) => {
    if (screenshotDirectory) await page.screenshot({ path: `${screenshotDirectory}/ux-polish-${name}.png`, fullPage: true })
  }
  try {
    await page.goto(`${baseURL}/courses/${course.slug}`)
    await page.getByRole('button', { name: 'English', exact: true }).click()
    await page.getByRole('heading', { name: english.course.loadError, exact: true }).waitFor()
    const beforeRetry = courseRequests
    await screenshot('server-error')
    courseMode = 'ok'
    await page.locator('.course-overview-state button').click()
    await page.getByRole('heading', { name: course.title, exact: true }).waitFor()
    assert.equal(courseRequests, beforeRetry + 1)

    courseMode = 'not-found'
    await page.reload()
    await page.getByRole('heading', { name: english.course.notFound, exact: true }).waitFor()
    assert.equal(await page.locator('.course-overview-state button').count(), 0)
    courseMode = 'network-error'
    await page.reload()
    await page.getByRole('heading', { name: english.course.loadError, exact: true }).waitFor()
    courseMode = 'ok'
    await page.locator('.course-overview-state button').click()
    await page.getByRole('heading', { name: course.title, exact: true }).waitFor()

    await page.evaluate(async () => {
      const { login } = await import('/src/api.js')
      await login('synthetic-fixture', 'synthetic-password')
    })
    const requestButton = page.locator('.course-enrollment button.btn-primary')
    await requestButton.waitFor()
    assert.equal(await page.locator('.enrollment-form textarea').count(), 0)
    const exerciseFocus = async () => {
      const label = await requestButton.innerText()
      await requestButton.focus()
      await page.keyboard.press('Enter')
      await wait(() => document.activeElement?.tagName === 'TEXTAREA')
      await screenshot(rejected ? 'reapply-focus' : 'request-focus')
      await page.locator('.enrollment-form button[type="button"]').focus()
      await page.keyboard.press('Enter')
      await wait(() => document.activeElement?.matches('.course-enrollment button.btn-primary'))
      assert.equal(await requestButton.innerText(), label)
    }
    await exerciseFocus()
    rejected = true
    await page.reload()
    await requestButton.waitFor()
    await exerciseFocus()

    enrolled = true
    await page.goto(`${baseURL}/lessons/900101`)
    await wait(() => {
      const images = [...document.querySelectorAll('.lesson-material-images img')]
      return images.length === 2 && images.every((image) => image.complete && image.naturalWidth > 0)
    })
    const images = page.locator('.lesson-material-images img')
    const sources = await images.evaluateAll((elements) => elements.map((image) => image.src))
    assert.ok(sources.every((source) => source.startsWith('blob:')))
    const initialImageRequests = imageRequests.length
    for (const [button, language] of [['Русский', 'ru'], ['Қазақша', 'kk'], ['English', 'en']]) {
      await page.getByRole('button', { name: button, exact: true }).click()
      await page.waitForFunction((lang) => document.documentElement.lang === lang, language)
      assert.equal(await images.nth(0).getAttribute('alt'), alternatives[language])
      assert.equal(await images.nth(0).getAttribute('lang'), language)
      assert.equal(await images.nth(1).getAttribute('alt'), '')
    }
    assert.deepEqual(await images.evaluateAll((elements) => elements.map((image) => image.src)), sources)
    assert.equal(imageRequests.length, initialImageRequests)
    assert.ok(imageRequests.every((request) => request.authenticated))
    await screenshot('lesson-alternatives')
    assert.deepEqual(mutations, [])
    assert.deepEqual(unexpected, [])
    assert.deepEqual(pageErrors, [])
    return { passed: ['500 retry', '404 distinction', 'network retry', 'request focus/cancel', 'reapply focus/cancel', 'localized informative alt', 'decorative alt', 'JWT blob loading without language refetch'], imageRequests: imageRequests.length, realApiRequests: 0 }
  } finally {
    await context.close()
  }
}
