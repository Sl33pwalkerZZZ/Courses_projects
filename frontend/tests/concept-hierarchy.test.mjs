import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { readFile } from 'node:fs/promises'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { createTestServer } from './helpers/vite.mjs'

let server, Interaction, i18n
const titles = ['Искусственный интеллект', 'Машинное обучение', 'Глубокое обучение', 'LLM']
const interaction = { type: 'concept_hierarchy', title: 'Связь понятий', items: titles.map(title => ({ title, text: 'Repeated full source definition stays in original lesson prose.' })) }
before(async () => {
  server = await createTestServer()
  i18n = createInstance()
  const resources = {}
  for (const language of ['ru', 'kk', 'en']) resources[language] = { translation: JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url))) }
  await i18n.init({ lng: 'ru', resources, interpolation: { escapeValue: false } })
  Interaction = (await server.ssrLoadModule('/src/components/learning/LearningContent.jsx')).LearningInteraction
})
after(async () => { await server?.close() })
const render = value => renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(Interaction, { interaction: value })))

test('four source concepts are nested semantic levels, not four unrelated selector buttons', async () => {
  await i18n.changeLanguage('ru')
  const html = render(interaction)
  assert.equal((html.match(/<ul class="concept-hierarchy-level">/g) || []).length, 4)
  assert.equal((html.match(/<li>/g) || []).length, 4)
  assert.equal((html.match(/<h4>/g) || []).length, 4)
  // The first three entries contain a child list before their closing li.
  assert.match(html, /<\/div><ul class="concept-hierarchy-level"><li>/)
  for (const title of titles) assert.ok(html.includes(title))
  assert.doesNotMatch(html, /<button|<svg|hidden=|aria-hidden|opacity:|Repeated full source definition/)
  assert.match(html, /Направление ИИ: обучение на данных/)
  assert.match(html, /Один из классов моделей глубокого обучения/)
  assert.match(html, /не весь генеративный ИИ/)
})

test('relationships have complete RU/KK/EN translations and remain permanently visible', async () => {
  for (const language of ['ru', 'kk', 'en']) {
    await i18n.changeLanguage(language)
    const dict = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url)))
    const html = render(interaction)
    for (const key of ['hierarchyAI', 'hierarchyML', 'hierarchyDL', 'hierarchyLLM', 'hierarchyBoundary']) {
      assert.ok(dict.learning[key]?.length > 10)
      assert.ok(html.includes(dict.learning[key]), `${language}: ${key}`)
    }
    assert.doesNotMatch(html, /aria-live|aria-expanded|aria-pressed|display:none/)
  }
})

test('other authored concept hierarchies preserve their full source data and generic interaction', () => {
  const html = render({ type: 'concept_hierarchy', title: 'Different source', items: [{ title: 'Original title', text: 'Original source explanation' }] })
  assert.match(html, /Original source explanation/)
  assert.match(html, /Original title/)
  assert.match(html, /<button/)
  assert.doesNotMatch(html, /concept-hierarchy-level/)
})

test('nested layout has narrow-screen spacing, theme tokens and no hiding or animation dependency', async () => {
  const css = await readFile(new URL('../src/components/learning/concept-hierarchy.css', import.meta.url), 'utf8')
  assert.match(css, /@media\(max-width:400px\)/)
  assert.match(css, /overflow-wrap:anywhere/)
  assert.match(css, /var\(--v2-text\)/)
  assert.doesNotMatch(css, /opacity:0|display:none|visibility:hidden|animation:|overflow:hidden/)
})
