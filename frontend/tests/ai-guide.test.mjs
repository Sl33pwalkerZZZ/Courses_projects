import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
import { AI_GUIDE_QUESTION_LIMIT, createGuideRequest, guideErrorKey } from '../src/utils/aiGuide.js'

let server, AIGuide
before(async () => {
  server = await createTestServer()
  AIGuide = (await server.ssrLoadModule('/src/components/learning/AIGuide.jsx')).default
})
after(async () => server?.close())

for (const language of ['ru', 'kk', 'en']) test(`AI Guide has localized accessible controls in ${language}`, async () => {
  const dict = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
  const i18n = createInstance()
  await i18n.init({ lng: language, resources: { [language]: { translation: dict } } })
  const render = initialOpen => renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(AIGuide, { lessonId: 113, initialOpen })))
  const closed = render(false)
  assert.match(closed, /aria-expanded="false"/)
  assert.doesNotMatch(closed, /<form/)
  const open = render(true)
  assert.match(open, /role="log"/)
  assert.match(open, /maxLength="1000"/)
  for (const key of ['title', 'question', 'send', 'clear', 'description', 'empty']) assert.ok(open.includes(dict.aiGuide[key]))
  assert.doesNotMatch(open, /Bearer|GROQ_API_KEY|aiGuide\./)
})

test('guide sends only question, language and lesson ID, never client lesson/context or credentials', async () => {
  const calls = []
  const client = { post: async (...args) => { calls.push(args); return { data: { answer: '<script>safe plain text</script>' } } } }
  const request = createGuideRequest(client, { lessonId: 113, question: ' Explain ', language: 'kk', getGeneration: () => 3 })
  assert.equal(await request.result, '<script>safe plain text</script>')
  assert.equal(calls[0][0], '/ai-guide/')
  assert.deepEqual(calls[0][1], { lesson_id: 113, question: 'Explain', language: 'kk' })
  assert.ok(calls[0][2].signal instanceof AbortSignal)
})

test('delayed account A answer cannot enter account B session', async () => {
  let generation = 1, resolve
  const request = createGuideRequest({ post: () => new Promise(done => { resolve = done }) }, { lessonId: 113, question: 'Question', getGeneration: () => generation })
  generation = 2
  resolve({ data: { answer: 'Private previous-session answer' } })
  await assert.rejects(request.result, { name: 'AbortError' })
})

test('clearing or unmounting cancels and discards even an abort-ignoring delayed response', async () => {
  let resolve, signal
  const request = createGuideRequest({ post: (...args) => { signal = args[2].signal; return new Promise(done => { resolve = done }) } }, { lessonId: 113, question: 'Question', getGeneration: () => 1 })
  request.cancel()
  assert.equal(signal.aborted, true)
  resolve({ data: { answer: 'Discard me' } })
  await assert.rejects(request.result, { name: 'AbortError' })
})

test('blank/oversized questions do not issue requests and empty provider answers fail safely', async () => {
  let calls = 0
  const client = { post: async () => { calls++; return { data: { answer: ' ' } } } }
  for (const question of [' ', 'a'.repeat(AI_GUIDE_QUESTION_LIMIT + 1)]) assert.throws(() => createGuideRequest(client, { lessonId: 113, question, getGeneration: () => 1 }))
  assert.equal(calls, 0)
  const request = createGuideRequest(client, { lessonId: 113, question: 'Valid', getGeneration: () => 1 })
  await assert.rejects(request.result, /Empty answer/)
})

test('access, rate limit, unavailable and network failures have distinct localized keys', () => {
  for (const status of [401, 403, 404]) assert.equal(guideErrorKey({ response: { status } }), 'aiGuide.accessError')
  assert.equal(guideErrorKey({ response: { status: 429 } }), 'aiGuide.rateLimit')
  assert.equal(guideErrorKey({ response: { status: 503 } }), 'aiGuide.unavailable')
  assert.equal(guideErrorKey(new Error('offline')), 'aiGuide.error')
})

test('lesson/session owns reset without duplicate sibling keys and answers use safe plain React text', async () => {
  const source = await readFile(new URL('../src/components/learning/AIGuide.jsx', import.meta.url), 'utf8')
  const lesson = await readFile(new URL('../src/pages/LessonView.jsx', import.meta.url), 'utf8')
  assert.match(lesson, /<AIGuide lessonId=\{lesson.id\}/)
  assert.doesNotMatch(lesson, /<AIGuide key=\{lesson.id\}/)
  assert.match(lesson, /<LessonWorkspace key=\{`\$\{id\}:\$\{session.generation\}:\$\{preview\}`\}/)
  assert.match(source, /request.current\?\.cancel\(\)/)
  assert.match(source, /getAuthSession\(\)\.generation/)
  assert.doesNotMatch(source, /dangerouslySetInnerHTML|localStorage|sessionStorage/)
})
