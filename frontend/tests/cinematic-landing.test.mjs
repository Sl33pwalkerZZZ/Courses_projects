import assert from 'node:assert/strict'
import { before, after, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { createTestServer } from './helpers/vite.mjs'
let server, Showcase, Preview, Closing
before(async () => {
  server = await createTestServer()
  Showcase = (await server.ssrLoadModule('/src/components/landing/LearningShowcase.jsx')).default
  Preview = (await server.ssrLoadModule('/src/components/landing/LandingCoursePreview.jsx')).default
  Closing = (await server.ssrLoadModule('/src/components/landing/ClosingInvitation.jsx')).default
})
after(async () => { await server?.close() })
const course = { id: 901, slug: 'actual-public-course', title: 'Public course <script>', description: 'Actual description', author: 'Course author', level: 'beginner', direction: { name: 'Media', slug: 'media' } }
for (const lang of ['ru','kk','en']) {
  test(`course preview uses real fields and real links in ${lang}`, async () => {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${lang}.json`, import.meta.url)))
    const i18n = createInstance();await i18n.init({ lng: lang, resources: { [lang]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    const render=(component,props={})=>renderToStaticMarkup(createElement(I18nextProvider,{i18n},createElement(MemoryRouter,null,createElement(component,props))))
    const html=render(Showcase,{courses:[course]})
    assert.match(html,/Public course &lt;script&gt;/)
    assert.match(html,/Actual description/)
    assert.match(html,/href="\/courses\/actual-public-course"/)
    assert.match(html,/aria-pressed="true"/)
    assert.doesNotMatch(html,/cinema\.[a-z]|progress_percent|completed_lessons|<script>/)
    for(const props of [{loading:true},{failed:true},{}]) {
      const fallback=render(Preview,props)
      assert.match(fallback,/role="status"/)
      assert.doesNotMatch(fallback,/undefined|\/courses\//)
    }
    const closing=render(Closing)
    assert.match(closing,/href="#course-library"/)
    assert.match(closing,/href="\/register"/)
  })
}
