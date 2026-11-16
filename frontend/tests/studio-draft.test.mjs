import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
import { lessonDraft, draftPayload, draftEqual, savedDraft, guardStudioNavigation } from '../src/utils/studioDraft.js'

const lesson = { id: 501, title: 'Fixture lesson A', text_content: 'Saved body', learning_content: { content_language: 'ru', source_sections: ['Heading'], objectives: ['Goal'], interactions: [] } }
let server, ResourceState
before(async () => {
  server = await createTestServer()
  ResourceState = (await server.ssrLoadModule('/src/components/instructor/StudioShared.jsx')).ResourceState
})
after(async () => { await server?.close() })

test('refresh fixture keeps editor content with current outline/media, including refresh failure and retry', () => {
  const draft = lessonDraft(lesson)
  draft.text_content = 'Unsaved text'
  let retries = 0
  const resource = { data: { title: 'Renamed module', attachments: ['new.wav'] }, loading: true, refreshing: true, reload: () => retries++ }
  const children = data => createElement('section', { 'data-editor': lesson.id }, `${draft.text_content}|${data.title}|${data.attachments.join(',')}`)
  let html = renderToStaticMarkup(createElement(ResourceState, { resource }, children))
  assert.match(html, /Unsaved text\|Renamed module\|new.wav/)
  assert.match(html, /role="status"/)
  html = renderToStaticMarkup(createElement(ResourceState, { resource: { ...resource, loading: false, refreshing: false, error: 'Refresh failed' } }, children))
  assert.match(html, /Unsaved text/)
  assert.match(html, /role="alert"/)
  assert.match(html, /Refresh failed/)
  assert.equal(retries, 0)
  // Initial load has no stale editor to display; initial failure remains retryable.
  html = renderToStaticMarkup(createElement(ResourceState, { resource: { loading: true, data: null } }, children))
  assert.doesNotMatch(html, /data-editor/)
  html = renderToStaticMarkup(createElement(ResourceState, { resource: { data: null, error: 'Initial failure', reload() {} } }, children))
  assert.match(html, /Initial failure/)
  assert.doesNotMatch(html, /data-editor/)
})

test('save baseline uses submitted version, not edits typed while PATCH was pending', async () => {
  const initial = lessonDraft(lesson)
  const submitted = { ...initial, text_content: 'Submitted body' }
  let resolve
  const pending = new Promise(done => { resolve = done })
  const newer = { ...submitted, text_content: 'Newer unsaved body' }
  const completion = pending.then(response => savedDraft(newer, submitted, response, 'ru'))
  resolve({ ...lesson, text_content: 'Submitted body' })
  const result = await completion
  assert.equal(result.form.text_content, 'Newer unsaved body')
  assert.equal(result.baseline.text_content, 'Submitted body')
  assert.equal(draftEqual(result.form, result.baseline), false)
  assert.equal(draftEqual(savedDraft(submitted, submitted, { ...lesson, text_content: 'Submitted body' }, 'ru').form, submitted), true)
  assert.equal(draftEqual(initial, lessonDraft(lesson)), true)
  assert.equal(lessonDraft({ ...lesson, id: 502, title: 'B', text_content: 'B body' }).text_content, 'B body')
})

test('raw objective edits made during save survive normalization and remain dirty', () => {
  const submitted = lessonDraft(lesson)
  const current = { ...submitted, learning_content: { ...submitted.learning_content, objectives: ['Goal', ''] } }
  const result = savedDraft(current, submitted, lesson, 'ru')
  assert.deepEqual(result.form.learning_content.objectives, ['Goal', ''])
  assert.equal(draftEqual(result.form, result.baseline), false)
})

test('failed request cannot acknowledge the draft; later successful save becomes clean', async () => {
  const initial = lessonDraft(lesson)
  let state = { form: { ...initial, text_content: 'Keep after failure' }, baseline: initial }
  await assert.rejects(Promise.reject(new Error('Save failed')).then(response => {
    state = savedDraft(state.form, draftPayload(state.form), response, 'ru')
  }), /Save failed/)
  assert.equal(state.form.text_content, 'Keep after failure')
  assert.equal(draftEqual(state.form, state.baseline), false)
  state = savedDraft(state.form, draftPayload(state.form), { ...lesson, text_content: state.form.text_content }, 'ru')
  assert.equal(draftEqual(state.form, state.baseline), true)
})

function navigationFixture() {
  const handlers = new Map(), calls = [], win = {
    history: { state: { idx: 2 }, go: delta => calls.push(['restore', delta]) },
    addEventListener(name, callback, capture) { handlers.set(name, { callback, capture }) },
    removeEventListener(name) { handlers.delete(name) },
  }
  const navigator = {
    push(path) { calls.push(['push', path]); win.history.state.idx++ },
    replace(path) { calls.push(['replace', path]) },
    go(delta) { calls.push(['go', delta]) },
  }
  return { win, navigator, calls, handlers, pop(idx) {
    win.history.state = { idx }
    let stopped = false
    handlers.get('popstate').callback({ stopImmediatePropagation() { stopped = true } })
    return stopped
  } }
}
test('route stay preserves destination and state; discard continues once; clean navigation needs no confirm', () => {
  const fixture = navigationFixture()
  let dirty = true, answer = false, confirmations = 0
  const originalPush = fixture.navigator.push
  const dispose = guardStudioNavigation(fixture.navigator, fixture.win, () => {
    if (!dirty) return true
    confirmations++; return answer
  })
  fixture.navigator.push('/lesson-b')
  assert.deepEqual(fixture.calls, [])
  answer = true
  fixture.navigator.push('/lesson-b')
  assert.deepEqual(fixture.calls, [['push', '/lesson-b']])
  dirty = false
  fixture.navigator.replace('/elsewhere')
  assert.equal(confirmations, 2)
  dispose()
  assert.equal(fixture.navigator.push, originalPush)
  assert.equal(fixture.handlers.size, 1) // bootstrap listener is inert without an editor
  assert.equal(fixture.pop(0), false)
})
test('browser Back stay is suppressed and rolled back; discard permits intended POP without double prompt', () => {
  const fixture = navigationFixture()
  let answer = false, confirmations = 0
  const dispose = guardStudioNavigation(fixture.navigator, fixture.win, () => { confirmations++; return answer })
  assert.equal(fixture.handlers.get('popstate').capture, true)
  assert.equal(fixture.pop(1), true)
  assert.deepEqual(fixture.calls, [['restore', 1]])
  assert.equal(fixture.pop(2), true)
  assert.equal(confirmations, 1)
  answer = true
  fixture.navigator.go(-1)
  assert.equal(fixture.pop(1), false)
  assert.equal(confirmations, 2)
  dispose()
})
test('dirty prompt and refreshing status exist and render in RU/KK/EN', async () => {
  for (const language of ['ru', 'kk', 'en']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    assert.ok(dictionary.instructorStudio.discardLessonChanges.trim())
    const i18n = createInstance()
    await i18n.init({ lng: language, resources: { [language]: { translation: dictionary } } })
    const html = renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(ResourceState, { resource: { data: {}, loading: true, refreshing: true } }, () => createElement('span', null, 'draft'))))
    assert.ok(html.includes(dictionary.instructorStudio.refreshingWorkspace))
  }
})
