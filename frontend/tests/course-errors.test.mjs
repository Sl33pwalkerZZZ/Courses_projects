import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { after, before, test } from 'node:test'
import axios from 'axios'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createServer } from 'vite'
import { courseErrorKind, loadCourse } from '../src/utils/courseDetail.js'

let server
let CourseLoadError
const translations = new Map()

before(async () => {
  server = await createServer({
    server: { middlewareMode: true, hmr: false, ws: false },
    optimizeDeps: { noDiscovery: true, include: [] }, appType: 'custom',
  })
  CourseLoadError = (await server.ssrLoadModule('/src/pages/CourseDetail.jsx')).CourseLoadError
  for (const language of ['en', 'ru', 'kk']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    const instance = createInstance()
    await instance.init({ lng: language, resources: { [language]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    translations.set(language, instance)
  }
})

after(async () => { await server?.close() })

function renderError(kind, language) {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: translations.get(language) },
    createElement(MemoryRouter, null, createElement(CourseLoadError, { kind, onRetry() {} })),
  ))
}

test('only actual HTTP 404 failures are classified as missing courses', () => {
  assert.equal(courseErrorKind({ response: { status: 404 } }), 'notFound')
  for (const failure of [new Error('Offline'), { code: 'ECONNABORTED' }, ...[400, 401, 403, 429, 500, 502, 503].map((status) => ({ response: { status } }))]) {
    assert.equal(courseErrorKind(failure), 'loadError')
  }
  assert.equal(courseErrorKind(new axios.CanceledError('Session changed')), null)
})

for (const language of ['en', 'ru', 'kk']) {
  test(`404 keeps the translated catalog escape without a misleading retry in ${language}`, () => {
    const html = renderError('notFound', language)
    assert.ok(html.includes(translations.get(language).t('course.notFound')))
    assert.match(html, /role="alert"/)
    assert.match(html, /href="\/"/)
    assert.doesNotMatch(html, /<button|course\.[a-zA-Z]/)
  })

  test(`recoverable errors display translated explanation and Retry in ${language}`, () => {
    const html = renderError('loadError', language)
    const i18n = translations.get(language)
    for (const key of ['course.loadError', 'course.loadErrorDescription', 'common.retry']) {
      assert.ok(html.includes(i18n.t(key)))
    }
    assert.match(html, /<button type="button" class="btn-primary">/)
    assert.match(html, /href="\/"/)
    assert.ok(!html.includes(i18n.t('course.notFound')))
    assert.doesNotMatch(html, /course\.[a-zA-Z]/)
  })
}

test('retry sends a fresh course request and can recover from a server failure', async () => {
  const calls = [], loaded = [], errors = []
  const course = { id: 2, title: 'Existing course', modules: [] }
  const client = { async get(path, options) {
    calls.push({ path, options })
    if (calls.length === 1) throw { response: { status: 503 } }
    return { data: course }
  } }
  const first = loadCourse(client, 'course with spaces', (data) => loaded.push(data), (kind) => errors.push(kind))
  await first.promise
  assert.deepEqual(errors, ['loadError'])
  assert.deepEqual(loaded, [])
  first.dispose()
  const retry = loadCourse(client, 'course with spaces', (data) => loaded.push(data), (kind) => errors.push(kind))
  await retry.promise
  assert.equal(calls.length, 2)
  assert.equal(calls[1].path, '/courses/course%20with%20spaces/')
  assert.ok(calls[1].options.signal instanceof AbortSignal)
  assert.notEqual(calls[0].options.signal, calls[1].options.signal)
  assert.deepEqual(loaded, [course])
  retry.dispose()
})

test('unmount or route replacement aborts loading and discards late results', async () => {
  for (const lateFailure of [false, true]) {
    let resolve, reject, signal
    const results = []
    const request = loadCourse({ get(_path, options) {
      signal = options.signal
      return new Promise((done, fail) => { resolve = done; reject = fail })
    } }, 'old-course', (data) => results.push(data), (kind) => results.push(kind))
    request.dispose()
    assert.equal(signal.aborted, true)
    if (lateFailure) reject({ response: { status: 500 } })
    else resolve({ data: { title: 'Obsolete course' } })
    await request.promise
    assert.deepEqual(results, [])
  }
})

test('session cancellations never replace the page with an error', async () => {
  const results = []
  const request = loadCourse({ async get() { throw new axios.CanceledError('Session changed') } }, 'course',
    (data) => results.push(data), (kind) => results.push(kind))
  await request.promise
  assert.deepEqual(results, [])
  request.dispose()
})
