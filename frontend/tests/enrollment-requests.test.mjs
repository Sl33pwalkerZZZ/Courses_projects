import assert from 'node:assert/strict'
import { before, after, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
let server, Card, Navigation
before(async () => {
  server = await createTestServer()
  Card = (await server.ssrLoadModule('/src/pages/instructor/EnrollmentRequests.jsx')).EnrollmentRequestCard
  Navigation = (await server.ssrLoadModule('/src/components/instructor/StudioNavigation.jsx')).default
})
after(async () => server?.close())
for (const language of ['ru', 'kk', 'en']) {
  test(`request history and pending actions render accessibly in ${language}`, async () => {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    const i18n = createInstance()
    await i18n.init({ lng: language, resources: { [language]: { translation: dictionary } } })
    const request = { id: 123, student: { id: 4, username: '<student>' }, course: { id: 8, title: 'Fixture course' }, created_at: '2026-10-21T09:00:00Z', message: '<script>unsafe</script>' }
    const render = (status, busy = false) => renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(Card, { request: { ...request, status, admin_note: 'Reason', reviewed_at: status === 'pending' ? null : request.created_at }, busy, onDecision() {} })))
    const pending = render('pending')
    assert.match(pending, /Fixture course/)
    assert.match(pending, /&lt;student&gt;/)
    assert.match(pending, /&lt;script&gt;unsafe/)
    assert.match(pending, /<label for="[^"]+"/)
    assert.equal((pending.match(/<button/g) || []).length, 2)
    assert.ok(pending.includes(i18n.t('instructorStudio.enrollmentRequests.approve')))
    assert.ok(pending.includes(i18n.t('instructorStudio.enrollmentRequests.reject')))
    assert.doesNotMatch(pending, /instructorStudio\./)
    assert.equal((render('pending', true).match(/disabled=""/g) || []).length, 3)
    for (const status of ['approved', 'rejected']) {
      const history = render(status)
      assert.doesNotMatch(history, /<button|<textarea/)
      assert.match(history, /Reason/)
      assert.ok(history.includes(i18n.t(`instructorStudio.enrollmentRequests.${status}`)))
    }
  })
}
test('review route and navigation use moderator access rather than author role', async () => {
  const app = await readFile(new URL('../src/App.jsx', import.meta.url), 'utf8')
  const dictionary = JSON.parse(await readFile(new URL('../src/i18n/locales/en.json', import.meta.url), 'utf8'))
  const i18n = createInstance()
  await i18n.init({ lng: 'en', resources: { en: { translation: dictionary } } })
  assert.match(app, /path="enrollment-requests" element={<StudioAccessGuard moderator><EnrollmentRequests/)
  for (const moderator of [false, true]) {
    const html = renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(MemoryRouter, null,
      createElement(Navigation, { identity: { is_moderator: moderator, can_manage_instructors: false } }))))
    assert.equal(html.includes('href="/instructor/enrollment-requests"'), moderator)
  }
})
