import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter, Routes, Route, Outlet } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
import { moveStudioItem, prepareLearningContent, publicationProblems, quizProblems, studioError, teachingEntryChange } from '../src/utils/instructorStudio.js'

let server, EducationalSections, QuizEditor, Curriculum
const translations = new Map()
before(async () => {
  server = await createTestServer()
  EducationalSections = (await server.ssrLoadModule('/src/components/instructor/EducationalSections.jsx')).default
  QuizEditor = (await server.ssrLoadModule('/src/pages/instructor/Assessment.jsx')).QuizEditor
  Curriculum = (await server.ssrLoadModule('/src/pages/instructor/Curriculum.jsx')).default
  for (const language of ['en', 'ru', 'kk']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    const i18n = createInstance()
    await i18n.init({ lng: language, resources: { [language]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    translations.set(language, i18n)
  }
})
after(async () => { await server?.close() })
function render(component, props, language) {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: translations.get(language) }, createElement(MemoryRouter, null, createElement(component, props))))
}
test('reordering preserves all sibling IDs without mutating input', () => {
  const list = [{ id: 3 }, { id: 5 }, { id: 6 }]
  assert.deepEqual(moveStudioItem(list, 1, -1).map(item => item.id), [5, 3, 6])
  assert.deepEqual(moveStudioItem(list, 0, -1), list)
  assert.deepEqual(list.map(item => item.id), [3, 5, 6])
})
test('teaching edits preserve source fields and metadata; blank objective lines are omitted', () => {
  for (const key of ['text', 'description', 'body']) {
    const source = { title: 'Original', [key]: 'Source', url: 'https://example.org', examples: ['Keep'] }
    assert.deepEqual(teachingEntryChange(source, 'Edited'), { ...source, [key]: 'Edited' })
    assert.equal(source[key], 'Source')
  }
  assert.equal(teachingEntryChange('Original', 'Edited'), 'Edited')
  const source = { source_sections: ['1.2'], objectives: [' First ', '', '  ', 'Second'], interactions: [] }
  assert.deepEqual(prepareLearningContent(source), { ...source, objectives: ['First', 'Second'] })
  assert.equal(source.objectives.length, 4)
})
test('publication errors localize actual DRF requirement leaves without internal field dumps', () => {
  const data = { requirements: [{ key: 'lesson_content', label: 'Every lesson', met: 'False' }, { key: 'assessment_reviewed', label: 'Review answers', met: 'False' }] }
  assert.equal(publicationProblems(data).length, 2)
  assert.equal(publicationProblems({ requirements: [{ key: 'ok', met: true }, { key: 'ok2', met: 'True' }] }).length, 0)
  const labels = { 'instructorStudio.requirements.lesson_content': 'Lesson incomplete', 'instructorStudio.requirements.assessment_reviewed': 'Review answers' }
  assert.equal(studioError({ response: { data } }, 'Error', key => labels[key]), 'Lesson incomplete · Review answers')
  assert.equal(studioError(new Error('Offline'), 'Retry'), 'Retry')
  assert.equal(studioError({ response: { data: { note: ['Explain rejection'] } } }, 'Error'), 'note: Explain rejection')
})
test('quiz validation rejects incomplete answer keys and accepts single/multiple questions', () => {
  const quiz = { title: 'Quiz', passing_percentage: 70, questions: [{ text: 'Which?', type: 'single', choices: [{ text: 'A', is_correct: true }, { text: 'B', is_correct: false }] }] }
  assert.deepEqual(quizProblems(quiz), [])
  quiz.questions[0].choices[1].is_correct = true
  assert.ok(quizProblems(quiz).includes('answers 1'))
  quiz.questions[0].type = 'multiple'
  assert.deepEqual(quizProblems(quiz), [])
  quiz.questions[0].choices.forEach(choice => { choice.is_correct = false })
  assert.ok(quizProblems(quiz).includes('answers 1'))
})
for (const language of ['en', 'ru', 'kk']) {
  test(`curriculum renders all six existing lessons in stored order with editing controls in ${language}`, () => {
    const lessons = [6, 3, 5, 2, 4, 1].map(order => ({ id: 90 + order, order, title: `Existing lesson ${order}` }))
    const course = { id: 8, is_published: false, modules: [{ id: 31, order: 1, title: 'Existing module', lessons }] }
    const html = renderToStaticMarkup(createElement(I18nextProvider, { i18n: translations.get(language) },
      createElement(MemoryRouter, { initialEntries: ['/curriculum'] }, createElement(Routes, null,
        createElement(Route, { element: createElement(Outlet, { context: { course, reload() {} } }) },
          createElement(Route, { path: '/curriculum', element: createElement(Curriculum) }))))))
    assert.equal((html.match(/aria-expanded="false"/g) || []).length, 6)
    let previous = -1
    for (let order = 1; order <= 6; order++) {
      const position = html.indexOf(`Existing lesson ${order}`)
      assert.ok(position > previous, `Lesson ${order} must be visible and sorted`)
      previous = position
      assert.ok(html.includes(`class="instructor-lesson-order">${order}.</span>`))
      assert.ok(html.includes(`aria-controls="studio-lesson-${90 + order}"`))
      assert.ok(html.includes(`${translations.get(language).t('instructorStudio.up')}: Existing lesson ${order}`))
    }
    assert.ok(html.includes(translations.get(language).t('instructorStudio.editLesson')))
    assert.doesNotMatch(html, /instructorStudio\.[a-zA-Z]/)
    assert.deepEqual(lessons.map(lesson => lesson.order), [6, 3, 5, 2, 4, 1])
  })
  test(`teaching headings and source tables are editable in ${language}`, () => {
    const html = render(EducationalSections, { value: [{ type: 'service_overview', title: 'Overview', services: [{ name: 'Service', description: 'Source body', details: 'Details', examples: ['Example'], url: 'https://example.org' }] }, { type: 'model_service', title: 'Comparison', headers: ['Model', 'Service'], rows: [['A', 'B']] }], onChange() {} }, language)
    assert.match(html, /value="Service"/)
    assert.match(html, /Source body/)
    assert.ok(html.includes(translations.get(language).t('instructorStudio.itemTitle')))
    assert.ok(html.includes(translations.get(language).t('instructorStudio.tableRows')))
    assert.doesNotMatch(html, /instructorStudio\.[a-zA-Z]/)
  })
  test(`published quiz is inspectable but locked in ${language}`, () => {
    const html = render(QuizEditor, { lesson: 3, initial: { id: 7, title: 'Locked', is_published: true, questions: [] }, onSaved() {} }, language)
    assert.match(html, /<fieldset disabled=""/)
    assert.ok(html.includes(translations.get(language).t('instructorStudio.quizLocked')))
    assert.ok(html.includes(translations.get(language).t('instructorStudio.previewQuestions')))
  })
}
