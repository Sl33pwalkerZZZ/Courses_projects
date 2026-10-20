import assert from 'node:assert/strict'
import test from 'node:test'
import { createInstructorIdentityStore, canEnterStudio } from '../src/utils/instructorIdentity.js'

function deferred() { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no }); return { promise, resolve, reject } }
const author = { id: 1, role: 'author', effective_role: 'author', can_access_studio: true, is_moderator: false }
const student = { id: 2, role: 'student', effective_role: 'student', can_access_studio: false, is_moderator: false }
test('student identity and staff display flags do not grant studio capabilities', () => {
  assert.equal(canEnterStudio(student), false)
  assert.equal(canEnterStudio({ ...student, is_staff: true }), false)
  assert.equal(canEnterStudio({ role: 'admin', is_superuser: true }), false)
  assert.equal(canEnterStudio(author), true)
  assert.equal(canEnterStudio({ ...student, effective_role: 'admin', can_access_studio: true, authority_source: 'superuser' }), true)
})
test('initial identity flights are shared; normal refresh preserves snapshot until resolved', async () => {
  let calls = 0, time = 1000
  const request = deferred()
  const store = createInstructorIdentityStore(() => { calls++; return request.promise }, () => time)
  const first = store.refresh(1), second = store.refresh(1)
  await Promise.resolve()
  assert.equal(calls, 1)
  request.resolve(author)
  await Promise.all([first, second])
  const snapshot = store.getSnapshot(1)
  assert.equal(snapshot.identity, author)
  await store.refresh(1)
  assert.equal(store.getSnapshot(1), snapshot)
  assert.equal(calls, 1)
  time += 16000
  await store.refresh(1)
  assert.equal(calls, 2)
})
test('account switch hides A immediately and ignores A response after B', async () => {
  const a = deferred(), b = deferred()
  const queue = [a, b]
  const store = createInstructorIdentityStore(() => queue.shift().promise)
  const first = store.refresh(1)
  await Promise.resolve()
  assert.equal(store.getSnapshot(2).identity, null)
  const second = store.refresh(2)
  await Promise.resolve()
  b.resolve(student)
  await second
  a.resolve(author)
  await first
  assert.equal(store.getSnapshot(2).identity, student)
  assert.equal(store.getSnapshot(1).identity, null)
})
test('logout discards in-flight privileged identity', async () => {
  const request = deferred()
  const store = createInstructorIdentityStore(() => request.promise)
  const pending = store.refresh(1)
  await Promise.resolve()
  await store.refresh(null)
  request.resolve(author)
  await pending
  assert.equal(store.getSnapshot(null).identity, null)
})
test('same-user permission revalidation revokes UI access without replacing JWT session', async () => {
  let identity = author
  const store = createInstructorIdentityStore(async () => identity)
  await store.refresh(1)
  identity = { ...student, id: author.id }
  await store.refresh(1, true)
  assert.equal(canEnterStudio(store.getSnapshot(1).identity), false)
})
test('failed or forbidden permission refresh removes cached privileged data and allows retry', async () => {
  let load = async () => author
  const store = createInstructorIdentityStore(() => load())
  await store.refresh(1)
  load = async () => { throw { response: { status: 403 } } }
  await store.refresh(1, true)
  assert.equal(store.getSnapshot(1).identity, null)
  assert.equal(store.getSnapshot(1).checked, true)
  assert.equal(store.getSnapshot(1).error, false)
  load = async () => { throw new Error('Offline') }
  await store.refresh(1, true)
  assert.equal(store.getSnapshot(1).error, true)
  load = async () => author
  await store.refresh(1, true)
  assert.equal(store.getSnapshot(1).identity, author)
})
