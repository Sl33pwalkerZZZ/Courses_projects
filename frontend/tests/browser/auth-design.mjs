// Run using Playwright MCP browser_run_code_unsafe with filename set to this file.
// Every API request is intercepted. No real credentials, accounts or DB writes.
// eslint-disable-next-line no-unused-expressions -- Entry point evaluated by the MCP VM.
async (initialPage) => {
  const browser = initialPage.context().browser()
  if (browser.browserType().name() !== 'firefox') throw new Error('Firefox required')
  const require = (condition, message) => { if (!condition) throw new Error(message) }
  const passed = []

  for (const mode of ['login', 'register']) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' })
    await context.addInitScript(() => {
      localStorage.setItem('ai-courses-language', 'en')
      localStorage.setItem('ai-courses-theme', 'light')
    })
    const page = await context.newPage()
    const counts = { token: 0, register: 0 }
    const unexpected = []
    const errors = []
    let tokenMode = 'reject'
    let registerMode = 'reject'
    let coursesGate = Promise.resolve()
    let releaseCourses
    let coursesError = false
    let courses = []
    let release
    page.on('pageerror', (error) => errors.push(error.message))
    const pair = await page.evaluate(() => {
      const make = (type) => {
        const payload = btoa(JSON.stringify({ user_id: 990100, token_type: type, exp: Math.floor(Date.now() / 1000) + 3600 })).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_')
        return `fixture.${payload}.fixture`
      }
      return { access: make('access'), refresh: make('refresh') }
    })
    await context.route('**/api/**', async (route) => {
      const request = route.request()
      const path = new URL(request.url()).pathname
      const headers = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'GET, POST, OPTIONS' }
      const json = (body, status = 200) => route.fulfill({ status, headers, contentType: 'application/json', body: JSON.stringify(body) })
      if (request.method() === 'OPTIONS') return route.fulfill({ status: 204, headers })
      if (request.method() === 'POST' && path === '/api/auth/token/') {
        counts.token++
        const decision = tokenMode
        if (decision === 'network') return route.abort('failed')
        if (decision === 'pending') await new Promise((resolve) => { release = resolve })
        return decision === 'ok' ? json(pair) : json({ detail: 'Synthetic invalid credentials' }, 401)
      }
      if (request.method() === 'POST' && path === '/api/auth/register/') {
        counts.register++
        const decision = registerMode
        if (decision === 'network') return route.abort('failed')
        if (decision === 'pending') await new Promise((resolve) => { release = resolve })
        return decision === 'ok' ? json({ username: 'fixture-only-user' }, 201) : json({ username: ['Synthetic duplicate username.'] }, 400)
      }
      if (request.method() === 'GET' && path === '/api/courses/') {
        await coursesGate
        return coursesError ? json({ detail: 'Synthetic course failure' }, 500) : json(courses)
      }
      unexpected.push(`${request.method()} ${path}`)
      return json({ detail: 'Blocked by isolated auth fixture' }, 405)
    })

    try {
      await page.goto(`http://localhost:5173/${mode}`)
      const username = page.locator('#auth-username')
      const password = page.locator('#auth-password')
      const submit = page.locator('.auth-submit')
      const form = page.locator('.auth-form')
      await username.waitFor()
      await submit.click()
      require(counts.token + counts.register === 0, `${mode}: empty form sent API request`)
      require(await username.evaluate((input) => document.activeElement === input), `${mode}: required focus`)
      await username.fill('fixture-only-user')

      if (mode === 'register') {
        await page.locator('#auth-email').fill('invalid-email')
        await password.fill('FixturePass123!')
        await submit.click()
        require(await page.locator('#auth-email').evaluate((input) => input.validity.typeMismatch), 'Register email validation')
        require(counts.register === 0, 'Invalid email submitted')
        await page.locator('#auth-email').fill('')
        await password.fill('')
        await password.pressSequentially('short')
        await submit.click()
        require(await password.evaluate((input) => input.validity.tooShort), 'Register minimum password length')
        require(counts.register === 0, 'Short password submitted')
      }

      await password.fill('FixturePass123!')
      await password.focus()
      await page.keyboard.press('Tab')
      require(await page.locator('.auth-password-toggle').evaluate((button) => document.activeElement === button), `${mode}: keyboard visibility control`)
      await page.keyboard.press('Space')
      require(await password.getAttribute('type') === 'text', `${mode}: reveal password`)
      require(await password.inputValue() === 'FixturePass123!', `${mode}: visibility changed value`)
      await page.keyboard.press('Space')
      require(await password.getAttribute('type') === 'password', `${mode}: hide password`)
      await page.keyboard.press('Tab')
      require(await submit.evaluate((button) => document.activeElement === button), `${mode}: keyboard submit order`)
      await page.keyboard.press('Enter')
      await page.locator('.auth-error').waitFor()
      const expectedError = mode === 'login' ? 'Incorrect username or password.' : 'Synthetic duplicate username.'
      require(await page.locator('.auth-error').innerText() === expectedError, `${mode}: server error`)
      require(await page.locator('.auth-error').getAttribute('role') === 'alert', `${mode}: announced error`)

      if (mode === 'login') tokenMode = 'network'
      else registerMode = 'network'
      await submit.click()
      const networkText = mode === 'login' ? 'Could not sign in. Check your connection and try again.' : 'Registration failed.'
      await page.getByRole('alert').filter({ hasText: networkText }).waitFor()

      if (mode === 'login') tokenMode = 'pending'
      else registerMode = 'pending'
      await submit.click()
      await page.waitForFunction(() => document.querySelector('.auth-form').getAttribute('aria-busy') === 'true')
      require(await submit.isDisabled() && await username.isDisabled() && await password.isDisabled(), `${mode}: busy fields`)
      require(await page.locator('.auth-password-toggle').isDisabled(), `${mode}: busy visibility`)
      const pendingCount = counts.token + counts.register
      await form.evaluate((element) => element.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })))
      require(counts.token + counts.register === pendingCount, `${mode}: duplicate submit`)
      require(await page.locator('.auth-error').count() === 0, `${mode}: stale error not cleared`)
      await page.screenshot({ path: `/home/almas/Desktop/courses/Courses_projects/.playwright-mcp/auth-v2-${mode}-loading.png`, fullPage: true })
      require(typeof release === 'function', `${mode}: mock pending request`)
      release()
      await page.locator('.auth-error').waitFor()
      await page.waitForFunction(() => !document.querySelector('.auth-submit').disabled)
      await page.screenshot({ path: `/home/almas/Desktop/courses/Courses_projects/.playwright-mcp/auth-v2-${mode}-error.png`, fullPage: true })

      tokenMode = 'ok'
      registerMode = 'ok'
      const beforeSuccess = { ...counts }
      await submit.click()
      await page.waitForURL('http://localhost:5173/')
      await page.locator('.signal-hero').waitFor()
      require(counts.token === beforeSuccess.token + 1, `${mode}: token login count`)
      if (mode === 'register') require(counts.register === beforeSuccess.register + 1, 'Register must create before auto-login')
      require(await page.evaluate(() => Boolean(localStorage.getItem('auth-session'))), `${mode}: session marker`)
      require(unexpected.length === 0 && errors.length === 0, `${mode}: unexpected request/runtime error`)
      passed.push(`${mode}: native validation, keyboard, visibility, errors, loading, duplicate guard, success redirect`)

      // Native cross-page anchors must remain correct when the async catalog grows.
      for (const failure of [false, true]) {
        await page.goto(`http://localhost:5173/${mode}`)
        coursesError = failure
        courses = Array.from({ length: 4 }, (_, index) => ({
          id: 991000 + index, slug: `anchor-fixture-${index}`, title: `Synthetic course ${index}`,
          description: 'Synthetic course material for layout testing. '.repeat(12), author: 'Fixture',
          direction: { slug: 'fixture', name: 'Fixture' }, level: 'beginner', review_count: 0, average_rating: null,
        }))
        coursesGate = new Promise((resolve) => { releaseCourses = resolve })
        await page.locator('.studio-footer a[href="/#learning-workflow"]').click()
        await page.waitForFunction(() => document.querySelector('#course-library')?.getAttribute('aria-busy') === 'true')
        releaseCourses()
        await page.waitForFunction(() => {
          const target = document.getElementById('learning-workflow')
          const header = document.querySelector('.site-header')
          return document.querySelector('#course-library')?.getAttribute('aria-busy') === 'false'
            && target.getBoundingClientRect().top >= header.getBoundingClientRect().bottom
            && target.getBoundingClientRect().top < innerHeight
        })
      }
      require(unexpected.length === 0 && errors.length === 0, `${mode}: anchor runtime error`)
      passed.push(`${mode}: workflow anchor after delayed catalog success and error`)
    } finally {
      release?.()
      releaseCourses?.()
      await context.close()
    }
  }
  return { passed, realAuthRequests: 0, realDatabaseWrites: 0 }
}
