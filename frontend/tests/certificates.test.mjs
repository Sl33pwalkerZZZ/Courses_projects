import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { createTestServer } from './helpers/vite.mjs'

let server, i18n, Status, Verification
before(async () => {
  server = await createTestServer()
  i18n = createInstance()
  const resources = {}
  for (const language of ['ru', 'kk', 'en']) resources[language] = { translation: JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url))) }
  await i18n.init({ lng: 'en', resources, interpolation: { escapeValue: false } })
  Status = (await server.ssrLoadModule('/src/components/certificates/Certificates.jsx')).CertificateStatusContent
  Verification = (await server.ssrLoadModule('/src/pages/CertificateVerification.jsx')).VerificationDetails
})
after(async () => { await server?.close() })
const render = (Component, props) => renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(Component, props)))

test('server-side certificate requirements remain separate from lesson progress, with no self-issuance action', async () => {
  await i18n.changeLanguage('en')
  const html = render(Status, { result: { enabled: true, eligible: false, requirements: [{ key: 'all_lessons', met: true }, { key: 'final_assessment', met: false }, { key: 'assignment_approved', met: false }] } })
  assert.match(html, /All lessons completed/)
  assert.match(html, /Final assessment passed/)
  assert.match(html, /approved by an educator/)
  assert.equal((html.match(/Not yet met/g) || []).length, 2)
  assert.match(html, /authorized administrator/)
  assert.doesNotMatch(html, /<button|<form|eligible.*true/)
})

test('disabled certificate feature has a clear non-eligibility message in all interface languages', async () => {
  for (const language of ['ru', 'kk', 'en']) {
    await i18n.changeLanguage(language)
    const html = render(Status, { result: { enabled: false } })
    assert.ok(html.includes(i18n.t('certificates.disabled')))
    assert.doesNotMatch(html, /certificates\./)
  }
})

test('public verification displays initials and revoked status without account information', async () => {
  await i18n.changeLanguage('en')
  const html = render(Verification, { certificate: { status: 'revoked', learner_initials: 'A. B.', course_title: 'AI course', issuer_name: 'Approved issuer', issued_at: '2026-10-22T10:00:00Z', learner_name: 'PRIVATE FULL NAME', email: 'private@example.test', score: 98 } })
  assert.match(html, /revoked and is no longer valid/)
  assert.match(html, /A\. B\./)
  assert.match(html, /Approved issuer/)
  assert.doesNotMatch(html, /PRIVATE FULL NAME|private@example|98|<button|<form/)
})

test('private reads and downloads guard account changes; only GET endpoints are exposed', async () => {
  const source = await readFile(new URL('../src/components/certificates/Certificates.jsx', import.meta.url), 'utf8')
  assert.match(source, /response\?\.requestKey === requestKey && session\.authenticated/)
  assert.match(source, /getAuthSession\(\)\.generation !== generation/)
  assert.match(source, /responseType: 'blob'/)
  assert.match(source, /URL\.revokeObjectURL/)
  assert.doesNotMatch(source, /api\.(post|put|patch|delete)\(/)
})
