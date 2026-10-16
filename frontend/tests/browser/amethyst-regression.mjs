// Isolated Firefox regression fixture. Every API request is intercepted.
// Synthetic accounts/content exist only in this browser context, never in SQLite.
// Run with Playwright MCP browser_run_code_unsafe(filename=...).
// eslint-disable-next-line no-unused-expressions
async (initialPage) => {
  const browser = initialPage.context().browser()
  if (browser.browserType().name() !== 'firefox') throw new Error('Firefox is required')
  const base = 'http://localhost:5173'
  const directory = '/home/almas/Desktop/courses/Courses_projects/.playwright-mcp'
  const options = await initialPage.evaluate(() => window.__fullRebuildOptions || {})
  const widths = options.interactionsOnly ? [] : options.widths || [1440, 768, 375, 320]
  const languages = options.languages || ['en', 'ru', 'kk']
  const themes = options.themes || ['light', 'dark']
  const checks = [], screenshots = [], errors = [], unexpected = [], mutations = []
  const assert = (condition, message) => { if (!condition) throw new Error(message) }
  const course = {
    id: 990001, slug: 'digital-playground-fixture', title: 'Building useful AI workflows',
    description: 'Synthetic browser fixture. Explore a practical workflow, evaluate its output, and reflect on the result.\n\nThese records exist only in intercepted browser responses.',
    author: 'Fixture educator', level: 'beginner', enrollment_mode: 'approval',
    direction: { name: 'Applied AI', slug: 'applied-ai' }, average_rating: 4.5, review_count: 2,
    modules: [
      { id: 990011, order: 1, title: 'Explore and understand', description: 'A synthetic module preview.', lessons: [{ id: 990101, order: 1, title: 'Map a useful workflow' }, { id: 990102, order: 2, title: 'Evaluate the output' }] },
      { id: 990012, order: 2, title: 'Practice and reflect', description: 'A second preview.', lessons: [{ id: 990103, order: 1, title: 'Present the result' }] },
    ],
  }
  const other = { ...course, id: 990002, slug: 'automation-fixture', title: 'Automation for everyday work', level: 'intermediate', direction: { name: 'Automation', slug: 'automation' } }
  const quiz = { id: 990501, lesson_id: 990101, title: 'Check your understanding', instructions: 'Synthetic knowledge assessment.', passing_percentage: 70, questions: [
    { id: 990511, type: 'single', text: 'What should happen before using an AI result?', choices: [{ id: 990521, text: 'Evaluate the result' }, { id: 990522, text: 'Always trust the output' }] },
    { id: 990512, type: 'multiple', text: 'Choose the useful review steps.', choices: [{ id: 990523, text: 'Check the sources' }, { id: 990524, text: 'Check the context' }, { id: 990525, text: 'Skip all verification' }] },
  ] }
  const end = new Date().toISOString().slice(0, 10)
  const start = new Date(Date.parse(`${end}T00:00:00Z`) - 364 * 86400000).toISOString().slice(0, 10)
  const previous = new Date(Date.parse(`${end}T00:00:00Z`) - 86400000).toISOString().slice(0, 10)
  const activity = { timezone: 'UTC', start_date: start, end_date: end, total_completed_lessons: 3, active_days_last_365: 2, current_streak_days: 2, daily_counts: [{ date: previous, count: 1 }, { date: end, count: 2 }] }
  const token = (account, type) => `fixture.${btoa(JSON.stringify({ user_id: account, token_type: type, exp: Math.floor(Date.now() / 1000) + 3600 })).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_')}.fixture`
  const routes = [
    ['home', '/'], ['course', `/courses/${course.slug}`], ['lesson', '/lessons/990101'],
    ['profile', '/profile'], ['login', '/login'], ['register', '/register'], ['not-found', '/missing-fixture-page'],
  ]
  async function environment({ width = 1440, language = 'en', theme = 'light', reducedMotion = 'reduce' } = {}) {
    let enrolled = true, status = 'pending', completed = false, courseError = 0, completionError = false, quizError = false, failQuiz = false, attempt = null, review = null
    const context = await browser.newContext({ viewport: { width, height: 1000 }, reducedMotion })
    await context.addInitScript(({ language, theme, access, refresh }) => {
      localStorage.setItem('ai-courses-language', language); localStorage.setItem('ai-courses-theme', theme)
      localStorage.setItem('access', access); localStorage.setItem('refresh', refresh); localStorage.setItem('auth-session', 'fixture-account-a')
    }, { language, theme, access: token(990901, 'access'), refresh: token(990901, 'refresh') })
    const headers = { 'access-control-allow-origin': '*', 'access-control-allow-headers': 'authorization, content-type', 'access-control-allow-methods': 'GET, HEAD, POST, PATCH, DELETE, OPTIONS' }
    await context.route('**/api/**', async (route) => {
      const request = route.request(), path = new URL(request.url()).pathname, method = request.method()
      const json = (body, code = 200) => route.fulfill({ status: code, headers, contentType: 'application/json', body: JSON.stringify(body) })
      if (method === 'OPTIONS') return route.fulfill({ status: 204, headers })
      const enrollment = { id: 990201, course, total_lessons: 3, completed_lessons: completed ? 2 : 1, progress_percent: completed ? 66.7 : 33.3, is_completed: false, next_lesson_id: completed ? 990103 : 990101, next_lesson_title: completed ? 'Present the result' : 'Map a useful workflow', completed_lesson_ids: completed ? [990101, 990102] : [990102] }
      if (!['GET', 'HEAD'].includes(method)) {
        mutations.push({ path, method, intercepted: true })
        if (path.endsWith('/complete/') && method === 'POST') { if (completionError) return json({ detail: 'Fixture completion failure' }, 500); completed = true; return json({ lesson_id: 990101, completed_at: `${end}T10:00:00Z` }) }
        if (path.endsWith('/quiz/attempts/') && method === 'POST') {
          if (quizError) return json({ detail: 'Fixture quiz failure' }, 500)
          const payload = request.postDataJSON()
          attempt = { id: 990601, quiz_id: quiz.id, submission_id: payload.submission_id, score: failQuiz ? 50 : 100, passed: !failQuiz, question_count: 2, correct_count: failQuiz ? 1 : 2, passing_percentage: 70, submitted_at: `${end}T10:30:00Z`, answers: quiz.questions.map((q, i) => ({ question_id: q.id, type: q.type, text: q.text, choices: q.choices, is_correct: !failQuiz || i === 0, explanation: 'Server-authorized synthetic feedback.', selected_choice_ids: payload.answers.find((a) => a.question_id === q.id).choice_ids, correct_choice_ids: i ? [990523, 990524] : [990521] })) }
          return json(attempt, 201)
        }
        if (path.endsWith('/enrollment-requests/') && method === 'POST') { status = 'pending'; return json({ id: 990301, status, course, message: request.postDataJSON().message, created_at: `${end}T09:00:00Z` }, 201) }
        if (path.endsWith('/enroll/') && method === 'POST') { enrolled = true; return json(enrollment, 201) }
        if (path.endsWith('/reviews/') && method === 'POST') { review = { id: 990401, ...request.postDataJSON(), author: 'Fixture learner A', created_at: `${end}T09:00:00Z`, status: 'pending' }; return json(review, 201) }
        if (path === '/api/reviews/990401/' && method === 'PATCH') { review = { ...review, ...request.postDataJSON(), status: 'pending' }; return json(review) }
        if (path === '/api/reviews/990401/' && method === 'DELETE') { review = null; return route.fulfill({ status: 204, headers }) }
        unexpected.push(`${method} ${path}`); return json({ detail: 'Unrecognized synthetic mutation blocked' }, 405)
      }
      if (path === '/api/courses/') return json([course, other])
      if (path === `/api/courses/${course.slug}/`) return courseError ? json({ detail: 'Synthetic course error' }, courseError) : json(course)
      if (path === '/api/auth/me/') return json({ id: 990901, username: 'Fixture learner A', email: 'learner@example.invalid', role: 'student' })
      if (path === '/api/my/enrollments/') return json(enrolled ? [enrollment] : [])
      if (path === '/api/my/enrollment-requests/') return json(status === 'none' ? [] : [{ id: 990301, course, status, admin_note: status === 'rejected' ? 'Synthetic reviewer explanation' : '', created_at: `${end}T09:00:00Z` }])
      if (path === `/api/courses/${course.slug}/reviews/`) return json({ average_rating: 4.5, review_count: 2, my_review: review, reviews: [{ id: 990411, rating: 5, text: 'Clear explanations and useful practice.', author: 'Fixture reviewer', created_at: `${end}T09:00:00Z` }, { id: 990412, rating: 4, text: 'A helpful introduction.', author: 'Another fixture reviewer', created_at: `${end}T09:00:00Z` }] })
      if (path === '/api/my/activity/') return json(activity)
      if (path === '/api/lessons/990101/') return json({ id: 990101, order: 1, title: 'Map a useful workflow', course_slug: course.slug, text_content: 'Begin with a task you understand. Describe the input, the decision, and the output.\n\nEvaluate the response against the original goal. Check sources and context before using the result.\n\nReflect on the workflow and record what you would improve next time.', completed_at: completed ? `${end}T10:00:00Z` : null, images: [{ id: 990701, image: '/api/lesson-images/990701/', order: 1, alt_text: { en: 'An input, review and output workflow', ru: 'Схема: входные данные, проверка и результат', kk: 'Кіріс, тексеру және нәтиже сызбасы' } }], assignments: [{ id: 990801, description: 'Map one workflow and identify a step that needs human review.' }] })
      if (path === '/api/lesson-images/990701/') { assert(Boolean(request.headers().authorization), 'Protected image missing JWT'); return route.fulfill({ status: 200, headers, contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg" width="700" height="160" viewBox="0 0 700 160"><rect width="700" height="160" fill="#182338"/><path d="M100 80H600" stroke="#84b7ff" stroke-width="2"/><g fill="#51d6c5"><circle cx="100" cy="80" r="18"/><circle cx="350" cy="80" r="18"/><circle cx="600" cy="80" r="18"/></g></svg>' }) }
      if (path === '/api/lessons/990101/quiz/') return json({ quiz })
      if (path === '/api/lessons/990101/quiz/attempts/') return json({ count: attempt ? 1 : 0, next: null, previous: null, results: attempt ? [attempt] : [], latest: attempt, best: attempt })
      if (path === '/api/quiz-attempts/990601/') return json(attempt)
      unexpected.push(`${method} ${path}`); return json({ detail: 'Unrecognized synthetic API blocked' }, 404)
    })
    const page = await context.newPage()
    page.on('pageerror', (error) => errors.push(error.message))
    return { context, page, set: (values) => { if ('enrolled' in values) enrolled = values.enrolled; if ('status' in values) status = values.status; if ('courseError' in values) courseError = values.courseError; if ('completionError' in values) completionError = values.completionError; if ('quizError' in values) quizError = values.quizError; if ('failQuiz' in values) failQuiz = values.failQuiz } }
  }
  // Full responsive + locale + theme matrix; screenshots cover every route/width/theme in EN.
  for (const width of widths) {
    for (const language of languages) {
      for (const theme of themes) {
        const { context, page } = await environment({ width, language, theme })
        try {
          for (const [name, path] of routes) {
            await page.goto(base + path)
            await page.locator('main h1').waitFor()
            if (name === 'profile') await page.locator('.activity-day').first().waitFor()
            if (name === 'lesson') await page.locator('.quiz-choice').first().waitFor()
            await page.waitForFunction(() => ![...document.querySelectorAll('main [aria-busy="true"]')].length)
            const state = await page.evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth, language: document.documentElement.lang, theme: document.documentElement.dataset.theme, heading: getComputedStyle(document.querySelector('main h1')).fontFamily }))
            assert(state.scroll <= width + 1, `Overflow ${name}/${width}/${language}/${theme}: ${state.scroll}`)
            assert(state.language === language && state.theme === theme, 'Preference mismatch')
            assert(!/serif/i.test(state.heading.replace(/sans-serif/gi, '')), 'Legacy serif heading')
            if (language === 'en') {
              const toggle = async () => {
                if (width < 360) {
                  await page.locator('.header-menu-toggle').click()
                  await page.locator('.header-menu .theme-toggle').click()
                  await page.keyboard.press('Escape')
                } else await page.locator('.header-preferences .theme-toggle').click()
              }
              await toggle()
              await page.waitForFunction((expected) => document.documentElement.dataset.theme === expected, theme === 'light' ? 'dark' : 'light')
              await toggle()
              await page.waitForFunction((expected) => document.documentElement.dataset.theme === expected, theme)
            }
            checks.push(`${name}/${width}/${language}/${theme}`)
            if (language === 'en') { const shot = `${directory}/amethyst-${name}-${width}-${theme}.png`; await page.screenshot({ path: shot, fullPage: true }); screenshots.push(shot) }
          }
        } finally { await context.close() }
      }
    }
  }
  assert(!errors.length, `React errors: ${errors.join(', ')}`)
  assert(!unexpected.length, `Unrecognized API: ${unexpected.join(', ')}`)
  if (options.skipInteractions) return { matrixCases: checks.length, checks, screenshots, errors, unexpected, realApiRequests: 0 }
  // Focus, selection, confirmed completion, errors, retry, and account isolation.
  const { context, page, set } = await environment({ reducedMotion: 'no-preference' })
  try {
    await page.goto(base + '/lessons/990101')
    await page.locator('.quiz-choice').first().waitFor()
    assert(await page.locator('.play-celebration').count() === 0, 'Premature celebration')
    assert(!await page.locator('.lesson-quiz').innerText().then((text) => text.includes('Server-authorized')), 'Leaked quiz answer')
    await page.locator('.quiz-choice input').first().focus()
    await page.keyboard.press('ArrowDown')
    assert(await page.locator('.quiz-choice input').nth(1).isChecked(), 'Native radio arrow selection failed')
    await page.keyboard.press('Tab')
    assert(await page.locator('.quiz-step-actions button').nth(1).evaluate((button) => document.activeElement === button), 'Motion label introduced an extra tab stop')
    await page.locator('.quiz-choice input').first().check()
    await page.locator('.quiz-step-actions button').nth(1).click()
    await page.waitForFunction(() => document.activeElement?.tagName === 'LEGEND')
    await page.locator('.quiz-choice input').nth(0).focus(); await page.keyboard.press('Space')
    await page.keyboard.press('Tab'); await page.keyboard.press('Space')
    assert(await page.locator('.quiz-choice input').nth(0).isChecked() && await page.locator('.quiz-choice input').nth(1).isChecked(), 'Native checkbox keyboard selection failed')
    await page.locator('.quiz-actions > button').click()
    await page.locator('.quiz-confirmation').waitFor()
    set({ quizError: true }); await page.locator('.quiz-confirmation button[type="submit"]').click()
    await page.locator('.quiz-error').first().waitFor()
    assert(await page.locator('.quiz-results').count() === 0, 'Failed submission showed results')
    set({ quizError: false }); await page.locator('.quiz-confirmation button[type="submit"]').click()
    await page.locator('.quiz-score-card.is-passed').waitFor()
    await page.locator('.quiz-attempt-list button').first().waitFor()
    await page.waitForFunction(() => document.activeElement?.matches('.quiz-score-card h3'))
    assert(!(await page.locator('.lesson-complete-button').isDisabled()), 'Quiz incorrectly completed lesson')
    await page.screenshot({ path: `${directory}/amethyst-quiz-passed.png`, fullPage: true })
    await page.locator('.quiz-results > button').click()
    await page.locator('.quiz-choice input').first().check(); await page.locator('.quiz-step-actions button').nth(1).click()
    await page.locator('.quiz-choice input').first().check(); await page.locator('.quiz-actions > button').click()
    set({ failQuiz: true }); await page.locator('.quiz-confirmation button[type="submit"]').click()
    await page.locator('.quiz-score-card:not(.is-passed)').waitFor()
    assert(await page.locator('.quiz-score-card .play-celebration').count() === 0, 'Fail celebrated')
    await page.screenshot({ path: `${directory}/amethyst-quiz-retry.png`, fullPage: true })
    set({ completionError: true }); await page.locator('.lesson-complete-button').click()
    await page.locator('.lesson-completion .error').waitFor()
    assert(await page.locator('.lesson-completed-badge').count() === 0, 'Failed completion showed completed')
    set({ completionError: false }); await page.locator('.lesson-complete-button').click()
    await page.locator('.lesson-completed-badge').waitFor(); await page.reload(); await page.locator('.lesson-completed-badge').waitFor()
    checks.push('quiz selection/focus/submit failure/pass/fail/retry; independent completion/error/reload')
    set({ enrolled: false, status: 'none' }); await page.goto(base + `/courses/${course.slug}`)
    await page.locator('.course-enrollment button.btn-primary').click(); await page.waitForFunction(() => document.activeElement?.tagName === 'TEXTAREA')
    await page.locator('.enrollment-form button[type="button"]').click(); await page.waitForFunction(() => document.activeElement?.matches('.course-enrollment button.btn-primary'))
    await page.locator('.course-enrollment button.btn-primary').click()
    await page.locator('.enrollment-form textarea').fill('I want to practice evaluating useful AI workflows.')
    await page.locator('.enrollment-form button[type="submit"]').click()
    await page.locator('.enrollment-success').waitFor()
    await page.reload(); await page.locator('.course-enrollment .enrollment-status').waitFor()
    assert(await page.locator('.enrollment-form').count() === 0, 'Pending application still editable')
    checks.push('application open/cancel keyboard focus; synthetic application submit/reload')
    for (const status of ['pending', 'rejected', 'approved']) {
      set({ status }); await page.reload(); await page.waitForFunction(() => !document.querySelector('.course-enrollment[aria-busy="true"]'))
      await page.screenshot({ path: `${directory}/amethyst-enrollment-${status}.png`, fullPage: true })
    }
    set({ enrolled: true }); await page.reload(); await page.locator('.review-form').waitFor()
    await page.locator('.review-rating-choice').nth(4).click()
    await page.locator('.review-form textarea').fill('A synthetic review to verify moderation and owner actions.')
    await page.locator('.review-form button[type="submit"]').click()
    await page.locator('.reviews-own').waitFor()
    assert(!(await page.locator('.reviews-list').innerText()).includes('A synthetic review'), 'Pending review became public')
    await page.locator('.review-edit-button').click(); await page.locator('.review-form textarea').fill('An edited synthetic review remains pending.')
    await page.locator('.review-form button[type="submit"]').click(); await page.locator('.reviews-own').waitFor()
    await page.locator('.review-delete-button').click(); await page.locator('.review-delete-dialog[open]').waitFor()
    await page.locator('.review-dialog-actions button').last().click(); await page.locator('.review-form').waitFor()
    checks.push('synthetic review create/pending/edit/delete with native dialog')
    set({ courseError: 500 }); await page.reload(); await page.locator('.course-overview-state button').waitFor(); set({ courseError: 0 }); await page.locator('.course-overview-state button').click(); await page.locator('#course-overview-title').waitFor()
    set({ courseError: 404 }); await page.reload(); await page.locator('.course-overview-state h1').waitFor(); assert(await page.locator('.course-overview-state button').count() === 0, '404 retry misclassified')
    set({ courseError: 0, enrolled: true }); await page.goto(base + '/profile'); await page.locator('.profile-username').waitFor()
    await page.evaluate(() => { localStorage.removeItem('access'); localStorage.removeItem('refresh'); localStorage.setItem('auth-session', 'fixture-logout'); window.dispatchEvent(new StorageEvent('storage', { key: 'auth-session' })) })
    await page.waitForURL('**/login'); assert(await page.locator('.profile-username').count() === 0, 'Private state survived logout')
    checks.push('application states; genuine404/server retry; cross-tab logout removes profile')
  } finally { await context.close() }
  const recovery = await environment()
  try {
    let failImport = true
    await recovery.context.route('**/src/pages/Profile.jsx*', (route) => failImport ? route.abort('failed') : route.continue())
    await recovery.page.goto(base + '/profile')
    await recovery.page.locator('.play-global-state[role="alert"] h1').waitFor()
    failImport = false
    await recovery.page.locator('.play-global-state button').click()
    await recovery.page.locator('.profile-username').waitFor()
    checks.push('lazy import failure reaches translated error boundary; Retry reload recovers')
  } finally { await recovery.context.close() }
  assert(!errors.length, `React errors: ${errors.join(', ')}`)
  assert(!unexpected.length, `Unrecognized API: ${unexpected.join(', ')}`)
  return { matrixCases: widths.length * languages.length * themes.length * routes.length, checks, screenshots, errors, unexpected, syntheticMutations: mutations, realApiRequests: 0 }
}
