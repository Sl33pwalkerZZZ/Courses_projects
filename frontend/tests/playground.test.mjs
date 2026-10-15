import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { before, after, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'

let server, NotFound, PageLoading, Ring, Pulse, Journey, Question, Results
const languages = new Map()
before(async () => {
  server = await createTestServer()
  ;({ NotFound, PageLoading } = await server.ssrLoadModule('/src/components/GlobalState.jsx'))
  Ring = (await server.ssrLoadModule('/src/components/playground/ProgressRing.jsx')).default
  Pulse = (await server.ssrLoadModule('/src/components/playground/ActivityPulse.jsx')).default
  Journey = (await server.ssrLoadModule('/src/components/playground/CourseJourney.jsx')).default
  Question = (await server.ssrLoadModule('/src/components/QuizQuestion.jsx')).default
  Results = (await server.ssrLoadModule('/src/components/QuizResults.jsx')).default
  for (const language of ['en', 'ru', 'kk']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    const i18n = createInstance()
    await i18n.init({ lng: language, resources: { [language]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    languages.set(language, i18n)
  }
})
after(async () => { await server?.close() })
function render(component, props, language = 'en') {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: languages.get(language) }, createElement(MemoryRouter, null, createElement(component, props))))
}
for (const language of ['en', 'ru', 'kk']) {
  test(`translated unknown routes and loading remain useful in ${language}`, () => {
    const html = render(NotFound, {}, language)
    assert.ok(html.includes(languages.get(language).t('playground.notFound')))
    assert.match(html, /href="\/"/)
    assert.doesNotMatch(html, /playground\.[a-z]|opacity:0/)
    assert.match(render(PageLoading, {}, language), /role="status" aria-busy="true"/)
  })
  test(`progress and activity reflect supplied data with localized text in ${language}`, () => {
    const ring = render(Ring, { value: 33.3, label: 'One of three lessons' }, language)
    assert.match(ring, /role="img" aria-label="One of three lessons"/)
    assert.ok(ring.includes(new Intl.NumberFormat(language, { style: 'percent', maximumFractionDigits: 1 }).format(.333)))
    const days = Array.from({ length: 30 }, (_, i) => ({ date: `2026-06-${String(i + 1).padStart(2, '0')}`, count: i < 2 ? 99 : i === 29 ? 2 : 0 }))
    const pulse = render(Pulse, { days }, language)
    assert.ok(pulse.includes(languages.get(language).t('playground.recentActivity', { count: 2 })))
    assert.equal((pulse.match(/<time /g) || []).length, 28)
    assert.doesNotMatch(pulse, /dateTime="2026-06-01"|dateTime="2026-06-02"/)
    assert.match(pulse, /<details><summary>/)
    assert.match(pulse, /dateTime="2026-06-30"/)
  })
}
test('course journey uses only actual public module metadata and native anchors', () => {
  const html = render(Journey, { modules: [{ id: 41, title: 'First <module>' }, { id: 42, title: 'Second module' }] })
  assert.match(html, /href="#course-module-41"/)
  assert.match(html, /href="#course-module-42"/)
  assert.ok(html.indexOf('First &lt;module&gt;') < html.indexOf('Second module'))
  assert.equal(render(Journey, { modules: [] }), '')
})
test('animated questions retain native single/multiple choices without answer metadata', () => {
  const question = { id: 1, type: 'single', text: 'Choose a step', choices: [{ id: 2, text: 'Review' }, { id: 3, text: 'Check' }] }
  const single = render(Question, { question, selected: [2], number: 1, total: 2 })
  assert.match(single, /<fieldset/)
  assert.equal((single.match(/type="radio"/g) || []).length, 2)
  assert.equal((single.match(/checked=""/g) || []).length, 1)
  // Motion's tap gesture must not introduce a second tab stop beside each input.
  assert.ok((single.match(/<label[^>]*>/g) || []).every((label) => !label.includes('tabindex="0"')))
  assert.doesNotMatch(single, /correct_choice_ids|explanation|is_correct/)
  const multiple = render(Question, { question: { ...question, type: 'multiple' }, selected: [2, 3], number: 2, total: 2 })
  assert.equal((multiple.match(/type="checkbox"/g) || []).length, 2)
  assert.equal((multiple.match(/checked=""/g) || []).length, 2)
})
test('failed server result offers retry and no success celebration', () => {
  const html = render(Results, { result: { passed: false, score: 50, correct_count: 1, question_count: 2, passing_percentage: 70, answers: [] } })
  assert.match(html, /role="status"/)
  assert.match(html, /50%/)
  assert.doesNotMatch(html, /play-celebration|is-passed/)
  assert.ok(html.includes(languages.get('en').t('quiz.tryAgain')))
})
