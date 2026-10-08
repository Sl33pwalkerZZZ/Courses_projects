import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { enrollmentErrorKey, latestCourseApplication, loadCourseEnrollment } from '../src/utils/enrollment.js'

function application(id, status, slug = 'ai', created_at = '2026-10-08T08:00:00Z') {
  return { id, status, course: { slug }, created_at }
}

function clientWith(enrollments, applications) {
  const calls = []
  return {
    calls,
    async get(url) {
      calls.push(url)
      const result = url === '/my/enrollments/' ? enrollments : applications
      if (result instanceof Error) throw result
      return { data: result }
    },
  }
}

test('latest application uses creation order and ID without changing the history', () => {
  const history = [application(3, 'rejected'), application(4, 'pending'), application(9, 'approved', 'other')]
  const original = structuredClone(history)
  assert.equal(latestCourseApplication(history, 'ai').id, 4)
  assert.deepEqual(history, original)
  assert.equal(latestCourseApplication(history, 'missing'), null)
  const newer = application(1, 'pending', 'ai', '2026-10-09T08:00:00Z')
  assert.equal(latestCourseApplication([...history, newer], 'ai').id, 1)
})

test('reload restores a pending reapplication instead of an older rejection', async () => {
  const history = [application(1, 'rejected'), application(2, 'pending')]
  const client = clientWith([], history)
  for (let reload = 0; reload < 2; reload++) {
    const state = await loadCourseEnrollment(client, 'ai', true)
    assert.equal(state.application.status, 'pending')
    assert.equal(state.application.id, 2)
    assert.equal(state.enrollment, null)
  }
})

test('rejection remains visible after reload and approved access retains its next lesson', async () => {
  const rejected = await loadCourseEnrollment(clientWith([], [application(1, 'rejected')]), 'ai', true)
  assert.equal(rejected.application.status, 'rejected')
  const enrollment = { id: 7, course: { slug: 'ai' }, next_lesson_id: 42, completed_lessons: 2 }
  const approved = await loadCourseEnrollment(clientWith([enrollment], [application(1, 'approved')]), 'ai', true)
  assert.deepEqual(approved.enrollment, enrollment)
  assert.equal(approved.application.status, 'approved')
})

test('another course enrollment or application never grants access to this course', async () => {
  const client = clientWith([{ id: 9, course: { slug: 'other' } }], [application(9, 'approved', 'other')])
  assert.deepEqual(await loadCourseEnrollment(client, 'ai', true), { enrollment: null, application: null })
})

test('confirmed enrollment remains available when application history fails', async () => {
  const enrollment = { id: 1, course: { slug: 'ai' }, next_lesson_id: 10 }
  const state = await loadCourseEnrollment(clientWith([enrollment], new Error('History unavailable')), 'ai', true)
  assert.deepEqual(state, { enrollment, application: null })
})

test('failed access or unknown application state does not pretend the student can apply', async () => {
  await assert.rejects(loadCourseEnrollment(clientWith([], new Error('History unavailable')), 'ai', true))
  await assert.rejects(loadCourseEnrollment(clientWith(new Error('Access unavailable'), []), 'ai', true))
})

test('open courses check enrollment without depending on the application endpoint', async () => {
  const client = clientWith([], new Error('This endpoint must not be called'))
  assert.deepEqual(await loadCourseEnrollment(client, 'ai', false), { enrollment: null, application: null })
  assert.deepEqual(client.calls, ['/my/enrollments/'])
})

test('server errors map to translated application messages', () => {
  const cases = [
    [{ status: 401 }, 'enrollment.sessionExpired'],
    [{ data: { code: 'duplicate_pending' } }, 'enrollment.duplicatePending'],
    [{ data: { code: 'already_enrolled' } }, 'enrollment.alreadyEnrolled'],
    [{ data: { code: 'open_enrollment' } }, 'enrollment.policyChanged'],
    [{ data: { code: 'approval_required' } }, 'enrollment.policyChanged'],
    [{ data: { message: ['Too short'] } }, 'enrollment.messageError'],
    [{ status: 500 }, 'enrollment.submitError'],
  ]
  for (const [response, expected] of cases) assert.equal(enrollmentErrorKey({ response }), expected)
  assert.equal(enrollmentErrorKey(new Error('Network error'), 'enrollment.loadError'), 'enrollment.loadError')
})

test('all application text and interpolation values are present in RU, KZ, and EN', async () => {
  const locales = await Promise.all(['ru', 'kk', 'en'].map(async (language) => JSON.parse(
    await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'),
  )))
  const keys = Object.keys(locales[2].enrollment).sort()
  for (const locale of locales) {
    assert.deepEqual(Object.keys(locale.enrollment).sort(), keys)
    for (const key of keys) {
      const text = locale.enrollment[key]
      if (typeof text === 'string') {
        assert.ok(text.trim(), key)
        assert.deepEqual(text.match(/{{\w+}}/g) || [], locales[2].enrollment[key].match(/{{\w+}}/g) || [], key)
      }
    }
    assert.deepEqual(Object.keys(locale.enrollment.status).sort(), ['approved', 'pending', 'rejected'])
    assert.ok(locale.profile.coursesTitle.trim())
  }
})
