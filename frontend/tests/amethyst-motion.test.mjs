import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { before, after, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
import { graphemes, textWords } from '../src/utils/motionText.js'

let server, Text, Story, Companion, ThemeContext
const translations = new Map()
before(async () => {
  server = await createTestServer()
  Text = (await server.ssrLoadModule('/src/components/motion/AnimatedText.jsx')).default
  Story = (await server.ssrLoadModule('/src/components/motion/SignalStory.jsx')).default
  Companion = (await server.ssrLoadModule('/src/components/motion/AICompanion.jsx')).default
  ThemeContext = (await server.ssrLoadModule('/src/theme/useTheme.js')).ThemeContext
  for (const language of ['en', 'ru', 'kk']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    const instance = createInstance()
    await instance.init({ lng: language, resources: { [language]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    translations.set(language, instance)
  }
})
after(async () => { await server?.close() })
function render(component, props = {}, language = 'en', theme = 'light') {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: translations.get(language) },
    createElement(ThemeContext.Provider, { value: { theme, toggleTheme() {} } }, createElement(component, props))))
}

test('graphemes retain combining marks, emoji sequences and Kazakh letters', () => {
  assert.deepEqual(graphemes('е\u0308', 'ru'), ['е\u0308'])
  assert.deepEqual(graphemes('👨‍👩‍👧‍👦', 'en'), ['👨‍👩‍👧‍👦'])
  assert.deepEqual(graphemes('ҚҰҮІҢ', 'kk'), ['Қ', 'Ұ', 'Ү', 'І', 'Ң'])
  assert.equal(graphemes('Learning', 'en').join(''), 'Learning')
  assert.equal(textWords('Үйрену  және\nтәжірибе').join(''), 'Үйрену  және\nтәжірибе')
})
test('unsupported segmentation degrades to intact words rather than damaged graphemes', () => {
  const saved = Intl.Segmenter
  try { Intl.Segmenter = undefined; assert.deepEqual(graphemes('е\u0308Қ'), ['е\u0308Қ']) }
  finally { Intl.Segmenter = saved }
})
for (const language of ['en', 'ru', 'kk']) {
  test(`large text preserves an unsplit accessible phrase in ${language}`, () => {
    const text = translations.get(language).t('studio.titleAccent')
    const html = render(Text, { text }, language)
    assert.ok(html.includes(`<span class="sr-only">${text}</span>`))
    assert.ok(html.includes(`<span aria-hidden="true">${text}</span>`))
    assert.doesNotMatch(html, /tabindex|role="button"|aria-live/)
  })
  test(`reduced/server story has every readable chapter and a native exit in ${language}`, () => {
    const html = render(Story, {}, language)
    for (const stage of ['discover', 'connect', 'practice']) {
      assert.ok(html.includes(translations.get(language).t(`amethyst.story.${stage}.title`)))
      assert.ok(html.includes(translations.get(language).t(`amethyst.story.${stage}.description`)))
    }
    assert.match(html, /href="#course-library"/)
    assert.doesNotMatch(html, /story-chapters|signal-story-sticky|opacity:0|amethyst\.[a-z]/)
  })
}
test('companion is decorative/static on server and all provided SVG dimensions stay intact', async () => {
  for (const theme of ['light', 'dark']) {
    const html = render(Companion, {}, 'en', theme)
    assert.match(html, /aria-hidden="true" data-motion-active="false"/)
    assert.equal((html.match(/<image /g) || []).length, 9)
    assert.doesNotMatch(html, /tabindex|https:\/\/www\.figma\.com/)
    for (const [name, size] of [['aura',208],['head',151],['eye',36],['pupil',14],['particle-1',12],['particle-2',8],['particle-3',9]]) {
      const asset = await readFile(new URL(`../src/assets/amethyst/${name}-${theme}.svg`, import.meta.url), 'utf8')
      const root = asset.match(/<svg\b[^>]*>/)[0]
      assert.ok(root.includes(`width="${size}"`) && root.includes(`height="${size}"`))
    }
  }
})
