import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { before, after, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'

let server, CourseCard, Filters, State, Skeleton, Workflow, Footer, StudioFooter
const translations = new Map()
const course = {
  id: 990001, slug: 'fixture-course', title: 'A complete and deliberately long course title that must remain readable',
  description: 'Synthetic course material remains complete and comes from the supplied API response.',
  author: 'Fixture author', direction: { slug: 'ai-foundations', name: 'AI Foundations' },
  level: 'beginner', average_rating: 4.5, review_count: 2,
}

before(async () => {
  server = await createTestServer()
  CourseCard = (await server.ssrLoadModule('/src/components/CourseCard.jsx')).default
  Filters = (await server.ssrLoadModule('/src/components/CatalogFilters.jsx')).default
  const states = await server.ssrLoadModule('/src/components/CatalogState.jsx')
  State = states.CatalogState
  Skeleton = states.CatalogSkeleton
  Workflow = (await server.ssrLoadModule('/src/components/LearningWorkflow.jsx')).default
  const footer = await server.ssrLoadModule('/src/components/Footer.jsx')
  Footer = footer.default
  StudioFooter = footer.StudioFooter
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
  test(`course card preserves API content, one named link and real reviews in ${lang}`, () => {
    const html = render(CourseCard, { course }, lang)
    assert.ok(html.includes(course.title) && html.includes(course.description) && html.includes(course.author))
    assert.match(html, /href="\/courses\/fixture-course"/)
    assert.match(html, /aria-labelledby="course-title-990001"/)
    assert.equal((html.match(/<a /g) || []).length, 1)
    assert.doesNotMatch(html, /<button|art-circle|art-caption|perspective/)
    const rating = new Intl.NumberFormat(lang, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(4.5)
    assert.ok(html.includes(translations.get(lang).t('reviews.ratingOutOfFive', { rating })))
    assert.ok(html.includes(translations.get(lang).t('reviews.count', { count: 2 })))
    assert.doesNotMatch(html, /studio\.[a-zA-Z]|reviews\.[a-zA-Z]/)
  })

  test(`filter controls remain named, controlled and use the actual directions in ${lang}`, () => {
    const html = render(Filters, { search: 'Actual search', direction: 'ai-foundations', level: 'beginner',
      directions: [course.direction], hasFilters: true, onReset() {}, onSearchChange() {}, onLevelChange() {}, onDirectionChange() {} }, lang)
    for (const id of ['course-search', 'course-direction', 'course-level']) {
      assert.ok(html.includes(`for="${id}"`) && html.includes(`id="${id}"`))
    }
    assert.match(html, /value="Actual search"/)
    assert.match(html, /value="ai-foundations" selected=""/)
    assert.match(html, /value="beginner" selected=""/)
    assert.ok(html.includes(`aria-label="${translations.get(lang).t('filters.reset')}"`))
    assert.doesNotMatch(html, /filters\.[a-zA-Z]|studio\.[a-zA-Z]/)
  })

  test(`empty, filtered and error states have correct recovery actions in ${lang}`, () => {
    const empty = render(State, { kind: 'empty' }, lang)
    assert.doesNotMatch(empty, /<button|role="alert"/)
    const filtered = render(State, { kind: 'filtered', onAction() {} }, lang)
    assert.ok(filtered.includes(translations.get(lang).t('common.reset')))
    assert.doesNotMatch(filtered, /role="alert"/)
    const error = render(State, { kind: 'error', onAction() {} }, lang)
    assert.match(error, /role="alert"/)
    assert.ok(error.includes(translations.get(lang).t('common.retry')))
    for (const html of [empty, filtered, error]) assert.doesNotMatch(html, /studio\.[a-zA-Z]|catalog\.[a-zA-Z]/)
  })

  test(`workflow explains conditional enrollment and public footer preserves navigation in ${lang}`, () => {
    const workflow = render(Workflow, {}, lang)
    assert.match(workflow, /id="learning-workflow"/)
    assert.equal((workflow.match(/<li /g) || []).length, 3)
    assert.ok(workflow.includes(translations.get(lang).t('studio.workflow.access.description')))
    const footer = render(StudioFooter, { authed: false }, lang)
    assert.match(footer, /href="#course-library"/)
    assert.match(footer, /href="#learning-workflow"/)
    assert.match(footer, /href="\/login"/)
    assert.doesNotMatch(footer, /href="\/profile"|language-switcher|footer-decoration/)
    assert.ok(footer.includes(translations.get(lang).t('footer.project')))
    assert.doesNotMatch(workflow + footer, /studio\.[a-zA-Z]/)
  })
}

test('subject identity remains stable when courses move after filtering or language changes', () => {
  const symbol = (html) => html.match(/studio-subject--\d/)[0]
  const first = symbol(render(CourseCard, { course, index: 0 }))
  assert.equal(symbol(render(CourseCard, { course, index: 5 })), first)
  assert.equal(symbol(render(CourseCard, { course, index: 3 }, 'kk')), first)
})

test('unreviewed courses never show fabricated ratings', () => {
  const html = render(CourseCard, { course: { ...course, review_count: 0, average_rating: null } })
  assert.ok(html.includes(translations.get('en').t('reviews.noReviews')))
  assert.doesNotMatch(html, /card-rating-value/)
})

test('loading skeletons are decorative and do not contain fake course links', () => {
  const html = render(Skeleton)
  assert.match(html, /aria-hidden="true"/)
  assert.equal((html.match(/course-skeleton/g) || []).length, 3)
  assert.doesNotMatch(html, /<a |<button/)
})

test('footer keeps authenticated destination and the deferred-route footer stays unchanged', () => {
  const authed = render(StudioFooter, { authed: true })
  assert.match(authed, /href="\/profile"/)
  assert.doesNotMatch(authed, /href="\/login"/)
  const legacy = render(Footer)
  assert.match(legacy, /footer-decoration/)
  assert.doesNotMatch(legacy, /studio-footer/)
})
