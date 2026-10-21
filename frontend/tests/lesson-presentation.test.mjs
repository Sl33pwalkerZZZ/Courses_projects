import assert from 'node:assert/strict'
import test from 'node:test'
import { lessonPresentation, isSelectionMapTemplate, studentAssignmentDescription, studentInteraction } from '../src/utils/lessonPresentation.js'

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
