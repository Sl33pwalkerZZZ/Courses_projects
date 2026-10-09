import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { before, after, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createServer } from 'vite'
import { activityLevel, buildActivityGrid, loadLearningActivity, normalizeActivity } from '../src/utils/activity.js'

const now = new Date('2024-03-01T12:00:00Z')
function fixture(days = [], total = days.reduce((sum, day) => sum + day.count, 0)) {
  return { timezone: 'UTC', start_date: '2023-03-03', end_date: '2024-03-01',
    total_completed_lessons: total, active_days_last_365: days.filter((day) => day.count > 0).length,
    current_streak_days: 0, daily_counts: days }
}
const day = (date, count) => ({ date, count })
let server, Calendar, Panel, Sections
const dictionaries = new Map()

before(async () => {
  server = await createServer({ server: { middlewareMode: true, hmr: false, ws: false }, optimizeDeps: { noDiscovery: true, include: [] }, appType: 'custom' })
  Calendar = (await server.ssrLoadModule('/src/components/LearningActivityCalendar.jsx')).default
  Panel = (await server.ssrLoadModule('/src/components/ProfileLearningActivity.jsx')).LearningActivityPanel
  Sections = (await server.ssrLoadModule('/src/pages/Profile.jsx')).ProfileLearningSections
  for (const language of ['en', 'ru', 'kk']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    const instance = createInstance()
    await instance.init({ lng: language, resources: { [language]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    dictionaries.set(language, instance)
  }
})
after(async () => { await server?.close() })

function render(Component, props, language = 'en') {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: dictionaries.get(language) },
    createElement(MemoryRouter, null, createElement(Component, props)),
  ))
}

test('normalization creates 365 chronological dates and fills missing days with zero', () => {
  const activity = normalizeActivity(fixture([day('2024-02-29', 2)]), now)
  assert.equal(activity.daily_counts.length, 365)
  assert.equal(activity.daily_counts[0].date, '2023-03-03')
  assert.equal(activity.daily_counts.at(-1).date, '2024-03-01')
  assert.equal(activity.daily_counts.find((entry) => entry.date === '2024-02-29').count, 2)
  assert.equal(activity.daily_counts.filter((entry) => entry.count === 0).length, 364)
  assert.deepEqual(activity.daily_counts.map((entry) => entry.date), activity.daily_counts.map((entry) => entry.date).sort())
})

test('grid uses Monday rows, padded weeks, and includes leap day without future activity', () => {
  const activity = normalizeActivity(fixture([day('2024-02-29', 1)]), now)
  const grid = buildActivityGrid(activity)
  assert.equal(grid.weeks.length, 53)
  assert.deepEqual(grid.weeks[0].slice(0, 4), [null, null, null, null])
  assert.equal(grid.weeks[0][4].date, '2023-03-03')
  assert.equal(grid.weeks.at(-1)[4].date, '2024-03-01')
  assert.deepEqual(grid.weeks.at(-1).slice(5), [null, null])
  const dates = grid.weeks.flat().filter(Boolean).map((entry) => entry.date)
  assert.equal(new Set(dates).size, 365)
  assert.ok(dates.includes('2024-02-29'))
})

test('month labels align with the column containing the first date of each month', () => {
  const grid = buildActivityGrid(normalizeActivity(fixture(), now))
  const january = grid.months.find((month) => month.label === 'Jan')
  assert.ok(grid.weeks[january.column].some((day) => day?.date === '2024-01-01'))
  for (let index = 1; index < grid.months.length; index++) {
    assert.ok(grid.months[index].column - grid.months[index - 1].column >= 3)
  }
})

test('date arithmetic handles Sunday starts and year boundaries', () => {
  const activity = { ...fixture(), start_date: '2023-01-01', end_date: '2023-12-31' }
  const grid = buildActivityGrid(normalizeActivity(activity, now))
  assert.equal(grid.weeks[0][6].date, '2023-01-01')
  assert.equal(grid.weeks.at(-1)[6].date, '2023-12-31')
  assert.equal(grid.weeks.flat().filter(Boolean).length, 365)
})

test('activity intensities use fixed documented count thresholds', () => {
  for (const [count, expected] of [[0, 0], [1, 1], [2, 2], [3, 2], [4, 3], [7, 3], [8, 4], [100, 4]]) {
    assert.equal(activityLevel(count), expected)
  }
  for (const count of [-1, 1.5, NaN, '1']) assert.throws(() => activityLevel(count))
})

test('zero activity remains zero and all-time history is separate from the calendar', () => {
  const zero = normalizeActivity(fixture(), now)
  assert.equal(zero.total_completed_lessons, 0)
  assert.ok(buildActivityGrid(zero).weeks.flat().filter(Boolean).every((entry) => entry.level === 0))
  const historic = normalizeActivity(fixture([], 42), now)
  assert.equal(historic.total_completed_lessons, 42)
  assert.equal(historic.active_days_last_365, 0)
})

test('missing and malformed API responses are errors, not fake empty statistics', () => {
  for (const response of [null, {}, [], { ...fixture(), daily_counts: null }, { ...fixture(), timezone: '' },
    { ...fixture(), timezone: 'Invalid/Zone' }, { ...fixture(), start_date: '2023-02-30' },
    { ...fixture(), end_date: '2025-03-01' }, { ...fixture(), total_completed_lessons: '0' },
    { ...fixture(), active_days_last_365: -1 }, { ...fixture(), current_streak_days: 1 },
  ]) assert.throws(() => normalizeActivity(response, now))
})

test('invalid, duplicate, out-of-window, or future daily counts are rejected', () => {
  for (const days of [[day('2024-02-30', 1)], [day('2024-03-02', 1)], [day('2023-03-02', 1)],
    [day('2024-03-01', -1)], [day('2024-03-01', 1.5)], [day('2024-03-01', '2')],
    [day('2024-03-01', 1), day('2024-03-01', 1)], [null],
  ]) assert.throws(() => normalizeActivity({ ...fixture(), daily_counts: days }, now))
  assert.throws(() => normalizeActivity({ ...fixture([day('2024-03-01', 2)]), total_completed_lessons: 1 }, now))
})

test('future-date validation uses the API timezone rather than the browser timezone', () => {
  const data = { ...fixture(), timezone: 'Asia/Almaty' }
  assert.doesNotThrow(() => normalizeActivity(data, new Date('2024-02-29T19:30:00Z')))
  assert.throws(() => normalizeActivity({ ...data, timezone: 'UTC' }, new Date('2024-02-29T19:30:00Z')))
})

test('activity fetching uses the authenticated endpoint and validates its response', async () => {
  const paths = []
  const result = await loadLearningActivity({ get: async (path) => { paths.push(path); return { data: fixture() } } })
  assert.deepEqual(paths, ['/my/activity/'])
  assert.equal(result.daily_counts.length, 365)
  await assert.rejects(loadLearningActivity({ get: async () => ({ data: {} }) }))
})

test('activity request failures can be retried without touching other Profile APIs', async () => {
  let calls = 0
  const client = { get: async (path) => {
    assert.equal(path, '/my/activity/')
    if (++calls === 1) throw { response: { status: 500 } }
    return { data: fixture() }
  } }
  await assert.rejects(loadLearningActivity(client))
  assert.equal((await loadLearningActivity(client)).total_completed_lessons, 0)
  assert.equal(calls, 2)
})

test('calendar renders 365 labelled days, a single tab stop, and no interactive future padding', () => {
  const html = render(Calendar, { activity: normalizeActivity(fixture([day('2024-02-29', 2)]), now) })
  assert.equal((html.match(/class="activity-day"/g) || []).length, 365)
  assert.equal((html.match(/tabindex="0"/g) || []).length, 1)
  assert.match(html, /data-date="2024-02-29"/)
  assert.match(html, /February 29, 2024: 2 lessons completed/)
  assert.doesNotMatch(html, /data-date="2024-03-02"/)
  assert.match(html, /0<\/span>|2–3/)
})

test('activity loading and error displays never substitute zero statistics', () => {
  const loading = render(Panel, { loading: true })
  assert.match(loading, /role="status"/)
  assert.doesNotMatch(loading, /activity-statistics|activity-day/)
  const error = render(Panel, { error: true, onRetry: () => {} })
  assert.match(error, /role="alert"/)
  assert.ok(error.includes(dictionaries.get('en').t('common.retry')))
  assert.doesNotMatch(error, /activity-statistics|class="activity-day"/)
})

test('zero students get a real empty heatmap and historic-only students get an accurate message', () => {
  const html = render(Panel, { activity: normalizeActivity(fixture(), now) })
  assert.match(html, /No activity yet/)
  assert.equal((html.match(/class="activity-day" data-level="0"/g) || []).length, 365)
  assert.match(html, /All time/)
  const historic = render(Panel, { activity: normalizeActivity(fixture([], 42), now) })
  assert.match(historic, /No completions in the past 365 days/)
  assert.match(historic, />42<\/strong>/)
})

test('existing learning, progress, continue links, and application history remain rendered', () => {
  const html = render(Sections, { enrollments: [{ id: 7, course: {
    title: 'Existing course', slug: 'existing-course', description: 'Stored description', direction: { name: 'AI' }, author: 'Existing author', level: 'beginner',
  }, total_lessons: 4, completed_lessons: 1, progress_percent: 25, is_completed: false, next_lesson_id: 21, next_lesson_title: 'Existing lesson' }] })
  assert.match(html, /My learning/)
  assert.match(html, /My applications/)
  assert.match(html, /class="profile-progress-bar" max="100" value="25"/)
  assert.match(html, /href="\/lessons\/21"/)
  assert.match(html, /href="\/courses\/existing-course"/)
})

test('no enrollments preserves both course empty state and applications section', () => {
  const html = render(Sections, { enrollments: [] })
  assert.match(html, /Your next chapter starts here/)
  assert.match(html, /My applications/)
})

for (const language of ['en', 'ru', 'kk']) {
  test(`calendar, stats, empty messages, and plural labels are localized in ${language}`, () => {
    const instance = dictionaries.get(language)
    const html = render(Panel, { activity: normalizeActivity(fixture(), now) }, language)
    assert.ok(html.includes(instance.t('activity.title')))
    assert.ok(html.includes(instance.t('activity.noActivity')))
    assert.doesNotMatch(html, /activity\.[a-zA-Z]/)
    for (const count of [0, 1, 2, 5, 21]) {
      const label = instance.t('activity.dayDetails', { count, date: 'DATE' })
      assert.ok(label.includes(String(count)))
      assert.doesNotMatch(label, /dayDetails/)
    }
  })
}

test('Russian tooltip and streak units have correct plural forms', () => {
  const instance = dictionaries.get('ru')
  assert.equal(instance.t('activity.dayDetails', { count: 1, date: 'DATE' }), 'DATE: завершён 1 урок')
  assert.equal(instance.t('activity.dayDetails', { count: 2, date: 'DATE' }), 'DATE: завершено 2 урока')
  assert.equal(instance.t('activity.dayDetails', { count: 5, date: 'DATE' }), 'DATE: завершено 5 уроков')
  assert.equal(instance.t('activity.streakUnit', { count: 21 }), 'день подряд')
})
