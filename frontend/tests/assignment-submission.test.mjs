import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
import { formatSubmissionTimestamps } from '../src/utils/assignmentSubmissionDates.js'

let server, AssignmentSubmission
const dictionaries = new Map()
before(async () => {
  server = await createTestServer()
  AssignmentSubmission = (await server.ssrLoadModule('/src/components/learning/AssignmentSubmission.jsx')).default
  for (const language of ['ru', 'kk', 'en']) {
    const dict = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    const instance = createInstance()
    await instance.init({ lng: language, resources: { [language]: { translation: dict } } })
    dictionaries.set(language, instance)
  }
})
after(async () => server?.close())

function render(language, preview = false) {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: dictionaries.get(language) },
    createElement(AssignmentSubmission, { assignment: { id: 77, type: 'text', description: 'Fixture assignment instructions' }, preview })))
}

test('assignment preview keeps instructions visible and clearly read-only in all locales', () => {
  for (const language of ['ru', 'kk', 'en']) {
    const html = render(language, true)
    assert.match(html, /Fixture assignment instructions/)
    assert.ok(html.includes(dictionaries.get(language).t('assignmentSubmission.preview')))
    assert.doesNotMatch(html, /<form|Bearer|\/media\/|legacy-file/)
  }
})

test('student workflow is multipart, uses protected download APIs, and enforces visible upload limits', async () => {
  const source = await readFile(new URL('../src/components/learning/AssignmentSubmission.jsx', import.meta.url), 'utf8')
  assert.match(source, /new FormData\(\)/)
  assert.match(source, /body\.append\('files', file\)/)
  assert.match(source, /\/files\/\$\{attachment\.id\}\//)
  assert.match(source, /MAX_FILES|files\.length \+ selected\.length > 5/)
  assert.match(source, /VIDEO_FILE = 50 \* 1024 \* 1024/)
  assert.match(source, /TOTAL = 100 \* 1024 \* 1024/)
  assert.doesNotMatch(source, /\.file\.url|window\.location.*media/)
})

test('student assignment translations and reviewer reopen controls exist for RU, KK, EN', async () => {
  for (const language of ['ru', 'kk', 'en']) {
    const dict = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    for (const key of ['title', 'history', 'feedback', 'filesLabel', 'fileRules', 'submit', 'locked', 'accessError', 'submittedAt', 'reviewedAt']) {
      assert.ok(dict.assignmentSubmission[key], `${language}.${key}`)
    }
    assert.ok(dict.instructorStudio.assignmentReview.reopen)
  }
})

test('submission date is shown without inventing a review date while review is pending', () => {
  const dates = formatSubmissionTimestamps({ submitted_at: '2026-11-10T09:15:00Z', reviewed_at: null }, 'ru')
  assert.ok(dates.submittedAt)
  assert.equal(dates.submittedAt.dateTime, '2026-11-10T09:15:00.000Z')
  assert.equal(dates.reviewedAt, null)
})

test('reviewed submission formats its own submission and review timestamps', () => {
  const dates = formatSubmissionTimestamps({
    submitted_at: '2026-11-10T09:15:00Z',
    reviewed_at: '2026-11-11T12:45:00+00:00',
  }, 'en')
  assert.equal(dates.submittedAt.dateTime, '2026-11-10T09:15:00.000Z')
  assert.equal(dates.reviewedAt.dateTime, '2026-11-11T12:45:00.000Z')
  assert.ok(dates.submittedAt.label)
  assert.ok(dates.reviewedAt.label)
})

test('each revision formats its own timestamps rather than sharing the latest revision dates', () => {
  const versions = [
    { submitted_at: '2026-10-01T08:00:00Z', reviewed_at: '2026-10-02T08:00:00Z' },
    { submitted_at: '2026-10-05T08:00:00Z', reviewed_at: null },
  ].map(version => formatSubmissionTimestamps(version, 'en'))
  assert.equal(versions[0].submittedAt.dateTime, '2026-10-01T08:00:00.000Z')
  assert.equal(versions[0].reviewedAt.dateTime, '2026-10-02T08:00:00.000Z')
  assert.equal(versions[1].submittedAt.dateTime, '2026-10-05T08:00:00.000Z')
  assert.equal(versions[1].reviewedAt, null)
})

test('missing and malformed timestamps are omitted safely', () => {
  assert.deepEqual(formatSubmissionTimestamps({}, 'en'), { submittedAt: null, reviewedAt: null })
  const reviewOnly = formatSubmissionTimestamps({ reviewed_at: '2026-11-11T12:45:00Z' }, 'en')
  assert.equal(reviewOnly.submittedAt, null)
  assert.ok(reviewOnly.reviewedAt)
  assert.deepEqual(formatSubmissionTimestamps({ submitted_at: 'not-a-timestamp', reviewed_at: '2026-02-30T12:00:00Z' }, 'en'), {
    submittedAt: null,
    reviewedAt: null,
  })
})

test('date labels and timestamp formatting follow RU, KK and EN localization', async () => {
  const labels = []
  const dates = []
  for (const language of ['ru', 'kk', 'en']) {
    const dict = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    labels.push(dict.assignmentSubmission.submittedAt, dict.assignmentSubmission.reviewedAt)
    dates.push(formatSubmissionTimestamps({ submitted_at: '2026-11-10T09:15:00Z' }, language).submittedAt.label)
  }
  assert.equal(new Set(labels).size, 6)
  assert.ok(dates.every(Boolean))
  assert.equal(new Set(dates).size, 3)

  const component = await readFile(new URL('../src/components/learning/AssignmentSubmission.jsx', import.meta.url), 'utf8')
  assert.match(component, /formatSubmissionTimestamps\(item, i18n\.resolvedLanguage\)/)
  assert.match(component, /dates\.submittedAt &&/)
  assert.match(component, /dates\.reviewedAt &&/)
})
