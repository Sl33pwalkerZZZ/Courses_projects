import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { createTestServer } from './helpers/vite.mjs'

let server, i18n, Status, Verification, CertificateNamePanel, CertificateListContent
before(async () => {
  server = await createTestServer()
  i18n = createInstance()
  const resources = {}
  for (const language of ['ru', 'kk', 'en']) resources[language] = { translation: JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url))) }
  await i18n.init({ lng: 'en', resources, interpolation: { escapeValue: false } })
  Status = (await server.ssrLoadModule('/src/components/certificates/Certificates.jsx')).CertificateStatusContent
  CertificateNamePanel = (await server.ssrLoadModule('/src/components/certificates/Certificates.jsx')).CertificateNamePanel
  CertificateListContent = (await server.ssrLoadModule('/src/components/certificates/Certificates.jsx')).CertificateListContent
  Verification = (await server.ssrLoadModule('/src/pages/CertificateVerification.jsx')).VerificationDetails
})
after(async () => { await server?.close() })
const render = (Component, props) => renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(MemoryRouter, null, createElement(Component, props))))

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

test('explicit required-lesson eligibility label is translated in RU, KK and EN', async () => {
  for (const language of ['ru', 'kk', 'en']) {
    await i18n.changeLanguage(language)
    const label = i18n.t('certificates.requirements.required_lessons')
    const html = render(Status, { result: { enabled: true, eligible: false, requirements: [{ key: 'required_lessons', met: true }] } })
    assert.ok(html.includes(label))
    assert.doesNotMatch(html, /certificates\.requirements\.required_lessons/)
  }
})

test('student certificate-name review and confirmation controls are localized in RU, KK and EN', async () => {
  for (const language of ['ru', 'kk', 'en']) {
    await i18n.changeLanguage(language)
    const html = render(CertificateNamePanel, {
      record: { learner_name: 'Әлия Қасымқызы', confirmed: false },
      draft: 'Әлия Қасымқызы', onDraftChange() {}, onSave() {}, onConfirm() {},
      confirmation: true, onConfirmationChange() {}, busy: false, error: '',
    })
    assert.match(html, /Әлия Қасымқызы/)
    assert.match(html, new RegExp(i18n.t('certificates.nameTitle')))
    assert.match(html, new RegExp(i18n.t('certificates.nameConfirm')))
    assert.match(html, new RegExp(i18n.t('certificates.nameConfirmButton')))
    assert.match(html, /type="checkbox" checked/)
    assert.doesNotMatch(html, /certificates\.name(?:Title|Confirm|ConfirmButton)/)
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

test('private reads and downloads guard account changes; certificate-name writes stay self-scoped', async () => {
  const source = await readFile(new URL('../src/components/certificates/Certificates.jsx', import.meta.url), 'utf8')
  assert.match(source, /response\?\.requestKey === requestKey && session\.authenticated/)
  assert.match(source, /getAuthSession\(\)\.generation !== generation/)
  assert.match(source, /responseType: 'blob'/)
  assert.match(source, /URL\.revokeObjectURL/)
  assert.match(source, /api\.put\('\/my\/certificate-name\//)
  assert.match(source, /api\.post\('\/my\/certificate-name\//)
  assert.doesNotMatch(source, /student_id|user_id|certificate_name_confirmed_at/)
})


test('Profile distinguishes unavailable, empty, loading and retryable error states in all locales', async () => {
  for (const language of ['ru', 'kk', 'en']) {
    await i18n.changeLanguage(language)
    const unavailable = render(CertificateListContent, { result: { enabled: false } })
    assert.ok(unavailable.includes(i18n.t('certificates.listUnavailable')))
    assert.ok(!unavailable.includes(i18n.t('certificates.empty')))
    const empty = render(CertificateListContent, { result: [] })
    assert.ok(empty.includes(i18n.t('certificates.empty')))
    assert.ok(!empty.includes(i18n.t('certificates.listUnavailable')))
    assert.ok(render(CertificateListContent, { result: null }).includes(i18n.t('common.loading')))
    const error = render(CertificateListContent, { result: null, error: true, refresh() {} })
    assert.match(error, /role="alert"/)
    assert.ok(error.includes(i18n.t('certificates.loadError')))
    assert.ok(error.includes(i18n.t('common.retry')))
  }
})
test('Profile maps issued and revoked legacy snapshots without requiring new certificate-name confirmation', () => {
  const certificate = { verification_code: 'synthetic-snapshot', course_title: 'Synthetic issued course', issued_at: '2026-10-27T05:00:00Z', revoked: false, verification_available: true }
  for (const revoked of [false, true]) {
    const html = render(CertificateListContent, { result: [{ ...certificate, revoked }] })
    assert.match(html, /Synthetic issued course/)
    assert.match(html, /\/certificates\/verify\/synthetic-snapshot/)
    assert.ok(html.includes(i18n.t(revoked ? 'certificates.status.revoked' : 'certificates.status.issued')))
    assert.ok(!html.includes(i18n.t('certificates.empty')))
  }
})


test('issued cards do not advertise public verification when the backend disables it', async () => {
  for (const language of ['ru', 'kk', 'en']) {
    await i18n.changeLanguage(language)
    const html = render(CertificateListContent, { result: [{ verification_code: 'synthetic-private', course_title: 'Stored course', issued_at: '2026-10-27T05:00:00Z', revoked: false, verification_available: false }] })
    assert.ok(html.includes(i18n.t('certificates.verificationUnavailable')))
    assert.doesNotMatch(html, /href="\/certificates\/verify/)
  }
})

test('preview and close-preview labels are available in all interface languages', async () => {
  for (const language of ['ru', 'kk', 'en']) {
    await i18n.changeLanguage(language)
    for (const key of ['preview', 'closePreview', 'verificationUnavailable']) {
      assert.notEqual(i18n.t(`certificates.${key}`), `certificates.${key}`)
    }
  }
})
