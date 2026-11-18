import assert from 'node:assert/strict'
import { before, after, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { createTestServer } from './helpers/vite.mjs'
import { quizProblems } from '../src/utils/instructorStudio.js'
let server, Editor
before(async () => { server = await createTestServer(); Editor = (await server.ssrLoadModule('/src/pages/instructor/Assessment.jsx')).QuizEditor })
after(async () => server?.close())
const quiz = { id:7, title:'Fixture quiz', instructions:'Exact instructions', passing_percentage:85, questions:[{ text:'Edited question?', type:'single', explanation:'Why B', choices:[{text:'A',is_correct:false},{text:'B',is_correct:true}] }] }
test('threshold follows server integer contract, including empty and fractional values', () => {
 for (const value of ['', ' ', null, undefined, 85.5, -1, 101, 'NaN']) assert.ok(quizProblems({...quiz,passing_percentage:value}).includes('passing'), String(value))
 for (const value of [0,70,100,'85']) assert.deepEqual(quizProblems({...quiz,passing_percentage:value}), [])
})
test('question/choice limits and exact single/multiple keys match server rules', () => {
 assert.ok(quizProblems({...quiz,questions:Array(101).fill(quiz.questions[0])}).includes('questions'))
 const question = {...quiz.questions[0],choices:Array(21).fill({text:'A',is_correct:true})}
 assert.ok(quizProblems({...quiz,questions:[question]}).includes('question 1'))
 assert.ok(quizProblems({...quiz,questions:[{...question,choices:[{text:'A',is_correct:true},{text:'B',is_correct:true}]}]}).includes('answers 1'))
 assert.deepEqual(quizProblems({...quiz,questions:[{...question,type:'multiple',choices:[{text:'A',is_correct:true},{text:'B',is_correct:true}]}]}),[])
})
test('reopened editor preserves text, threshold and correct answer in RU/KK/EN; assessed quizzes lock', async () => {
 for (const language of ['ru','kk','en']) {
  const dictionary=JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`,import.meta.url),'utf8'))
  const i18n=createInstance(); await i18n.init({lng:language,resources:{[language]:{translation:dictionary}}})
  const render=initial=>renderToStaticMarkup(createElement(I18nextProvider,{i18n},createElement(Editor,{lesson:500,initial,onSaved(){}})))
  const html=render(quiz)
  assert.match(html,/Edited question\?/);assert.match(html,/value="85"/); assert.match(html,/step="1"/)
  assert.match(html,/type="radio"[^>]*checked=""/)
  assert.ok(html.includes(i18n.t('instructorStudio.quizAuthoring.single')))
  assert.ok(html.includes(i18n.t('instructorStudio.quizAuthoring.answerPolicy')))
  assert.match(render({...quiz,locked:true}),/<fieldset disabled=""/)
 }
})
