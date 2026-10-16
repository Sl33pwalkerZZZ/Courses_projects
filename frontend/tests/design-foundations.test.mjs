import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'

let server, HomeHero, Header, Button, ThemeContext
const dictionaries = new Map()
const translations = new Map()

before(async () => {
  // Existing toolchain compiles the actual components; no browser/DOM dependencies.
  server = await createTestServer()
  HomeHero = (await server.ssrLoadModule('/src/components/HomeHero.jsx')).default
  Header = (await server.ssrLoadModule('/src/components/Header.jsx')).default
  Button = (await server.ssrLoadModule('/src/components/ui/Button.jsx')).default
  ThemeContext = (await server.ssrLoadModule('/src/theme/useTheme.js')).ThemeContext
  for (const lang of ['en', 'ru', 'kk']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${lang}.json`, import.meta.url), 'utf8'))
    const instance = createInstance()
    await instance.init({ lng: lang, resources: { [lang]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    translations.set(lang, instance)
    dictionaries.set(lang, dictionary)
  }
})
after(async () => { await server?.close() })

function render(Component, props = {}, lang = 'en') {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: translations.get(lang) },
    createElement(ThemeContext.Provider, { value: { theme: 'light', toggleTheme() {} } },
      createElement(MemoryRouter, null, createElement(Component, props))),
  ))
}

for (const lang of ['en', 'ru', 'kk']) {
  test(`homepage has immediately available translated title and real navigation in ${lang}`, () => {
    const html = render(HomeHero, {}, lang)
    const t = translations.get(lang).t.bind(translations.get(lang))
    assert.match(html, /<h1 id="hero-title">/)
    assert.ok(html.includes(t('studio.title')))
    assert.ok(html.includes(t('studio.titleAccent')))
    assert.ok(html.includes(t('studio.description')))
    assert.match(html, /href="#course-library"/)
    assert.match(html, /href="\/register"/)
    assert.doesNotMatch(html, /opacity:0|visibility:hidden|studio\.[a-zA-Z]/)
  })

  test(`header keeps public routes, language choices and named menu in ${lang}`, () => {
    const html = render(Header, {}, lang)
    const t = translations.get(lang).t.bind(translations.get(lang))
    for (const href of ['/#course-library', '/login', '/register', '#main-content']) {
      assert.ok(html.includes(`href="${href}"`))
    }
    assert.ok(html.includes(`aria-label="${t('header.menu')}"`))
    assert.match(html, /aria-haspopup="dialog" aria-expanded="false"/)
    assert.doesNotMatch(html, /href="\/profile"/)
    for (const name of ['Русский', 'Қазақша', 'English']) assert.ok(html.includes(`aria-label="${name}"`))
  })

  test(`new UI strings are explicitly translated in ${lang}`, () => {
    const dictionary = dictionaries.get(lang)
    for (const key of ['eyebrow', 'title', 'titleAccent', 'description', 'appearance']) {
      assert.equal(typeof dictionary.studio[key], 'string')
      assert.ok(dictionary.studio[key].length > 0)
    }
    assert.ok(dictionary.header.menu && dictionary.header.closeMenu)
  })
}

test('shared actions preserve native link, router-link and disabled button semantics', () => {
  const anchor = render(Button, { href: '#course-library', children: 'Browse' })
  assert.match(anchor, /<a href="#course-library"/)
  const link = render(Button, { to: '/register', children: 'Register' })
  assert.match(link, /href="\/register"/)
  const button = render(Button, { disabled: true, children: 'Saving' })
  assert.match(button, /<button type="button"/)
  assert.match(button, /disabled=""/)
})

test('companion is decorative, local and preserves the Figma layer geometry', () => {
  const html = render(HomeHero)
  assert.match(html, /class="ai-companion" aria-hidden="true"/)
  assert.equal((html.match(/<image /g) || []).length, 9)
  for (const size of [340, 208, 151, 36, 14, 12, 8, 9]) assert.ok(html.includes(`width="${size}" height="${size}"`))
  assert.match(html, /href="(?:data:image\/svg\+xml,|\/src\/assets\/amethyst\/)/)
  assert.doesNotMatch(html, /https:\/\/www\.figma\.com|\.png/)
})

test('effective Amethyst colors preserve text/control contrast in both themes and hero surfaces', async () => {
  const css = await readFile(new URL('../src/styles/v2-tokens.css', import.meta.url), 'utf8')
  const luminance = (hex) => {
    const rgb = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
      .map((c) => c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4)
    return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722
  }
  const contrast = (a, b) => {
    const values = [luminance(a), luminance(b)].sort((x, y) => x - y)
    return (values[1] + .05) / (values[0] + .05)
  }
  const blocks = [css.split(':root {')[1].split('}')[0], css.split(':root[data-theme="light"] {')[1].split('}')[0]]
  for (const [index, block] of blocks.entries()) {
    const colors = Object.fromEntries([...block.matchAll(/--v2-([\w-]+): (#[0-9A-Fa-f]{6});/g)].map((match) => [match[1], match[2]]))
    assert.equal(colors.primary, index ? '#722CC4' : '#955CF0')
    for (const bg of ['canvas', 'surface', 'surface-raised']) {
      for (const fg of ['text', 'text-muted', 'link', 'accent', 'success', 'warning', 'danger']) {
        assert.ok(contrast(colors[fg], colors[bg]) >= 4.5, `${index}: ${fg}/${bg}`)
      }
      assert.ok(contrast(colors['control-border'], colors[bg]) >= 3)
    }
    assert.ok(contrast(colors.primary, colors['on-primary']) >= 4.5)
    assert.ok(contrast(colors['primary-hover'], colors['on-primary']) >= 4.5)
    for (const bg of ['hero-canvas', 'hero-surface-raised']) {
      for (const fg of ['hero-text', 'hero-text-muted', 'hero-link']) assert.ok(contrast(colors[fg], colors[bg]) >= 4.5)
      assert.ok(contrast(colors['hero-focus'], colors[bg]) >= 3)
    }
  }
})
