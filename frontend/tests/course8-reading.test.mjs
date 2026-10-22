import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { readFile } from 'node:fs/promises'
import { getCourse8Reading } from '../src/utils/course8Reading.js'
import source from './fixtures/course8Source.json' with { type: 'json' }
import metadata from '../src/utils/course8Source.json' with { type: 'json' }
import { createTestServer } from './helpers/vite.mjs'

let server, Reading
before(async () => {
  server = await createTestServer()
  Reading = (await server.ssrLoadModule('/src/components/learning/Course8Reading.jsx')).default
})
after(async () => { await server?.close() })
function lesson(id) {
  const saved = structuredClone(source[id])
  return { ...saved, learning_content: { interactions: saved.interactions } }
}
const render = id => renderToStaticMarkup(createElement(Reading, { lesson: lesson(id) }))
const occurrences = (text, needle) => text.split(needle).length - 1

test('public source guards contain fingerprints, never the protected educational snapshots', () => {
  for (const id of [93, 94, 95, 96]) {
    assert.match(metadata[id].text, /^\d+:[0-9a-f]{16}$/)
    assert.match(metadata[id].interactions, /^\d+:[0-9a-f]{16}$/)
    assert.equal(metadata[id].text_content, undefined)
    assert.equal(metadata[id].assignment_description, undefined)
  }
})

test('only verified source readings are reorganized; teacher edits safely fall back', () => {
  for (const id of [93, 94, 95]) {
    const original = lesson(id)
    const copy = structuredClone(original)
    assert.equal(getCourse8Reading(original).id, id)
    assert.deepEqual(original, copy)
    for (const change of [
      value => { value.id = 9 },
      value => { value.course_slug = 'another-course' },
      value => { value.text_content += '\nNew teacher explanation' },
      value => { value.learning_content.interactions.push({ type: 'new_source' }) },
      value => { value.learning_content.interactions[0].title = 'Teacher update' },
    ]) {
      const edited = structuredClone(original)
      change(edited)
      assert.equal(getCourse8Reading(edited), null)
    }
  }
  assert.equal(getCourse8Reading(lesson(96)), null)
})

test('model/service definitions, GPT example, all comparison facts and non-one-to-one relationship appear once', () => {
  const html = render(93)
  const plan = getCourse8Reading(lesson(93))
  assert.ok(html.includes(plan.definition))
  assert.ok(html.includes(plan.example))
  assert.ok(html.includes(plan.conclusion))
  assert.equal(occurrences(html, '<table>'), 1)
  for (const row of source[93].interactions[0].rows) for (const cell of row) assert.equal(occurrences(html, cell), 1)
  assert.match(html, /<strong>GPT → ChatGPT<\/strong>/)
  assert.doesNotMatch(html, /1\.3\.|<button|hidden=|opacity:/)
})

test('categories preserve all five source rows; each service description and official link appears once', () => {
  const html = render(94)
  for (const row of source[94].interactions[0].rows) for (const cell of row) assert.ok(html.includes(cell))
  assert.equal(occurrences(html, '<table>'), 1)
  for (const item of getCourse8Reading(lesson(94)).services) {
    assert.equal(occurrences(html, item.text), 1)
    assert.equal(occurrences(html, `href="${item.url}"`), 1)
    // Each URL appears in its single anchor's href and visible text, never prose.
    assert.equal(occurrences(html, item.url), 2)
  }
  assert.doesNotMatch(html, /Адрес:|сведения требуют проверки перед публикацией|1\.4\.|1\.5\./)
  assert.match(html, /функции сервисов могут меняться/)
  assert.match(html, /Деление условно/)
  assert.match(html, /Нельзя считать какой-либо сервис лучшим для всех задач/)
})

test('five selection steps always visible, task table in step 2 and six criteria in step 3', () => {
  const html = render(95)
  const process = source[95].interactions[0]
  assert.equal(occurrences(html, 'class="course8-step-number"'), 5)
  assert.equal(occurrences(html, '<h3>'), 5)
  assert.equal(occurrences(html, '<table>'), 1)
  assert.ok(html.indexOf('Определить необходимые возможности') < html.indexOf('<table>'))
  assert.ok(html.indexOf('</table>') < html.indexOf('Оценить критерии'))
  assert.ok(html.indexOf('Оценить критерии') < html.indexOf('class="course8-criteria"'))
  for (const row of process.rows) for (const cell of row) assert.equal(occurrences(html, `<td>${cell}</td>`), 1)
  for (const criterion of process.criteria) assert.equal(occurrences(html, criterion), 1)
  for (const index of [0, 3, 4]) assert.equal(occurrences(html, process.steps[index].text), 1)
  assert.match(html, /еженедельного отчёта о продажах/)
  assert.match(html, /корпоративная инфраструктура или локальные модели/)
  assert.doesNotMatch(html, /<button|aria-expanded|\shidden=|opacity:|1\.6\./)
})

test('responsive layout uses theme tokens and readable table cells without hidden instructional text', async () => {
  const css = await readFile(new URL('../src/components/learning/course8-reading.css', import.meta.url), 'utf8')
  assert.match(css, /var\(--v2-text\)/)
  assert.match(css, /table-layout:fixed/)
  assert.match(css, /minmax\(0,1fr\)/)
  assert.match(css, /@media\(max-width:400px\)/)
  assert.doesNotMatch(css, /opacity:0|visibility:hidden|display:none|animation:|overflow:hidden/)
  assert.match(css, /li:not\(:last-child\)::after/)
  assert.match(css, /inset-block-end:-2\.5rem/)
  assert.match(css, /inset-inline-start:calc\(1rem - 1px\)/)
  assert.doesNotMatch(css, /li\+li::before/)
})
