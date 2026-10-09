import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createServer } from 'vite'
import { lessonErrorKey, lessonNavigation, loadCourseOutline, loadEnrollmentProgress, orderCurriculum, saveLessonCompletion } from '../src/utils/lessons.js'

const modules = [
  { id: 2, title: 'Later module', order: 20, lessons: [
    { id: 22, title: 'Last lesson', order: 20 }, { id: 21, title: 'Third lesson', order: 10 },
  ] },
  { id: 1, title: 'First module', order: 10, lessons: [
    { id: 12, title: 'Second lesson', order: 20 }, { id: 11, title: 'First lesson', order: 10 },
  ] },
]
const course = { slug: 'existing-course', title: 'Existing course', modules }
const enrollment = { course, total_lessons: 4, completed_lessons: 1, progress_percent: 25, completed_lesson_ids: [11] }
const failure = (status) => ({ response: { status } })
const translations = new Map()
let server, Sidebar, Material, Status

before(async () => {
  server = await createServer({ server: { middlewareMode: true, hmr: false, ws: false }, optimizeDeps: { noDiscovery: true, include: [] }, appType: 'custom' })
  Sidebar = (await server.ssrLoadModule('/src/components/LessonCourseSidebar.jsx')).default
  const view = await server.ssrLoadModule('/src/pages/LessonView.jsx')
  Material = view.LessonMaterial
  Status = view.LessonWorkspaceStatus
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

test('curriculum is ordered by module, lesson, and ID without modifying API data', () => {
  const original = structuredClone(modules)
  const ordered = orderCurriculum(modules)
  assert.deepEqual(ordered.map((module) => module.id), [1, 2])
  assert.deepEqual(ordered.flatMap((module) => module.lessons.map((lesson) => lesson.id)), [11, 12, 21, 22])
  assert.deepEqual(modules, original)
  const ties = orderCurriculum([{ ...modules[0], lessons: [
    { id: 30, order: 1 }, { id: 29, order: 1 },
  ] }])
  assert.deepEqual(ties[0].lessons.map((lesson) => lesson.id), [29, 30])
})

test('previous/next navigation crosses module boundaries in actual curriculum order', () => {
  const navigation = lessonNavigation(modules, '12')
  assert.equal(navigation.module.id, 1)
  assert.equal(navigation.lessonIndex, 1)
  assert.equal(navigation.previous.id, 11)
  assert.equal(navigation.next.id, 21)
  assert.equal(lessonNavigation(modules, 21).previous.id, 12)
})

test('first, last, missing, and empty lessons have safe navigation boundaries', () => {
  assert.equal(lessonNavigation(modules, 11).previous, null)
  assert.equal(lessonNavigation(modules, 22).next, null)
  assert.equal(lessonNavigation(modules, 999), null)
  assert.equal(lessonNavigation([], 11), null)
  assert.equal(lessonNavigation(modules, 'invalid'), null)
})

test('outline restores only the current course enrollment and backend completion IDs', async () => {
  const calls = []
  const client = { async get(path) {
    calls.push(path)
    return { data: path === '/my/enrollments/' ? [{ course: { slug: 'another' } }, enrollment] : course }
  } }
  const result = await loadCourseOutline(client, course.slug)
  assert.equal(result.enrollment, enrollment)
  assert.deepEqual(result.enrollment.completed_lesson_ids, [11])
  assert.deepEqual(result.course.modules.map((module) => module.id), [1, 2])
  assert.deepEqual(calls.sort(), ['/courses/existing-course/', '/my/enrollments/'])
})

test('missing enrollment never becomes a made-up student progress record', async () => {
  assert.equal(await loadEnrollmentProgress({ get: async () => ({ data: [] }) }, course.slug), null)
})

test('failed progress requests remain errors rather than zero-progress results', async () => {
  for (const status of [401, 403, 500]) {
    const error = failure(status)
    await assert.rejects(loadCourseOutline({ get: async () => { throw error } }, course.slug), (caught) => caught === error)
  }
})

test('completion uses the existing endpoint and requires confirmation for the requested lesson', async () => {
  const completedAt = '2026-10-09T08:00:00Z'
  let endpoint
  assert.equal(await saveLessonCompletion({ post: async (path) => {
    endpoint = path
    return { data: { lesson_id: 11, completed_at: completedAt } }
  } }, '11'), completedAt)
  assert.equal(endpoint, '/lessons/11/complete/')
  for (const data of [{}, { lesson_id: 11, completed_at: null }, { lesson_id: 12, completed_at: completedAt }, { lesson_id: 11, completed_at: 'invalid' }]) {
    await assert.rejects(saveLessonCompletion({ post: async () => ({ data }) }, 11), /not confirmed/)
  }
})

test('unauthorized or failed completion cannot produce a completion timestamp', async () => {
  for (const status of [401, 403, 500]) {
    const error = failure(status)
    await assert.rejects(saveLessonCompletion({ post: async () => { throw error } }, 11), (caught) => caught === error)
  }
})

test('access and missing-lesson errors have distinct UI messages', () => {
  for (const [status, key] of [[401, 'signIn'], [403, 'accessDenied'], [404, 'notFound'], [500, 'loadError']]) {
    assert.equal(lessonErrorKey(failure(status)), `lessonWorkspace.${key}`)
  }
  assert.equal(lessonErrorKey(new Error('Offline')), 'lessonWorkspace.loadError')
})

test('sidebar highlights only the current lesson, restores completion indicators, and opens its module', () => {
  const html = render(Sidebar, { course, lessonId: 21, completedIds: [11], enrollment })
  assert.equal((html.match(/aria-current="page"/g) || []).length, 1)
  const currentLink = html.match(/<a[^>]*aria-current="page"[^>]*>/)[0]
  assert.match(currentLink, /href="\/lessons\/21"/)
  assert.equal((html.match(/lesson-outline-link is-completed/g) || []).length, 1)
  assert.match(html, /Completed lesson/)
  assert.match(html, /25%/)
  assert.ok(html.indexOf('First module') < html.indexOf('Later module'))
  assert.match(html, /aria-hidden="true" inert=""/)
  assert.equal((html.match(/aria-expanded="true"/g) || []).length, 1)
})

test('staff preview without enrollment shows no invented progress', () => {
  const html = render(Sidebar, { course, lessonId: 21 })
  assert.doesNotMatch(html, /<progress|is-completed/)
  assert.match(html, /Enrollment is required to save learning progress/)
})

test('progress refresh errors offer retry and keep the last confirmed summary', () => {
  const html = render(Sidebar, { course, lessonId: 21, enrollment, progressError: true, onRefresh: () => {} })
  assert.match(html, /25%/)
  assert.match(html, /role="alert"/)
  assert.match(html, /could not be refreshed/)
  assert.ok(html.includes(translations.get('en').t('common.retry')))
})

test('lesson material escapes HTML and preserves stored text, images, and assignment descriptions', () => {
  const html = render(Material, { lesson: {
    text_content: 'First paragraph\n\n<script>alert("unsafe")</script>',
    images: [{ id: 1, image: '/media/lesson.png' }],
    assignments: [{ id: 2, description: 'Existing assignment <img onerror="unsafe">' }],
  } })
  assert.match(html, /First paragraph/)
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /<script|onerror="unsafe"/)
  assert.match(html, /src="\/media\/lesson.png"/)
  assert.match(html, /Existing assignment &lt;img/)
})

test('empty material is intentional and never filled with a placeholder lesson', () => {
  const html = render(Material, { lesson: { text_content: '  ', images: [], assignments: [] } })
  assert.match(html, /Lesson material has not been added yet/)
  assert.doesNotMatch(html, /lesson-material-text|lesson-material-images|lesson-material-assignments/)
})

for (const language of ['en', 'ru', 'kk']) {
  test(`workspace outline and access errors are translated in ${language}`, () => {
    const instance = translations.get(language)
    const html = render(Sidebar, { course, lessonId: 21, completedIds: [11], enrollment }, language)
    assert.ok(html.includes(instance.t('lessonWorkspace.outline')))
    assert.ok(html.includes(instance.t('lessonWorkspace.completedLesson')))
    for (const key of ['signIn', 'accessDenied', 'notFound', 'loadError']) {
      const error = render(Status, { error: `lessonWorkspace.${key}`, courseSlug: course.slug, onRetry: () => {} }, language)
      assert.match(error, /role="alert"/)
      assert.match(error, /href="\/courses\/existing-course"/)
      assert.doesNotMatch(error, /lesson-reading-area|lesson-material|lessonWorkspace\./)
      if (key === 'signIn') assert.match(error, /href="\/login"/)
    }
  })
}
