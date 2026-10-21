import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
import { emptySelectionMap, selectionMapProblems, updateComparedService, normalizeSelectionMap, serializeSelectionMap } from '../src/utils/selectionMap.js'
import { loadCourseOutline, lessonParagraphs } from '../src/utils/lessons.js'
let server, Content, Interaction, Selection, SourceParagraph
const languages = new Map()
before(async () => {
  server = await createTestServer()
  const components = await server.ssrLoadModule('/src/components/learning/LearningContent.jsx')
  Content = components.default; Interaction = components.LearningInteraction
  SourceParagraph = components.SourceParagraph
  Selection = (await server.ssrLoadModule('/src/components/learning/SelectionMap.jsx')).default
  for (const language of ['ru', 'kk', 'en']) {
    const instance = createInstance()
    await instance.init({ lng: language, resources: { [language]: { translation: JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url))) } }, interpolation: { escapeValue: false } })
    languages.set(language, instance)
  }
})
after(async () => { await server?.close() })
const render = (component, props, language = 'en') => renderToStaticMarkup(createElement(I18nextProvider, { i18n: languages.get(language) }, createElement(component, props)))
test('selection drafts are independent and complete submissions require distinct services and evidence', () => {
  const draft = emptySelectionMap(); draft.services[0] = 'Changed'
  assert.equal(emptySelectionMap().services[0], '')
  assert.ok(selectionMapProblems(draft).includes('services'))
  const full = { ...emptySelectionMap(), working_task: 'Anonymized task', input_data: 'Synthetic example', expected_result: 'Summary', required_capabilities: 'Text', final_justification: 'Evidence', services: ['One', 'Two'], selected_service: 'One', comparison_criteria: { quality: 'a', features: 'a', cost: 'a', speed: 'a', privacy: 'a', ease: 'a' }, testing_results: [{ service: 'One', result: 'Observed result' }, { service: 'Two', result: 'Observed result' }] }
  assert.deepEqual(selectionMapProblems(full), [])
  const padded = { ...full, services: [' One ', ' Two '], selected_service: ' One ', testing_results: [{ service: ' One ', result: 'Observed' }, { service: ' Two ', result: 'Observed' }] }
  assert.deepEqual(selectionMapProblems(padded), [])
  assert.ok(selectionMapProblems({ ...full, services: ['One', 'one'] }).includes('services'))
  assert.ok(selectionMapProblems({ ...full, selected_service: 'Other' }).includes('selected_service'))
  assert.ok(selectionMapProblems({ ...full, testing_results: [] }).includes('testing_results'))
  const renamed = updateComparedService(full, 0, 'Renamed')
  assert.equal(renamed.selected_service, 'Renamed'); assert.equal(renamed.testing_results[0].service, 'Renamed')
  assert.equal(full.services[0], 'One')
})
test('source tables preserve cells as escaped accessible native tables', () => {
  const html = render(Interaction, { interaction: { type: 'model_service', title: 'Comparison', headers: ['Model', 'Service'], rows: [['<script>bad</script>', 'Interface']] } })
  assert.match(html, /<th scope="col">Model<\/th>/); assert.match(html, /&lt;script&gt;/); assert.doesNotMatch(html, /<script>/)
  assert.match(html, /tabindex="0"/)
})
test('source references remain unchanged clickable HTTPS links, never executable markup', () => {
  const text = 'Источник https://help.openai.com/en/articles/10032626-prompt-ingineering-best-practices-for-chatgpt. javascript:alert(1) <script>bad</script>'
  const html = render(SourceParagraph, { text })
  assert.match(html, /href="https:\/\/help.openai.com\/en\/articles\/10032626-prompt-ingineering-best-practices-for-chatgpt"/)
  assert.match(html, /rel="noopener noreferrer"/)
  assert.match(html, /javascript:alert\(1\)/)
  assert.doesNotMatch(html, /href="javascript:|<script>/)
})
test('LLM process is readable static HTML without requiring keyboard or pointer selection', () => {
  const html = render(Interaction, { interaction: { type: 'llm_steps', title: 'Process', steps: [{ title: 'Input', text: 'Source description' }, { title: 'Output', text: 'Result' }] } })
  assert.match(html, /<h4>Input<\/h4>/); assert.match(html, /<p>Source description<\/p>/); assert.match(html, /<h4>Output<\/h4>/)
  assert.doesNotMatch(html, /<button|aria-pressed|correct_answer|is_correct/)
})
test('other step selectors retain their native keyboard buttons', () => {
  const html = render(Interaction, { interaction: { type: 'selection_steps', title: 'Selection', steps: [{ title: 'Task', text: 'Source description' }, { title: 'Compare', text: 'Criteria' }] } })
  assert.match(html, /<button/)
  assert.match(html, /aria-pressed="true"/)
  assert.match(html, /Source description/)
})
for (const language of ['ru', 'kk', 'en']) test(`Russian course fallback with translated interface in ${language}`, () => {
  const html = render(Content, { content: { content_language: 'ru', objectives: ['Исходная цель'], interactions: [] } }, language)
  assert.match(html, /lang="ru"/); assert.match(html, /Исходная цель/)
  assert.ok(html.includes(languages.get(language).t('learning.objectives')))
  if (language !== 'ru') assert.ok(html.includes(languages.get(language).t('learning.russianFallback')))
  const form = render(Selection, { assignment: { id: 99 } }, language)
  assert.ok(form.includes(languages.get(language).t('selectionMap.safety')))
  assert.ok(form.includes(languages.get(language).t('selectionMap.noExternalCalls')))
  assert.doesNotMatch(form, /localStorage|Bearer|correct_answer/)
})
test('draft instructor outline uses only authorized preview API and never invents enrollment', async () => {
  const calls = []
  const result = await loadCourseOutline({ get: async path => { calls.push(path); return { data: { title: 'Draft', modules: [] } } } }, 'draft-course', true)
  assert.deepEqual(calls, ['/instructor/courses/draft-course/preview/']); assert.equal(result.enrollment, null)
})

test('partial drafts omit empty service slots and resume with two editable slots', () => {
  const payload = emptySelectionMap(); payload.working_task = 'Task only'
  const saved = serializeSelectionMap(payload)
  assert.deepEqual(saved.services, []); assert.deepEqual(saved.testing_results, [])
  assert.deepEqual(normalizeSelectionMap(saved).services, ['', ''])
  assert.equal(normalizeSelectionMap(saved).working_task, 'Task only')
})
test('table fallback deduplication preserves all surrounding source explanations', () => {
  const lesson = { text_content: 'Explanation\n\nA | B\nC | D\n\nConclusion', learning_content: { interactions: [{ headers: ['A', 'B'], rows: [['C', 'D']] }] } }
  assert.deepEqual(lessonParagraphs(lesson), ['Explanation', 'Conclusion'])
  assert.deepEqual(lessonParagraphs({ text_content: 'A | B\nC | D' }), ['A | B\nC | D'])
})
