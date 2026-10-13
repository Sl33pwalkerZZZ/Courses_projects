import assert from 'node:assert/strict'
import { test } from 'node:test'
import { loadLessonImage } from '../src/utils/lessonImages.js'

const imageBlob = () => new Blob(['image bytes'], { type: 'image/png' })

function harness(client, id = 15) {
  const loaded = [], errors = [], created = [], revoked = []
  const request = loadLessonImage(client, id,
    (src) => loaded.push(src), (error) => errors.push(error), {
      createObjectURL(blob) { created.push(blob); return 'blob:protected-image' },
      revokeObjectURL(src) { revoked.push(src) },
    },
  )
  return { request, loaded, errors, created, revoked }
}

test('private images use the supplied authenticated client with blob response and cancellation', async () => {
  const calls = []
  const blob = imageBlob()
  const state = harness({ async get(path, options) {
    calls.push({ path, options })
    return { data: blob }
  } })
  await state.request.promise
  assert.equal(calls[0].path, '/lesson-images/15/')
  assert.equal(calls[0].options.responseType, 'blob')
  assert.ok(calls[0].options.signal instanceof AbortSignal)
  assert.deepEqual(state.loaded, ['blob:protected-image'])
  assert.deepEqual(state.created, [blob])
  assert.deepEqual(state.errors, [])
  state.request.dispose()
  assert.equal(calls[0].options.signal.aborted, true)
  assert.deepEqual(state.revoked, ['blob:protected-image'])
  state.request.dispose()
  assert.equal(state.revoked.length, 1)
})

test('401, 403, 404, network, and server failures never create an image URL', async () => {
  for (const failure of [new Error('Offline'), ...[401, 403, 404, 500].map((status) => ({ response: { status } }))]) {
    const state = harness({ async get() { throw failure } })
    await state.request.promise
    assert.deepEqual(state.errors, [failure])
    assert.deepEqual(state.loaded, [])
    assert.deepEqual(state.created, [])
    state.request.dispose()
  }
})

test('invalid image IDs cannot become URLs or send credentials to another host', async () => {
  for (const id of ['https://untrusted.test/image', '../other-file', 0, -1, 1.5, '15', null]) {
    let calls = 0
    const state = harness({ async get() { calls++; return { data: imageBlob() } } }, id)
    await state.request.promise
    assert.equal(calls, 0)
    assert.equal(state.errors.length, 1)
    assert.deepEqual(state.created, [])
  }
})

test('non-image, empty, or malformed successful responses remain errors', async () => {
  for (const data of [{}, 'image', new Blob(['denied'], { type: 'application/json' }), new Blob([], { type: 'image/png' })]) {
    const state = harness({ async get() { return { data } } })
    await state.request.promise
    assert.equal(state.errors.length, 1)
    assert.deepEqual(state.loaded, [])
    assert.deepEqual(state.created, [])
  }
})

test('unmount or image replacement aborts pending requests and ignores late success', async () => {
  let finish, signal
  const state = harness({ get(_path, options) {
    signal = options.signal
    return new Promise((resolve) => { finish = resolve })
  } })
  state.request.dispose()
  assert.equal(signal.aborted, true)
  finish({ data: imageBlob() })
  await state.request.promise
  assert.deepEqual(state.loaded, [])
  assert.deepEqual(state.errors, [])
  assert.deepEqual(state.created, [])
  assert.deepEqual(state.revoked, [])
})

test('late rejected requests after cleanup do not update the unmounted component', async () => {
  let reject
  const state = harness({ get() { return new Promise((_resolve, fail) => { reject = fail }) } })
  state.request.dispose()
  reject(new Error('Canceled'))
  await state.request.promise
  assert.deepEqual(state.errors, [])
  assert.deepEqual(state.loaded, [])
})
