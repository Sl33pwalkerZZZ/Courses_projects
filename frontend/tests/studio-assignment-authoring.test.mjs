import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { createTestServer } from './helpers/vite.mjs'
let server, Form, Instructions, Student
const dictionaries = new Map()
before(async () => {
 server = await createTestServer()
 Form = (await server.ssrLoadModule('/src/pages/instructor/Assessment.jsx')).AssignmentForm
 Instructions = (await server.ssrLoadModule('/src/components/learning/AssignmentInstructions.jsx')).default
 Student = (await server.ssrLoadModule('/src/components/learning/AssignmentSubmission.jsx')).default
 for (const language of ['ru','kk','en']) {
  const dict = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
  const instance = createInstance(); await instance.init({ lng: language, resources: { [language]: { translation: dict } }, interpolation: { escapeValue: false } })
  dictionaries.set(language, instance)
 }
})
after(async () => server?.close())
const assignment = { id: 55, type: 'text', learning_activity: 'final_media_project', description: 'Fixture project title\n\nExact paragraph.\nSecond line with <literal> text.' }
function render(Component, props, language='en') {
 return renderToStaticMarkup(createElement(I18nextProvider, { i18n: dictionaries.get(language) }, createElement(Component, props)))
}
test('existing final activity and real text/file submission options remain selected on reopen', () => {
 const html = render(Form, { lesson: 501, initial: assignment, onSaved() {} })
 assert.match(html, /value="final_media_project" selected=""/)
 assert.match(html, /value="text" selected=""/)
 assert.match(html, /Text and\/or files/)
 assert.match(html, /Files required; text optional/)
 assert.doesNotMatch(html, /value="both"|name="title"/)
 assert.ok(html.includes('Fixture project title\n\nExact paragraph.\nSecond line with &lt;literal&gt; text.'))
 const file = render(Form, { initial: { ...assignment, type:'file' }, onSaved() {} })
 assert.match(file, /value="file" selected=""/)
})
test('rubric has all four existing labels, readonly whole-number ranges, no scoring inputs', () => {
 const html = render(Instructions, { assignment })
 for (const key of ['completeness','application','quality','documentation']) assert.ok(html.includes(dictionaries.get('en').t(`instructorStudio.assignmentReview.rubric.${key}`)))
 assert.equal((html.match(/0–25 points/g)||[]).length, 4)
 assert.doesNotMatch(html, /<input|<textarea|<select/)
 assert.doesNotMatch(render(Instructions, { assignment: { ...assignment, learning_activity:'' } }), /Final project rubric/)
})
test('actual student preview and shared instructions preserve exact text, line breaks and escaping', () => {
 const html = render(Student, { assignment, preview:true })
 const content = render(Instructions, { assignment })
 assert.ok(html.includes(content))
 assert.match(html, /assignment-instructions-text/)
 assert.ok(html.includes('Fixture project title\n\nExact paragraph.\nSecond line with &lt;literal&gt; text.'))
 assert.doesNotMatch(html, /<form|<literal>/)
})
test('title/instructions guidance, modes and rubric are translated in RU/KK/EN', () => {
 for (const [language, i18n] of dictionaries) {
  const html = render(Form, { initial:assignment, onSaved() {} }, language)
  for (const key of ['titleInstructions','descriptionHint','activityLabel','text','file','fixedRubric','preview']) assert.ok(html.includes(i18n.t(`instructorStudio.assignmentAuthoring.${key}`)), `${language}.${key}`)
  assert.equal((render(Instructions, { assignment }, language).match(/<dt>/g)||[]).length,4)
 }
})
test('standard/map workflows and published lock are preserved', () => {
 const blank = render(Form, { lesson:501, onSaved() {} })
 assert.match(blank, /required=""/)
 assert.doesNotMatch(blank, /instructor-assignment-rubric/)
 const map = render(Form, { initial:{ ...assignment, learning_activity:'ai_selection_map' }, onSaved() {} })
 assert.match(map, /value="ai_selection_map" selected=""/)
 assert.match(map, /<select[^>]*disabled=""/)
 assert.doesNotMatch(map, /instructor-assignment-rubric/)
 assert.match(render(Form, { initial:assignment, onSaved() {}, locked:true }), /<fieldset disabled=""/)
})
