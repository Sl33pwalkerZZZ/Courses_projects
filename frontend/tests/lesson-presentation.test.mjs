import assert from 'node:assert/strict'
import test from 'node:test'
import { lessonPresentation, isSelectionMapTemplate, studentAssignmentDescription, studentInteraction } from '../src/utils/lessonPresentation.js'
import { lesson91Reading, lessonReadingBlocks } from '../src/utils/lessonPresentation.js'
import { lesson91Source as source } from '../src/utils/lesson91Source.js'
import course8Source from './fixtures/course8Source.json' with { type: 'json' }
import { verifiedCourse8Practice } from '../src/utils/lessonPresentation.js'

test('verified practice groups all six instructions once and rejects changed content', () => {
  const saved = course8Source['96']
  const lesson = { ...saved, learning_content: { interactions: saved.interactions }, assignments: [{ learning_activity: 'ai_selection_map', description: saved.assignment_description }] }
  assert.equal(verifiedCourse8Practice(lesson), true)
  const paragraphs = saved.text_content.split('\n\n')
  const blocks = lessonReadingBlocks(paragraphs, lesson)
  assert.equal(blocks.filter(block => block.type === 'instructions').length, 1)
  assert.equal(blocks.find(block => block.type === 'instructions').items.length, 6)
  assert.deepEqual(blocks.flatMap(block => block.type === 'instructions' ? block.items : [block.text]), paragraphs)
  for (const changed of [{ ...lesson, id: 95 }, { ...lesson, text_content: saved.text_content + '\nTeacher update' }, { ...lesson, assignments: [] }, { ...lesson, assignments: [{ learning_activity: 'ai_selection_map', description: 'New teacher instructions' }] }]) {
    assert.ok(!verifiedCourse8Practice(changed))
    assert.ok(lessonReadingBlocks(paragraphs, changed).every(block => block.type !== 'instructions'))
  }
})

test('lesson 91 hides only its verified cover prefix without mutating source or losing teaching text', () => {
  const paragraphs = [...source.titlePage, source.sectionHeading, 'Keep every teaching paragraph.']
  const original = [...paragraphs]
  const lesson = { id: 91, course_slug: source.courseSlug }
  assert.deepEqual(lesson91Reading(lesson, paragraphs), paragraphs.slice(7))
  assert.deepEqual(paragraphs, original)
  for (const other of [{ ...lesson, id: 92 }, { ...lesson, course_slug: 'other' }]) {
    assert.deepEqual(lesson91Reading(other, paragraphs), original)
  }
  const edited = [...paragraphs]
  edited[1] = 'New teacher text'
  assert.deepEqual(lesson91Reading(lesson, edited), edited)
  const changedHeading = [...paragraphs]
  changedHeading[7] = 'New heading'
  assert.deepEqual(lesson91Reading(lesson, changedHeading), changedHeading)
})

test('source examples gain a semantic list with exact wording and preserve all other prose', () => {
  const paragraphs = ['Before', source.exampleHeading, ...source.examples, source.relationHeading, 'After']
  const blocks = lessonReadingBlocks(paragraphs)
  assert.deepEqual(blocks[1], { type: 'examples', heading: source.exampleHeading, items: source.examples })
  const restored = blocks.flatMap(block => block.type === 'examples' ? [block.heading, ...block.items] : [block.text])
  assert.deepEqual(restored, paragraphs)
  const edited = [...paragraphs]
  edited[2] = 'Teacher replacement example'
  assert.ok(lessonReadingBlocks(edited).every(block => block.type === 'paragraph'))
})

const template = { type: 'model_service', title: 'Source map', headers: ['Параметр', 'Ответ участника'], rows: [['Рабочая задача', ''], ['Исходные данные', '']] }
test('practice has one form entry point while its exact source template stays available as reference', () => {
  const lesson = { text_content: 'Task instructions\n\nПараметр | Ответ участника\nРабочая задача | \nИсходные данные | \n\nWorked example\n\n1.8. Выводы по первой главе\n\nImportant conclusion\n\nМатериалы для дополнительного изучения\n\nhttps://example.org/',
    learning_content: { objectives: ['Objective'], interactions: [template] }, assignments: [{ learning_activity: 'ai_selection_map' }] }
  const original = structuredClone(lesson)
  const result = lessonPresentation(lesson)
  assert.deepEqual(result.reading, ['Task instructions', 'Worked example'])
  assert.deepEqual(result.conclusions, ['1.8. Выводы по первой главе', 'Important conclusion'])
  assert.deepEqual(result.resources, ['Материалы для дополнительного изучения', 'https://example.org/'])
  assert.deepEqual(result.templates, [template])
  assert.deepEqual(result.content.interactions, [])
  assert.deepEqual(lesson, original)
})
test('informative tables and unrelated lessons are never mistaken for empty practice templates', () => {
  assert.equal(isSelectionMapTemplate({ ...template, rows: [['Task', 'Important explanation']] }), false)
  assert.equal(isSelectionMapTemplate({ ...template, rows: [['Task', null]] }), false)
  assert.equal(isSelectionMapTemplate({ ...template, headers: ['Model', 'Service'] }), false)
  const source = { text_content: 'Keep\n\n1.8. Выводы по первой главе', learning_content: { interactions: [template] } }
  assert.deepEqual(lessonPresentation(source).content.interactions, [template])
  assert.equal(lessonPresentation(source).conclusions.length, 0)
})
test('only exact editorial provenance is removed from student presentation; source warnings remain', () => {
  const safety = 'Не сохраняйте персональные данные, пароли или ключи.'
  const provenance = 'Поля сравнения и сохранение черновика — авторское цифровое развитие исходной карты.'
  assert.equal(studentAssignmentDescription(`${safety} ${provenance}`), safety)
  assert.equal(studentAssignmentDescription(`Teacher discussion: ${provenance} More explanation.`), `Teacher discussion: ${provenance} More explanation.`)
  const original = { title: 'Сервисы из раздела 1.5 — сведения требуют проверки перед публикацией', warning: 'Features vary; check sources.' }
  assert.equal(studentInteraction(original).title, 'Обзор популярных ИИ-сервисов')
  assert.equal(studentInteraction(original).warning, original.warning)
  assert.ok(original.title.includes('перед публикацией'))
})
