import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { readFile } from 'node:fs/promises'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { createTestServer } from './helpers/vite.mjs'

let server, Check
before(async () => {
  server = await createTestServer()
  Check = (await server.ssrLoadModule('/src/components/learning/PracticeCheck.jsx')).default
})
after(async () => { await server?.close() })
test('optional practice is labeled, keyboard-native and has no revealed feedback initially', async () => {
  for (const language of ['ru', 'kk', 'en']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url)))
    const i18n = createInstance()
    await i18n.init({ lng: language, resources: { [language]: { translation: dictionary } } })
    for (const lessonId of [93, 95]) {
      const html = renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(Check, { lessonId })))
      assert.ok(html.includes(dictionary.learning.selfCheckNote))
      assert.match(html, /<fieldset lang="ru"><legend>/)
      assert.equal((html.match(/type="radio"/g) || []).length, 2)
      assert.doesNotMatch(html, /role="status"|checked=""/)
    }
  }
  const code = await readFile(new URL('../src/components/learning/PracticeCheck.jsx', import.meta.url), 'utf8')
  assert.doesNotMatch(code, /fetch\(|api\.|localStorage|sessionStorage/)
  assert.equal(renderToStaticMarkup(createElement(Check, { lessonId: 94 })), '')
})
