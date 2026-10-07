import assert from 'node:assert/strict'
import test from 'node:test'
import axios, { AxiosError } from 'axios'

let instance = 0

function token(seconds) {
  const payload = Buffer.from(JSON.stringify({ exp: Math.floor(Date.now() / 1000) + seconds })).toString('base64url')
  return `header.${payload}.signature`
}

function response(config, data, status = 200) {
  return { config, data, status, statusText: '', headers: {} }
}

function fail(config, status = 401) {
  throw new AxiosError('Request failed', 'ERR_BAD_RESPONSE', config, null, response(config, { code: 'token_not_valid' }, status))
}

async function setup(tokens, handler) {
  const storage = new Map(Object.entries(tokens))
  globalThis.localStorage = {
    getItem: (key) => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: (key) => storage.delete(key),
  }
  globalThis.window = new EventTarget()
  const calls = []
  // Both Axios clients use this adapter, so tests make no network requests.
  axios.defaults.adapter = async (config) => {
    calls.push({ url: config.url, method: config.method, authorization: config.headers.Authorization, data: config.data })
    return handler(config)
  }
  const auth = await import(`../src/api.js?test=${++instance}`)
  return { ...auth, api: auth.default, storage, calls }
}

test('authentication requires a current access token or recoverable refresh token', async () => {
  for (const [tokens, expected] of [
    [{}, false],
    [{ access: token(300) }, true],
    [{ access: token(-60), refresh: token(3600) }, true],
    [{ refresh: token(3600) }, true],
    [{ access: token(-60), refresh: token(-60) }, false],
    [{ access: 'broken', refresh: 'broken' }, false],
  ]) {
    const auth = await setup(tokens, () => { throw new Error('No requests expected') })
    assert.equal(auth.isAuthenticated(), expected)
  }
})

test('expired access refreshes, saves the token, and retries the original request once', async () => {
  const fresh = token(300)
  const auth = await setup({ access: token(-60), refresh: token(3600) }, (config) => {
    if (config.url === '/auth/token/refresh/') {
      assert.equal(config.headers.Authorization, undefined)
      return response(config, { access: fresh })
    }
    if (config.headers.Authorization !== `Bearer ${fresh}`) fail(config)
    return response(config, { username: 'student' })
  })
  assert.equal((await auth.api.get('/auth/me/')).data.username, 'student')
  assert.equal(auth.storage.get('access'), fresh)
  assert.equal(auth.calls.filter((call) => call.url === '/auth/token/refresh/').length, 1)
  assert.equal(auth.calls.filter((call) => call.url === '/auth/me/').length, 2)
})

test('simultaneous 401s share one refresh request', async () => {
  const fresh = token(300)
  const auth = await setup({ access: token(-60), refresh: token(3600) }, async (config) => {
    if (config.url === '/auth/token/refresh/') {
      await new Promise((resolve) => setTimeout(resolve, 5))
      return response(config, { access: fresh })
    }
    if (config.headers.Authorization !== `Bearer ${fresh}`) fail(config)
    return response(config, [])
  })
  await Promise.all(['/auth/me/', '/my/enrollments/', '/courses/ai/reviews/'].map((url) => auth.api.get(url)))
  assert.equal(auth.calls.filter((call) => call.url === '/auth/token/refresh/').length, 1)
})

test('a late 401 for the old token reuses the refreshed token', async () => {
  const fresh = token(300)
  let releaseLateResponse
  const lateResponse = new Promise((resolve) => { releaseLateResponse = resolve })
  const auth = await setup({ access: token(-60), refresh: token(3600) }, async (config) => {
    if (config.url === '/auth/token/refresh/') return response(config, { access: fresh })
    if (config.headers.Authorization !== `Bearer ${fresh}`) {
      if (config.url === '/my/enrollments/') await lateResponse
      fail(config)
    }
    return response(config, [])
  })
  const late = auth.api.get('/my/enrollments/')
  await auth.api.get('/auth/me/')
  releaseLateResponse()
  await late
  assert.equal(auth.calls.filter((call) => call.url === '/auth/token/refresh/').length, 1)
})

test('failed refresh clears both tokens and notifies the UI', async () => {
  const auth = await setup({ access: token(-60), refresh: token(3600) }, (config) => fail(config))
  const states = []
  const unsubscribe = auth.subscribeAuth(() => states.push(auth.isAuthenticated()))
  try {
    await assert.rejects(auth.api.get('/auth/me/'), (error) => error.response.status === 401)
    assert.equal(auth.storage.size, 0)
    assert.equal(auth.isAuthenticated(), false)
    assert.deepEqual(states, [true, false])
  } finally {
    unsubscribe()
  }
})

for (const url of ['/courses/', '/courses/ai/', '/courses/ai/reviews/']) {
  test(`public read ${url} retries anonymously when refresh fails`, async () => {
    const auth = await setup({ access: token(-60), refresh: token(3600) }, (config) => {
      if (config.url === '/auth/token/refresh/' || config.headers.Authorization) fail(config)
      return response(config, { public: true })
    })
    assert.equal((await auth.api.get(url)).data.public, true)
    assert.equal(auth.storage.size, 0)
    assert.equal(auth.calls.filter((call) => call.url === url).length, 2)
    assert.equal(auth.calls.at(-1).authorization, undefined)
  })
}

test('expired or malformed stored credentials do not block public requests', async () => {
  for (const tokens of [
    { access: token(-60), refresh: token(-60) },
    { access: 'broken', refresh: 'broken' },
  ]) {
    const auth = await setup(tokens, (config) => {
      assert.equal(config.headers.Authorization, undefined)
      return response(config, [])
    })
    await auth.api.get('/courses/')
    assert.equal(auth.storage.size, 0)
    assert.equal(auth.calls.length, 1)
  }
})

test('a second 401 stops retries and ends the failed session', async () => {
  const auth = await setup({ access: token(-60), refresh: token(3600) }, (config) => {
    if (config.url === '/auth/token/refresh/') return response(config, { access: token(300) })
    fail(config)
  })
  await assert.rejects(auth.api.get('/auth/me/'), (error) => error.response.status === 401)
  assert.equal(auth.calls.length, 3)
  assert.equal(auth.storage.size, 0)
})

test('a refresh-only session can recover a protected request', async () => {
  const fresh = token(300)
  const auth = await setup({ refresh: token(3600) }, (config) => {
    if (config.url === '/auth/token/refresh/') return response(config, { access: fresh })
    if (!config.headers.Authorization) fail(config)
    return response(config, [])
  })
  await auth.api.get('/my/enrollments/')
  assert.equal(auth.storage.get('access'), fresh)
})

test('missing refresh token clears rejected credentials and allows a public read', async () => {
  const auth = await setup({ access: token(300) }, (config) => {
    if (config.headers.Authorization) fail(config)
    return response(config, [])
  })
  await auth.api.get('/courses/')
  assert.equal(auth.storage.size, 0)
  assert.equal(auth.calls.length, 2)
})

test('failed refresh never retries a protected write anonymously', async () => {
  const auth = await setup({ access: token(-60), refresh: token(3600) }, (config) => fail(config))
  await assert.rejects(auth.api.post('/courses/ai/reviews/', { rating: 5, text: 'Useful' }))
  assert.equal(auth.calls.filter((call) => call.url === '/courses/ai/reviews/').length, 1)
})

test('server errors other than 401 do not refresh or clear the session', async () => {
  const auth = await setup({ access: token(300), refresh: token(3600) }, (config) => fail(config, 500))
  await assert.rejects(auth.api.get('/auth/me/'), (error) => error.response.status === 500)
  assert.equal(auth.calls.length, 1)
  assert.equal(auth.isAuthenticated(), true)
})

test('invalid login credentials do not trigger refresh', async () => {
  const auth = await setup({}, (config) => fail(config))
  await assert.rejects(auth.login('student', 'wrong'), (error) => error.response.status === 401)
  assert.equal(auth.calls.length, 1)
  assert.equal(auth.calls[0].url, '/auth/token/')
})

test('registration and login use clean auth requests and publish session changes', async () => {
  const auth = await setup({}, (config) => {
    assert.equal(config.headers.Authorization, undefined)
    return response(config, config.url === '/auth/register/' ? {} : { access: token(300), refresh: token(3600) })
  })
  const states = []
  const unsubscribe = auth.subscribeAuth(() => states.push(auth.isAuthenticated()))
  try {
    await auth.register('student', '', 'password')
    assert.equal(auth.isAuthenticated(), true)
    auth.logout()
    assert.deepEqual(states, [false, true, false])
    assert.deepEqual(auth.calls.map((call) => call.url), ['/auth/register/', '/auth/token/'])
  } finally {
    unsubscribe()
  }
})

test('logout during refresh cannot restore the old session', async () => {
  let finishRefresh
  let startedRefresh
  const started = new Promise((resolve) => { startedRefresh = resolve })
  const pending = new Promise((resolve) => { finishRefresh = resolve })
  const auth = await setup({ access: token(-60), refresh: token(3600) }, async (config) => {
    if (config.url === '/auth/token/refresh/') {
      startedRefresh()
      await pending
      return response(config, { access: token(300) })
    }
    fail(config)
  })
  const request = auth.api.get('/auth/me/')
  const rejected = assert.rejects(request)
  await started
  auth.logout()
  finishRefresh()
  await rejected
  assert.equal(auth.storage.size, 0)
})

test('an old protected request is not replayed as a newly signed-in user', async () => {
  let releaseOldRequest
  let startedOldRequest
  const started = new Promise((resolve) => { startedOldRequest = resolve })
  const pending = new Promise((resolve) => { releaseOldRequest = resolve })
  const fresh = token(600)
  const auth = await setup({ access: token(300), refresh: token(3600) }, async (config) => {
    if (config.url === '/auth/token/') return response(config, { access: fresh, refresh: token(7200) })
    startedOldRequest()
    await pending
    fail(config)
  })
  const request = auth.api.post('/courses/ai/reviews/', { rating: 5, text: 'Useful' })
  const rejected = assert.rejects(request)
  await started
  await auth.login('another-student', 'password')
  releaseOldRequest()
  await rejected
  assert.equal(auth.storage.get('access'), fresh)
  assert.equal(auth.calls.filter((call) => call.url === '/courses/ai/reviews/').length, 1)
})

test('authentication subscribers update when the last usable token expires', async (context) => {
  context.mock.timers.enable({ apis: ['Date', 'setTimeout'], now: 1800000000000 })
  const auth = await setup({ access: token(1) }, () => { throw new Error('No requests expected') })
  const states = []
  const unsubscribe = auth.subscribeAuth(() => states.push(auth.isAuthenticated()))
  try {
    context.mock.timers.tick(1001)
    assert.deepEqual(states, [true, false])
  } finally {
    unsubscribe()
  }
})
