import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createTestServer } from './helpers/vite.mjs'
import { readFile } from 'node:fs/promises'
import { selectionStepUsesSourceTable } from '../src/utils/lessonPresentation.js'
let server, Content, Interaction
before(async () => {
  server = await createTestServer()
  const components = await server.ssrLoadModule('/src/components/learning/LearningContent.jsx')
  Content = components.default
  Interaction = components.LearningInteraction
})
after(async () => { await server?.close() })
const render = props => renderToStaticMarkup(createElement(Interaction, props))
test('actual lesson 92 shape provides all five visible process steps without hidden animation state', () => {
  const titles = ['Запрос пользователя', 'Разбиение на токены и обработка контекста', 'Вычисления языковой модели', 'Генерация ответа', 'Результат для пользователя']
  const text = 'Упрощённая последовательность из раздела 1.2; схема не означает гарантии достоверности.'
  const html = render({ interaction: { type: 'llm_steps', title: 'Как запрос превращается в ответ', steps: titles.map(title => ({ title, text })) } })
  for (const title of titles) assert.ok(html.includes(title))
  assert.match(html, /<ol class="learning-process">/)
  assert.equal(html.split(text).length - 1, 5)
  assert.doesNotMatch(html, /opacity:0/)
  assert.equal((html.match(/<h4>/g) || []).length, 5)
  assert.equal((html.match(/<p>/g) || []).length, 5)
  assert.doesNotMatch(html, /<button|aria-pressed/)
})
test('distinct process descriptions retain every supplied source explanation', () => {
  const html = render({ interaction: { type: 'llm_steps', title: 'Steps', steps: [{ title: 'First', text: 'Full first explanation' }, { title: 'Second', description: 'Full second explanation' }] } })
  assert.match(html, /Full first explanation/)
  assert.match(html, /Full second explanation/)
})
test('the saved lesson 92 snapshot and approval-only proposal each render five full heading/description pairs', async () => {
  const proposal = JSON.parse(await readFile(new URL('../../docs/courses/lesson92-content-edit-proposal.json', import.meta.url), 'utf8'))
  assert.equal(proposal.lesson_id, 92)
  for (const interaction of [proposal.before[0], proposal.after[0]]) {
    const html = render({ interaction })
    assert.equal(interaction.steps.length, 5)
    assert.equal((html.match(/<h4>/g) || []).length, 5)
    assert.equal((html.match(/<p>/g) || []).length, 5)
    for (const step of interaction.steps) {
      assert.ok(html.includes(step.title))
      assert.ok(html.includes(step.text))
    }
    assert.doesNotMatch(html, /<button|aria-hidden="true"[^>]*>[^<]*Запрос|opacity:0/)
  }
})
test('existing interaction types preserve titles, tables, links and source explanations', () => {
  for (const type of ['concept_hierarchy', 'categories', 'services', 'selection_steps', 'model_service']) {
    const html = render({ interaction: { type, title: 'Source title', items: [{ title: 'Item', text: 'Original explanation', url: 'https://example.com/source' }], headers: ['Task', 'Capability'], rows: [['Writing', 'Text']], criteria: ['Privacy'], warning: 'Source warning' } })
    for (const value of ['Source title', 'Original explanation', 'https://example.com/source', 'Writing', 'Privacy', 'Source warning']) assert.ok(html.includes(value), `${type}: ${value}`)
  }
})
test('empty interaction shells are omitted instead of presenting blank teaching panels', () => {
  assert.equal(render({ interaction: { type: 'llm_steps', title: 'Empty shell', steps: [] } }), '')
  assert.match(render({ interaction: { type: 'selection_steps', title: 'Source table', steps: [], rows: [['Task', 'Functions']] } }), /Task/)
})
test('generic implementation preface is not part of student learning content', () => {
  const html = renderToStaticMarkup(createElement(Content, { content: { objectives: ['Teacher objective'], interactions: [] } }))
  assert.doesNotMatch(html, /learning.authoredActivity|Интерактивное представление добавлено/)
  assert.match(html, /Teacher objective/)
})

test('only the verified empty selection step uses its existing source table as detail', () => {
  const interaction = { type: 'selection_steps', steps: [{ title: 'Шаг 1', text: 'Task' }, { title: 'Шаг 2. Определить необходимые возможности', text: '' }], headers: ['Задача', 'Нужные функции', 'Инструменты для проверки'], rows: [['Анализ таблиц', 'Вычисления', 'Source tools']] }
  assert.equal(selectionStepUsesSourceTable(interaction, 1), true)
  assert.equal(selectionStepUsesSourceTable(interaction, 0), false)
  assert.equal(selectionStepUsesSourceTable({ ...interaction, type: 'llm_steps' }, 1), false)
  assert.equal(selectionStepUsesSourceTable({ ...interaction, headers: ['Other', 'Headers'] }, 1), false)
  assert.equal(selectionStepUsesSourceTable({ ...interaction, rows: [] }, 1), false)
  assert.equal(selectionStepUsesSourceTable({ ...interaction, steps: [interaction.steps[0], { ...interaction.steps[1], text: 'Existing explanation' }] }, 1), false)
  const html = render({ interaction })
  assert.equal((html.match(/<table>/g) || []).length, 1)
  assert.match(html, /Анализ таблиц/)
})
