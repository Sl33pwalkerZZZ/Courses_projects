import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { renderToStaticMarkup } from 'react-dom/server'
import { createTestServer } from './helpers/vite.mjs'
import { mediaLessonSections } from '../src/utils/mediaLessonPresentation.js'
const lessons = await Promise.all(['media-lesson', 'media-lesson-101', 'media-lesson-102'].map(async name =>
  JSON.parse(await readFile(new URL(`./fixtures/${name}.json`, import.meta.url), 'utf8'))))
const i18n = createInstance()
let server, Reading, LessonMaterial, SourceParagraph
before(async () => {
  await i18n.init({ lng: 'ru', resources: { ru: { translation: {} } } })
  server = await createTestServer()
  Reading = (await server.ssrLoadModule('/src/components/learning/MediaLessonReading.jsx')).default
  SourceParagraph = (await server.ssrLoadModule('/src/components/learning/LearningContent.jsx')).SourceParagraph
  LessonMaterial = (await server.ssrLoadModule('/src/pages/LessonView.jsx')).LessonMaterial
})
after(async () => { await server?.close() })
const render = sections => renderToStaticMarkup(createElement(Reading, { sections }))
const reconstruct = sections => sections.flatMap(section => [section.heading, ...section.blocks.flatMap(block =>
  block.type === 'table' ? block.rows.map(row => row.map((cell, i) => `${block.headers[i]}: ${cell}`).join('; ')) : [block.text])]).join('\n\n')

test('all three actual saved lessons retain every text value and original ordering exactly', () => {
  for (const lesson of lessons) {
    const sections = mediaLessonSections(lesson)
    assert.equal(reconstruct(sections), lesson.text_content)
    const html = render(sections)
    assert.equal((html.match(/<h2 /g) || []).length, lesson.learning_content.source_sections.length)
    for (const section of sections) for (const block of section.blocks) {
      if (block.type === 'paragraph') {
        const paragraphHtml = renderToStaticMarkup(createElement(SourceParagraph, { text: block.text }))
        assert.equal(html.split(paragraphHtml).length - 1, 1)
      }
    }
  }
})

test('four source tables appear once, with labelled focusable regions and column headers', () => {
  for (const [index, lesson] of lessons.entries()) {
    const sections = mediaLessonSections(lesson)
    const tables = sections.flatMap(section => section.blocks.filter(block => block.type === 'table'))
    assert.deepEqual(tables.map(table => table.rows.length), [[6], [7], [9, 6]][index])
    const html = render(sections)
    assert.equal((html.match(/<table>/g) || []).length, tables.length)
    assert.match(html, /role="region" aria-labelledby="[^"]+" tabindex="0"/)
    assert.equal((html.match(/scope="col"/g) || []).length, tables.reduce((n, table) => n + table.headers.length, 0))
    assert.doesNotMatch(html, /Этап: Идея;|Поле брифа: Тема;|Критерий: Итого;/)
  }
  const html = render(mediaLessonSections(lessons[1]))
  assert.ok(html.indexOf('Поэтому работа начинается') < html.indexOf('<table>'))
  assert.ok(html.indexOf('</table>') < html.indexOf('2. Из чего'))
})

test('same metadata contract works for future courses without IDs or title matching', () => {
  const future = { title: 'Future lesson', course_slug: 'future', text_content: 'Introduction\n\nOriginal prose\n\nDetails\n\nField: A; Value: One\n\nField: B; Value: Two', learning_content: { source_sections: ['Introduction', 'Details'], interactions: [] } }
  const sections = mediaLessonSections(future)
  assert.equal(reconstruct(sections), future.text_content)
  assert.equal(sections[1].blocks[0].rows.length, 2)
})

test('legacy section IDs, custom interactions and ambiguous metadata fall back unchanged', () => {
  const lesson = lessons[0]
  assert.equal(mediaLessonSections({ ...lesson, learning_content: {} }), null)
  assert.equal(mediaLessonSections({ ...lesson, learning_content: { source_sections: ['1.1', '1.2'], interactions: [] } }), null)
  assert.equal(mediaLessonSections({ ...lesson, learning_content: { ...lesson.learning_content, interactions: [{ type: 'llm_steps' }] } }), null)
  assert.equal(mediaLessonSections({ ...lesson, text_content: lesson.text_content + '\n\n' + lesson.learning_content.source_sections[0] }), null)
})

test('unknown labelled prose and numbered instructions remain text; HTML is escaped', () => {
  const lesson = { text_content: 'Section\n\n1. This is an instruction.\n\nLabel: alone; Value: single\n\n<script>alert(1)</script>', learning_content: { source_sections: ['Section'] } }
  const sections = mediaLessonSections(lesson)
  assert.equal(reconstruct(sections), lesson.text_content)
  const html = render(sections)
  assert.doesNotMatch(html, /<table>|<script>/)
  assert.match(html, /<p>1\. This is an instruction\.<\/p>/)
  assert.match(html, /&lt;script&gt;/)
})

test('prompt examples, rules and original references are visible without interaction', () => {
  const promptHtml = render(mediaLessonSections(lessons[1]))
  assert.match(promptHtml, /media-lesson-prompt/)
  assert.match(promptHtml, /media-lesson-definition/)
  const html = render(mediaLessonSections(lessons[2]))
  assert.match(html, /media-lesson-warning/)
  for (const url of lessons[2].text_content.match(/https?:\/\/[^\s)]+/g)) assert.ok(html.includes(`href="${url}"`))
  assert.equal((html.match(/<a /g) || []).length, 3)
})

test('LessonMaterial retains objectives and renders fallback for legacy lessons', () => {
  for (const lesson of lessons) {
    const html = renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(LessonMaterial, { lesson, preview: true })))
    assert.match(html, /media-lesson-reading/)
    for (const objective of lesson.learning_content.objectives) assert.ok(html.includes(objective))
  }
  const legacy = { ...lessons[0], learning_content: { ...lessons[0].learning_content, source_sections: ['1.1'] } }
  const html = renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(LessonMaterial, { lesson: legacy, preview: true })))
  assert.doesNotMatch(html, /media-lesson-reading|<table>/)
  assert.match(html, /Этап: Идея;/)
})
