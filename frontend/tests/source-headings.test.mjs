import assert from 'node:assert/strict'
import test from 'node:test'
import { studentSourceHeading } from '../src/utils/sourceHeadings.js'

const lesson = { id: 91, course_slug: 'kak-vybrat-neyroset-pod-svoyu-zadachu' }
test('only known chapter headings lose Word numbering in this course presentation', () => {
  assert.equal(studentSourceHeading('1.1. Что такое искусственный интеллект', lesson), 'Что такое искусственный интеллект')
  assert.equal(studentSourceHeading('1.8. Выводы по первой главе', { ...lesson, id: 96 }), 'Выводы по первой главе')
  for (const value of ['1. First example', 'Шаг 2. Определить возможности', '1.1. Other heading', 'Версия 1.2.', '1.9. More content']) {
    assert.equal(studentSourceHeading(value, lesson), value)
  }
  for (const other of [{ ...lesson, id: 90 }, { ...lesson, course_slug: 'other' }]) {
    assert.equal(studentSourceHeading('1.1. Что такое искусственный интеллект', other), '1.1. Что такое искусственный интеллект')
  }
})
