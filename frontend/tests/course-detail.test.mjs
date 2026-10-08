import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createServer } from 'vite'

let server
let CourseCurriculum
let CourseEnrollment
const translations = new Map()
const modules = [
  { id: 7, title: 'First module', order: 10, lessons: [
    { id: 31, title: 'First lesson', order: 1, text_content: 'Protected body must never be rendered' },
    { id: 32, title: 'Second lesson', order: 2 },
  ] },
  { id: 8, title: 'Second module', order: 20, lessons: [{ id: 33, title: 'Third lesson', order: 1 }] },
]

before(async () => {
  // Compile the real JSX with the already installed Vite; no DOM package or API calls.
  server = await createServer({
    server: { middlewareMode: true, hmr: false, ws: false },
    optimizeDeps: { noDiscovery: true, include: [] }, appType: 'custom',
  })
  CourseCurriculum = (await server.ssrLoadModule('/src/components/CourseCurriculum.jsx')).default
  CourseEnrollment = (await server.ssrLoadModule('/src/components/CourseEnrollment.jsx')).default
  for (const language of ['en', 'ru', 'kk']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    const instance = createInstance()
    await instance.init({ lng: language, resources: { [language]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    translations.set(language, instance)
  }
})

after(async () => { await server?.close() })

function render(Component, props, language = 'en') {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: translations.get(language) },
    createElement(MemoryRouter, null, createElement(Component, props)),
  ))
}

test('first module is expanded and other panels are inert and hidden from assistive technology', () => {
  const html = render(CourseCurriculum, { modules })
  assert.equal((html.match(/aria-expanded="true"/g) || []).length, 1)
  assert.equal((html.match(/aria-expanded="false"/g) || []).length, 1)
  assert.match(html, /aria-hidden="true" inert=""/)
  assert.match(html, /aria-controls="[^"]+-panel"/)
  assert.ok(html.indexOf('First module') < html.indexOf('Second module'))
  assert.match(html, />10<\/span>/)
  assert.match(html, />20<\/span>/)
})

test('public curriculum displays lesson titles and locks without links or protected bodies', () => {
  const html = render(CourseCurriculum, { modules })
  assert.match(html, /First lesson/)
  assert.match(html, /Second lesson/)
  assert.match(html, /Course access required/)
  assert.doesNotMatch(html, /href="\/lessons\//)
  assert.doesNotMatch(html, /Protected body must never be rendered/)
})

test('confirmed course access enables lesson navigation without rendering lesson bodies', () => {
  const html = render(CourseCurriculum, { modules, canAccessLessons: true })
  for (const id of [31, 32, 33]) assert.match(html, new RegExp(`href="/lessons/${id}"`))
  assert.doesNotMatch(html, /curriculum-lesson-locked/)
  assert.doesNotMatch(html, /Protected body must never be rendered/)
})

test('module descriptions are optional and empty courses have a usable fallback', () => {
  const description = render(CourseCurriculum, { modules: [{ ...modules[0], description: 'Existing module description' }] })
  assert.match(description, /Existing module description/)
  const empty = render(CourseCurriculum, { modules: [] })
  assert.match(empty, /The curriculum will appear here/)
  assert.doesNotMatch(empty, /curriculum-module-toggle|Expand all|Collapse all/)
  const noLessons = render(CourseCurriculum, { modules: [{ ...modules[0], lessons: [] }] })
  assert.match(noLessons, /0 lessons/)
  assert.match(noLessons, /Lessons have not been added/)
})

for (const language of ['en', 'ru', 'kk']) {
  test(`curriculum controls and lesson counts use ${language} translations`, () => {
    const instance = translations.get(language)
    const html = render(CourseCurriculum, { modules }, language)
    assert.ok(html.includes(instance.t('courseOverview.expandAll')))
    assert.ok(html.includes(instance.t('courseOverview.lessonCount', { count: 2 })))
    assert.ok(html.includes(instance.t('courseOverview.lockedLesson')))
    assert.doesNotMatch(html, /courseOverview\./)
  })

  test(`existing anonymous enrollment state keeps its login link in ${language}`, () => {
    const course = { slug: 'test', title: 'Existing title', enrollment_mode: 'approval', modules }
    const html = render(CourseEnrollment, { course, authed: false, onEnrollmentChange: () => {} }, language)
    assert.match(html, /href="\/login"/)
    assert.doesNotMatch(html, /<form|<textarea/)
    assert.doesNotMatch(html, /enrollment\.[a-zA-Z]/)
  })
}

test('existing enrollment component waits for confirmed access before displaying an action', () => {
  const html = render(CourseEnrollment, {
    course: { slug: 'test', enrollment_mode: 'approval', modules }, authed: true, onEnrollmentChange: () => {},
  })
  assert.match(html, /role="status"/)
  assert.match(html, /Loading/)
  assert.doesNotMatch(html, /<button|<form|href="\/lessons\//)
})

test('open enrollment keeps the existing anonymous sign-in behavior', () => {
  const html = render(CourseEnrollment, {
    course: { slug: 'test', enrollment_mode: 'open', modules }, authed: false, onEnrollmentChange: () => {},
  })
  assert.match(html, /href="\/login"/)
  assert.match(html, /to start the course/)
})

test('module and lesson counts have correct Russian plural forms', () => {
  const instance = translations.get('ru')
  for (const [count, expected] of [[0, '0 модулей'], [1, '1 модуль'], [2, '2 модуля'], [5, '5 модулей']]) {
    assert.equal(instance.t('courseOverview.moduleCount', { count }), expected)
  }
  assert.equal(instance.t('courseOverview.lessonCount', { count: 21 }), '21 урок')
})
