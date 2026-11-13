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
test('only an explicitly reopenable current generic approval exposes the reopen action', () => {
  const html = render({ ...pending, status: 'approved', can_reopen: true })
  assert.ok(html.includes(instances.get('en').t('instructorStudio.assignmentReview.reopen')))
  assert.doesNotMatch(render({ ...pending, status: 'approved', is_structured: true, can_reopen: false }), /Reopen for a new revision/)
})

const completeRubric = { completeness: 0, application: 12, quality: 25, documentation: 20 }
test('rubric parser accepts integer boundaries and numeric input strings without changing scores', async () => {
  const { validateRubricScores } = await import('../src/utils/instructorStudio.js')
  assert.deepEqual(validateRubricScores(completeRubric), { scores: completeRubric, invalid: [] })
  assert.deepEqual(validateRubricScores({ ...completeRubric, quality: '25' }).scores, completeRubric)
})
test('rubric parser rejects fractional, negative, excessive, empty, missing and non-numeric values without rounding', async () => {
  const { validateRubricScores } = await import('../src/utils/instructorStudio.js')
  for (const value of [12.5, '12.5', -1, '-1', 26, '26', '', ' ', null, undefined, NaN, Infinity, true, 'invalid']) {
    const raw = { ...completeRubric, quality: value }
    assert.deepEqual(validateRubricScores(raw), { scores: null, invalid: ['quality'] })
    assert.ok(Object.is(raw.quality, value), 'validation must not mutate the entered score')
  }
})
test('rubric renders required integer constraints and localized associated errors in all locales', () => {
  for (const language of ['ru', 'kk', 'en']) {
    const fixture = { ...pending, assignment_learning_activity: 'final_media_project', rubric_scores: completeRubric }
    const valid = render(fixture, 99, language)
    assert.equal((valid.match(/type="number"/g) || []).length, 4)
    assert.equal((valid.match(/step="1"/g) || []).length, 4)
    assert.equal((valid.match(/min="0" max="25"/g) || []).length, 4)
    assert.doesNotMatch(valid, /aria-invalid="true"/)
    for (const value of ['12.5', '-1', '26', '']) {
      const invalid = render({ ...fixture, rubric_scores: { ...completeRubric, quality: value } }, 99, language)
      const message = instances.get(language).t('instructorStudio.assignmentReview.rubricScoreError')
      assert.notEqual(message, 'instructorStudio.assignmentReview.rubricScoreError')
      assert.ok(invalid.includes(message))
      assert.match(invalid, /aria-invalid="true" aria-describedby="([^"]+)-quality-error"/)
      assert.match(invalid, /id="[^"]+-quality-error" class="instructor-error" role="alert"/)
      assert.ok(!invalid.includes(instances.get(language).t('instructorStudio.assignmentReview.rubricTotal', { total: 57 })))
    }
  }
})
test('server rubric validation remains readable through the existing action error formatter', async () => {
  const { studioError } = await import('../src/utils/instructorStudio.js')
  const message = 'Each rubric score must be an integer from 0 to 25.'
  assert.equal(studioError({ response: { status: 400, data: { rubric_scores: [message] } } }, 'Save failed'), `rubric_scores: ${message}`)
})
