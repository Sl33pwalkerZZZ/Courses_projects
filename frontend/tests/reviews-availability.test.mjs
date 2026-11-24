import assert from 'node:assert/strict'
import { before, after, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
import { reviewLoadErrorKey } from '../src/utils/courseReviews.js'
let server, ReviewsLoadState
before(async () => {
  server = await createTestServer()
  ;({ ReviewsLoadState } = await server.ssrLoadModule('/src/components/CourseReviews.jsx'))
})
after(async () => { await server?.close() })
async function render(error, language = 'ru') {
  const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
  const i18n = createInstance()
  await i18n.init({ lng: language, resources: { [language]: { translation: dictionary } } })
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(MemoryRouter, null,
    createElement(ReviewsLoadState, { error, onRetry() {}, disabled: false }))))
}
test('published-only endpoint 404 is unavailable; auth, server and network failures stay errors', () => {
  assert.equal(reviewLoadErrorKey({ response: { status: 404 } }), 'reviews.unavailable')
  assert.equal(reviewLoadErrorKey({ response: { status: 401 } }), 'reviews.sessionExpired')
  for (const status of [403, 429, 500, 503]) assert.equal(reviewLoadErrorKey({ response: { status } }), 'reviews.loadError')
  assert.equal(reviewLoadErrorKey({}), 'reviews.loadError')
})
for (const language of ['ru', 'kk', 'en']) test(`unavailable is neutral and translated in ${language}`, async () => {
  const html = await render('reviews.unavailable', language)
  assert.match(html, /role="status"/)
  assert.doesNotMatch(html, /role="alert"|<button|<form|href=|reviews\.unavailable/)
  assert.ok(html.includes({ ru: 'опубликованных', kk: 'жарияланған', en: 'published' }[language]))
})
test('network/server error retains retry; expired session retains login', async () => {
  assert.match(await render('reviews.loadError'), /role="alert"/)
  assert.match(await render('reviews.loadError'), /<button/)
  assert.match(await render('reviews.sessionExpired'), /href="\/login"/)
})
