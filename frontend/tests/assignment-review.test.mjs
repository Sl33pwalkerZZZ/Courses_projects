import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
let server, SubmissionCard
const instances = new Map()
before(async () => {
  server = await createTestServer()
  SubmissionCard = (await server.ssrLoadModule('/src/pages/instructor/Submissions.jsx')).SubmissionCard
  for (const language of ['ru', 'kk', 'en']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    const instance = createInstance()
    await instance.init({ lng: language, resources: { [language]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    instances.set(language, instance)
  }
})
after(async () => { await server?.close() })
const pending = { id: 4, revision: 3, student: { id: 5, username: 'Fixture learner' }, lesson_title: 'Practical work', course_id: 8, course_title: 'Fixture course', status: 'pending', submitted_at: '2026-10-23T10:00:00Z', payload: { tasks: [{ task: 'Fixture answer' }] }, assignment_description: 'Source instructions', can_review: true }
function render(submission, viewerId = 99, language = 'en') {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: instances.get(language) }, createElement(MemoryRouter, null, createElement(SubmissionCard, { submission, viewerId }))))
}
test('pending review shows structured answer, course link, feedback and decisions in all locales', () => {
  for (const language of ['ru', 'kk', 'en']) {
    const html = render(pending, 99, language)
    assert.match(html, /Fixture learner/)
    assert.match(html, /Fixture answer/)
    const labeled = render({ ...pending, payload: { working_task: 'Preserved student prose', data_classification: 'internal' } }, 99, language)
    assert.ok(labeled.includes(instances.get(language).t('selectionMap.fields.working_task')))
    assert.ok(labeled.includes(instances.get(language).t('selectionMap.classification.internal')))
    assert.ok(labeled.includes('Preserved student prose'))
    assert.match(html, /\/instructor\/courses\/8\/submissions/)
    assert.match(html, /<textarea/)
    assert.equal((html.match(/<button/g) || []).length, 2)
    assert.doesNotMatch(html, /instructorStudio\.assignmentReview\./)
  }
})
test('self-review and server-denied review have no approval controls', () => {
  for (const html of [render(pending, 5), render({ ...pending, can_review: false })]) {
    assert.doesNotMatch(html, /<textarea|<button/)
    assert.match(html, /Fixture answer/)
  }
})
test('completed review is immutable in UI and identifies evidence and feedback', () => {
  const html = render({ ...pending, status: 'approved', reviewer_comment: 'Good work', reviewer_username: 'Fixture educator', reviewed_at: '2026-10-23T12:00:00Z', review_is_verifiable: true })
  assert.match(html, /Good work/)
  assert.match(html, /Fixture educator/)
  assert.match(html, /verifiable review evidence/)
  assert.doesNotMatch(html, /<textarea|<button/)
  assert.match(render({ ...pending, status: 'approved', review_is_verifiable: false }), /Historical status/)
})
