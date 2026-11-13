import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
import course8Source from './fixtures/course8Source.json' with { type: 'json' }
import { lessonCourseErrorKey, lessonErrorKey, lessonNavigation, loadCourseOutline, loadEnrollmentProgress, loadLessonCourse, orderCurriculum, saveLessonCompletion } from '../src/utils/lessons.js'

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
test('real source integration renders one reading and preserves objectives and practice', () => {
  for (const id of [93, 94, 95, 96]) {
    const saved = structuredClone(course8Source[id])
    const lesson = { ...saved, learning_content: { content_language: 'ru', objectives: ['Keep learning objective'], interactions: saved.interactions },
      assignments: id === 96 ? [{ id: 1, learning_activity: 'ai_selection_map', description: saved.assignment_description }] : [] }
    const html = render(Material, { lesson })
    assert.ok(html.includes('Keep learning objective'))
    assert.doesNotMatch(html, /<h2>1\.[1-8]\./)
    assert.equal((html.match(/<table>/g) || []).length, id === 96 ? 0 : 1)
    if (id === 94) for (const item of saved.interactions[1].items) assert.equal(html.split(`href="${item.url}"`).length - 1, 1)
    if (id === 95) assert.equal((html.match(/class="course8-step-number"/g) || []).length, 5)
    if (id === 96) {
      assert.match(html, /lesson-practice-instructions/)
      assert.match(html, /lesson-practice-disclosure/)
      assert.ok(html.includes(translations.get('en').t('selectionMap.safety')))
      assert.ok(!html.includes(translations.get('en').t('learning.practiceReference')))
      assert.match(html, /разрешение на их использование|обезличенные образцы/)
      assert.match(html, /class="lesson-resources"/)
      assert.equal((html.match(/rel="noopener noreferrer"/g) || []).length, 7)
      for (const url of saved.text_content.match(/https?:\/\/\S+/gu)) assert.ok(html.includes(`href="${url}"`))
      assert.match(html, />OpenAI Academy — обучение работе с ChatGPT<\/a>/)
    }
  }
})
let server, Sidebar, Material, Status

before(async () => {
  server = await createTestServer()
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

test('outline and progress loaders read only their own endpoint and preserve backend completion IDs', async () => {
  const calls = []
  const client = { async get(path) {
    calls.push(path)
    return { data: path === '/my/enrollments/' ? [{ course: { slug: 'another' } }, enrollment] : course }
  } }
  const result = await loadCourseOutline(client, course.slug)
  assert.deepEqual(calls, ['/courses/existing-course/'])
  const progress = await loadEnrollmentProgress(client, course.slug)
  assert.equal(progress, enrollment)
  assert.deepEqual(progress.completed_lesson_ids, [11])
  assert.deepEqual(result.course.modules.map((module) => module.id), [1, 2])
  assert.deepEqual(calls.sort(), ['/courses/existing-course/', '/my/enrollments/'])
})

test('structured lesson contents renders one named on-page navigation', () => {
  const lesson = {
    title: 'Structured lesson',
    text_content: '1. First section\n\nFirst explanation.\n\n2. Second section\n\nSecond explanation.',
    learning_content: { content_language: 'ru', source_sections: ['1. First section', '2. Second section'], objectives: [], interactions: [] },
    images: [], assignments: [],
  }
  const html = render(Material, { lesson })
  assert.equal((html.match(/class="lesson-section-navigation"/g) || []).length, 1)
  assert.match(html, /1\. First section/)
  assert.match(html, /2\. Second section/)
})

test('missing enrollment never becomes a made-up student progress record', async () => {
  assert.equal(await loadEnrollmentProgress({ get: async () => ({ data: [] }) }, course.slug), null)
})

test('failed progress requests remain errors rather than zero-progress results', async () => {
  for (const status of [401, 403, 500]) {
    const error = failure(status)
    await assert.rejects(loadEnrollmentProgress({ get: async () => { throw error } }, course.slug), (caught) => caught === error)
  }
})

function courseLoader(client, preview = false) {
  const updates = { outline: [], progress: [] }
  const request = loadLessonCourse(client, course.slug, preview, {
    onOutline: state => updates.outline.push(state), onProgress: state => updates.progress.push(state),
  })
  return { ...request, updates }
}

for (const outlineFails of [false, true]) {
  for (const progressFails of [false, true]) {
    test(`independent outline/progress results: outline ${outlineFails ? 'fails' : 'succeeds'}, progress ${progressFails ? 'fails' : 'succeeds'}`, async () => {
      const error = failure(500)
      const loader = courseLoader({ get: async path => {
        const progress = path === '/my/enrollments/'
        if (progress ? progressFails : outlineFails) throw error
        return { data: progress ? [enrollment] : course }
      } })
      await loader.ready
      const outline = loader.updates.outline.at(-1), progress = loader.updates.progress.at(-1)
      assert.equal(outline.loading, false)
      assert.equal(progress.loading, false)
      assert.equal(outline.error, outlineFails ? error : null)
      assert.equal(progress.error, progressFails ? error : null)
      assert.equal(outline.data?.slug || null, outlineFails ? null : course.slug)
      assert.equal(progress.data, progressFails ? null : enrollment)
    })
  }
}

test('a slow progress request never delays publication of the real outline', async () => {
  let releaseProgress, outlineLoaded
  const pending = new Promise(resolve => { releaseProgress = resolve })
  const outlined = new Promise(resolve => { outlineLoaded = resolve })
  const states = []
  const request = loadLessonCourse({ get: async path => ({ data: path === '/my/enrollments/' ? await pending : course }) }, course.slug, false, {
    onOutline: state => { if (state.data) outlineLoaded(state) }, onProgress: state => states.push(state),
  })
  assert.equal((await outlined).data.slug, course.slug)
  assert.equal(states.at(-1).loading, true)
  assert.equal(states.at(-1).data, null)
  releaseProgress([enrollment])
  await request.ready
  assert.equal(states.at(-1).data, enrollment)
})

test('progress retry does not reload the curriculum, coalesces clicks, and retains confirmed progress on later failure', async () => {
  const calls = []
  let broken = true
  const loader = courseLoader({ get: async path => {
    calls.push(path)
    if (path === '/my/enrollments/' && broken) throw failure(500)
    return { data: path === '/my/enrollments/' ? [enrollment] : course }
  } })
  await loader.ready
  broken = false
  const retry = loader.refreshProgress()
  assert.equal(loader.refreshProgress(), retry)
  assert.equal(loader.updates.progress.at(-1).loading, true)
  await retry
  assert.equal(loader.updates.progress.at(-1).data, enrollment)
  broken = true
  await loader.refreshProgress()
  assert.equal(loader.updates.progress.at(-1).data, enrollment)
  assert.equal(loader.updates.progress.at(-1).error.response.status, 500)
  assert.equal(calls.filter(path => path === '/courses/existing-course/').length, 1)
  assert.equal(calls.filter(path => path === '/my/enrollments/').length, 3)
})

test('outline retry preserves independently loaded progress and only retries the outline', async () => {
  const calls = []
  let broken = true
  const loader = courseLoader({ get: async path => {
    calls.push(path)
    if (path !== '/my/enrollments/' && broken) throw failure(500)
    return { data: path === '/my/enrollments/' ? [enrollment] : course }
  } })
  await loader.ready
  broken = false
  const retry = loader.retryOutline()
  assert.equal(loader.retryOutline(), retry)
  await retry
  assert.equal(loader.updates.outline.at(-1).data.slug, course.slug)
  assert.equal(loader.updates.progress.at(-1).data, enrollment)
  assert.equal(calls.filter(path => path === '/my/enrollments/').length, 1)
  assert.equal(calls.length, 3)
})

test('disposed account A loaders cannot publish into account B state', async () => {
  let release
  const pending = new Promise(resolve => { release = resolve })
  const old = courseLoader({ get: async path => { await pending; return { data: path === '/my/enrollments/' ? [enrollment] : course } } })
  await Promise.resolve()
  old.dispose()
  const current = courseLoader({ get: async path => ({ data: path === '/my/enrollments/' ? [] : { ...course, title: 'Account B course' } }) })
  await current.ready
  release()
  await old.ready
  assert.equal(old.updates.outline.length, 1)
  assert.equal(old.updates.progress.length, 1)
  assert.equal(current.updates.outline.at(-1).data.title, 'Account B course')
  assert.equal(current.updates.progress.at(-1).data, null)
})

test('session cancellations do not publish empty results or error states', async () => {
  const loader = courseLoader({ get: async () => { throw { code: 'ERR_CANCELED' } } })
  await loader.ready
  assert.equal(loader.updates.outline.length, 1)
  assert.equal(loader.updates.progress.length, 1)
})

for (const status of [401, 403]) {
  test(`authorization failure ${status} stays an explicit error rather than an empty course`, async () => {
    const loader = courseLoader({ get: async () => { throw failure(status) } })
    await loader.ready
    for (const resource of ['outline', 'progress']) {
      const state = loader.updates[resource].at(-1)
      assert.equal(state.data, null)
      assert.equal(state.error.response.status, status)
      assert.equal(lessonCourseErrorKey(state.error, resource), `lessonWorkspace.${status === 401 ? 'signIn' : 'accessDenied'}`)
    }
  })
  test(`authorization failure ${status} on retry removes stale access data`, async () => {
    let denied = false
    const loader = courseLoader({ get: async path => {
      if (denied) throw failure(status)
      return { data: path === '/my/enrollments/' ? [enrollment] : course }
    } })
    await loader.ready
    denied = true
    await Promise.all([loader.retryOutline(), loader.refreshProgress()])
    assert.equal(loader.updates.outline.at(-1).data, null)
    assert.equal(loader.updates.progress.at(-1).data, null)
    assert.equal(loader.updates.progress.at(-1).error.response.status, status)
  })
}

test('instructor preview loads only its authorized outline and never queries learner progress', async () => {
  const calls = []
  const loader = courseLoader({ get: async path => { calls.push(path); return { data: course } } }, true)
  await loader.ready
  await loader.refreshProgress()
  assert.deepEqual(calls, ['/instructor/courses/existing-course/preview/'])
  assert.equal(loader.updates.progress.length, 0)
})

test('unpublished six-module curriculum is complete without enrollment progress in RU/KK/EN', async () => {
  let id = 0
  const draft = { ...course, is_published: false, modules: Array.from({ length: 6 }, (_, moduleIndex) => ({
    id: moduleIndex + 1, order: moduleIndex + 1, title: `Module ${moduleIndex + 1}`,
    lessons: Array.from({ length: moduleIndex === 5 ? 1 : 3 }, (_, lessonIndex) => ({ id: ++id, order: lessonIndex + 1, title: `Lesson ${id}` })),
  })).reverse() }
  const loader = courseLoader({ get: async path => {
    if (path === '/my/enrollments/') throw failure(500)
    return { data: draft }
  } })
  await loader.ready
  for (const language of ['ru', 'kk', 'en']) {
    const html = render(Sidebar, { course: loader.updates.outline.at(-1).data, lessonId: 1, progressError: failure(500) }, language)
    assert.equal((html.match(/class="lesson-outline-module"/g) || []).length, 6)
    assert.equal((html.match(/class="lesson-outline-link"/g) || []).length, 16)
    assert.ok(html.indexOf('Module 1') < html.indexOf('Module 6'))
    assert.doesNotMatch(html, /<progress|0%|is-completed|lucide-circle /)
    assert.ok(html.includes(translations.get(language).t('lessonWorkspace.progressError')))
    assert.ok(html.includes(translations.get(language).t('lessonWorkspace.progressUnknown')))
  }
})

test('outline failure preserves visible confirmed progress; both failures offer separate retries', () => {
  const progressHtml = render(Sidebar, { course: null, courseSlug: course.slug, outlineError: failure(500), enrollment })
  assert.match(progressHtml, /25%/)
  assert.doesNotMatch(progressHtml, /lesson-outline-modules/)
  const bothHtml = render(Sidebar, { course: null, courseSlug: course.slug, outlineError: failure(500), progressError: failure(500) })
  assert.equal((bothHtml.match(/<button/g) || []).length, 2)
  assert.doesNotMatch(bothHtml, /<progress|0%|lesson-outline-modules/)
  assert.ok(bothHtml.includes(translations.get('en').t('lessonWorkspace.outlineError')))
  assert.ok(bothHtml.includes(translations.get('en').t('lessonWorkspace.progressError')))
  assert.ok(bothHtml.includes(translations.get('en').t('lessonWorkspace.retryProgress')))
  assert.ok(bothHtml.includes(translations.get('en').t('lessonWorkspace.retryOutline')))
})

test('loading progress shows a loading state without invented progress or enrollment advice', () => {
  const html = render(Sidebar, { course, lessonId: 11, progressLoading: true })
  assert.match(html, /aria-busy="true"/)
  assert.doesNotMatch(html, /<progress|0%/)
  assert.ok(html.includes(translations.get('en').t('lessonWorkspace.updatingProgress')))
  assert.ok(!html.includes(translations.get('en').t('lessonWorkspace.previewOnly')))
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
  assert.ok(html.includes(translations.get('en').t('lessonWorkspace.progressError')))
  assert.ok(html.includes(translations.get('en').t('lessonWorkspace.progressLastConfirmed')))
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
  assert.doesNotMatch(html, /src="\/media\/lesson.png"|<img/)
  assert.match(html, /role="status"/)
  assert.match(html, /Existing assignment &lt;img/)
})

test('empty material is intentional and never filled with a placeholder lesson', () => {
  const html = render(Material, { lesson: { text_content: '  ', images: [], assignments: [] } })
  assert.match(html, /Lesson material has not been added yet/)
  assert.doesNotMatch(html, /lesson-material-text|lesson-material-images|lesson-material-assignments/)
})

for (const language of ['en', 'ru', 'kk']) {
  test(`structured practice keeps the source reference and uses translated controls in ${language}`, () => {
    const t = translations.get(language).t.bind(translations.get(language))
    assert.notEqual(t('common.cancel'), 'common.cancel')
    for (const key of ['practiceTransition', 'openPractice', 'practiceReference']) {
      assert.notEqual(t(`learning.${key}`), `learning.${key}`)
    }
    const lesson = {
      text_content: 'Source task\n\nПараметр | Ответ участника\nРабочая задача | \n\nWorked example\n\n1.8. Выводы по первой главе\n\nKeep conclusion\n\nМатериалы для дополнительного изучения\n\nhttps://example.org/',
      learning_content: { content_language: 'ru', objectives: ['Original objective'], interactions: [
        { type: 'model_service', title: 'Source template', headers: ['Параметр', 'Ответ участника'], rows: [['Рабочая задача', '']] },
      ] },
      assignments: [{ id: 1, learning_activity: 'ai_selection_map', description: 'Preserve safety. Поля сравнения и сохранение черновика — авторское цифровое развитие исходной карты.' }],
    }
    const html = render(Material, { lesson }, language)
    assert.ok(html.indexOf('Original objective') < html.indexOf('Source task'))
    assert.match(html, /Worked example/)
    assert.match(html, /Keep conclusion/)
    assert.match(html, /href="https:\/\/example.org\/"/)
    assert.match(html, /Preserve safety/)
    assert.doesNotMatch(html, /авторское цифровое развитие|learning\.(openPractice|practiceReference|practiceTransition)/)
    assert.match(html, /<details class="lesson-practice-disclosure"><summary>/)
    assert.equal((html.match(/<table>/g) || []).length, 1)
  })
  test(`private lesson images initially show translated loading without public or protected URLs in ${language}`, () => {
    const html = render(Material, { lesson: { images: [{ id: 15, image: '/api/lesson-images/15/' }] } }, language)
    assert.ok(html.includes(translations.get(language).t('common.loading')))
    assert.match(html, /role="status"/)
    assert.doesNotMatch(html, /<img|\/api\/lesson-images|\/media\/|Bearer/)
  })

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
