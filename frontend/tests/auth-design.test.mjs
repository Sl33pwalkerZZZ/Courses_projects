import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { before, after, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'

let server, Login, Register, Field, ErrorMessage, Footer
const translations = new Map()
before(async () => {
  server = await createTestServer()
  Login = (await server.ssrLoadModule('/src/pages/Login.jsx')).default
  Register = (await server.ssrLoadModule('/src/pages/Register.jsx')).default
  Field = (await server.ssrLoadModule('/src/components/AuthField.jsx')).default
  ErrorMessage = (await server.ssrLoadModule('/src/components/AuthError.jsx')).default
  Footer = (await server.ssrLoadModule('/src/components/Footer.jsx')).StudioFooter
  for (const lang of ['en', 'ru', 'kk']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${lang}.json`, import.meta.url), 'utf8'))
    const instance = createInstance()
    await instance.init({ lng: lang, resources: { [lang]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    translations.set(lang, instance)
  }
})
after(async () => { await server?.close() })

function render(Component, props = {}, lang = 'en') {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: translations.get(lang) },
    createElement(MemoryRouter, null, createElement(Component, props)),
  ))
}

for (const lang of ['en', 'ru', 'kk']) {
  for (const [mode, page] of [['login', () => Login], ['register', () => Register]]) {
    test(`${mode} preserves translated form semantics and navigation in ${lang}`, () => {
      const html = render(page(), {}, lang)
      assert.ok(html.includes(translations.get(lang).t(`auth.${mode}Title`)))
      assert.match(html, /<h1 id="auth-title">/)
      assert.match(html, /<form[^>]*aria-labelledby="auth-title"[^>]*aria-busy="false"/)
      assert.match(html, /for="auth-username"/)
      assert.match(html, /autoComplete="username"/)
      assert.match(html, /maxLength="150"/)
      assert.match(html, /type="submit"/)
      assert.match(html, new RegExp(`href="/${mode === 'login' ? 'register' : 'login'}"`))
      assert.doesNotMatch(html, /auth-orbit|academic-button|auth\.[a-zA-Z]|studio\.[a-zA-Z]/)
      const password = html.match(/<input[^>]*id="auth-password"[^>]*>/)[0]
      assert.match(password, /type="password"/)
      assert.match(password, /required=""/)
      assert.match(html, /aria-controls="auth-password" aria-pressed="false"/)
      assert.ok(html.includes(translations.get(lang).t('auth.showPassword')))
      if (mode === 'register') {
        assert.match(password, /minLength="8"/)
        assert.match(password, /autoComplete="new-password"/)
        const email = html.match(/<input[^>]*id="auth-email"[^>]*>/)[0]
        assert.match(email, /type="email"/)
        assert.match(email, /aria-describedby="auth-email-hint"/)
        assert.doesNotMatch(email, /required=/)
      } else {
        assert.match(password, /autoComplete="current-password"/)
        assert.doesNotMatch(html, /id="auth-email"/)
      }
    })
  }

  test(`auth decoration remains local, nonblocking and decorative in ${lang}`, () => {
    const html = render(Login, {}, lang)
    assert.match(html, /class="auth-illustration" aria-hidden="true"/)
    assert.equal((html.match(/alt=""/g) || []).length, 3)
    for (const size of [340, 188, 86]) assert.ok(html.includes(`width="${size}" height="${size}"`))
    assert.doesNotMatch(html, /https:\/\/www\.figma\.com|opacity:0|visibility:hidden/)
  })
}

test('disabled password field also disables its visibility button and keeps hint association', () => {
  const html = render(Field, { name: 'password', label: 'Password', type: 'password', hint: 'Guidance', disabled: true, required: true })
  assert.equal((html.match(/disabled=""/g) || []).length, 2)
  assert.match(html, /aria-describedby="auth-password-hint"/)
  assert.match(html, /id="auth-password-hint"/)
  assert.match(html, /class="auth-focus-line" aria-hidden="true"/)
})

test('server error text remains an immediately visible escaped alert', () => {
  const html = render(ErrorMessage, { children: '<script>unsafe()</script>' })
  assert.match(html, /role="alert"/)
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /<script>|opacity:0/)
})

test('reused V2 footer links to actual homepage sections from auth routes', () => {
  const html = render(Footer, { authed: false, home: false })
  assert.match(html, /href="\/#course-library"/)
  assert.match(html, /href="\/#learning-workflow"/)
  assert.doesNotMatch(html, /href="#/)
  const home = render(Footer, { authed: false })
  assert.match(home, /href="#course-library"/)
})
