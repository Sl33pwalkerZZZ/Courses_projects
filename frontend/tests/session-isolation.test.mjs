import assert from 'node:assert/strict'
import test from 'node:test'
import axios, { AxiosError } from 'axios'

let instance = 0
let tokenNumber = 0

function token(userId, seconds = 300) {
  const payload = Buffer.from(JSON.stringify({
    user_id: userId,
    exp: Math.floor(Date.now() / 1000) + seconds,
    jti: `test-${++tokenNumber}`,
  })).toString('base64url')
  return `header.${payload}.signature`
}

function credentials(userId, seconds = 300) {
  return { access: token(userId, seconds), refresh: token(userId, 3600) }
}

function response(config, data, status = 200) {
  return { config, data, status, statusText: '', headers: {} }
}

function fail(config, status = 401) {
  throw new AxiosError('Request failed', 'ERR_BAD_RESPONSE', config, null, response(config, { code: 'token_not_valid' }, status))
}

function deferred() {
  let resolve
  const promise = new Promise((finish) => { resolve = finish })
  return { promise, resolve }
}

async function setup(tokens = {}, handler = () => { throw new Error('Unexpected request') }) {
  const storage = new Map(Object.entries(tokens))
  globalThis.localStorage = {
    getItem: (key) => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, String(value)),
    removeItem: (key) => storage.delete(key),
  }
  globalThis.window = new EventTarget()
  const calls = []
  // Both clients use an in-memory adapter: no real accounts, requests, or DB writes.
  axios.defaults.adapter = async (config) => {
    calls.push({ url: config.url, method: config.method, authorization: config.headers.Authorization })
    return handler(config)
  }
  const auth = await import(`../src/api.js?sessiontest=${++instance}`)
  function storageEvent(key) {
    const event = new Event('storage')
    Object.defineProperty(event, 'key', { value: key })
    window.dispatchEvent(event)
  }
  function otherTabLogin(userId) {
    const next = credentials(userId)
    storage.set('access', next.access)
    storage.set('refresh', next.refresh)
    storage.set('auth-session', `other-tab-${instance}-${userId}`)
    storageEvent('auth-session')
    return next
  }
  return { ...auth, api: auth.default, storage, calls, storageEvent, otherTabLogin }
}

function canceled(error) {
  return error.code === 'ERR_CANCELED'
}

test('normal login publishes a token-free session snapshot and logout clears credentials', async () => {
  const pair = credentials(1)
  const auth = await setup({}, (config) => response(config, pair))
  const initial = auth.getAuthSession()
  assert.equal(initial.authenticated, false)
  assert.equal(auth.getAuthSession(), initial)
  await auth.login('account-a', 'test-password')
  const loggedIn = auth.getAuthSession()
  assert.equal(loggedIn.authenticated, true)
  assert.notEqual(loggedIn.generation, initial.generation)
  assert.ok(auth.storage.get('auth-session'))
  assert.deepEqual(Object.keys(loggedIn).sort(), ['authenticated', 'generation'])
  assert.equal(JSON.stringify(loggedIn).includes(pair.access), false)
  auth.logout()
  assert.equal(auth.isAuthenticated(), false)
  assert.notEqual(auth.getAuthSession().generation, loggedIn.generation)
  for (const key of ['access', 'refresh', 'auth-session']) assert.equal(auth.storage.has(key), false)
})

test('a successful same-tab account switch changes the session while staying authenticated', async () => {
  const auth = await setup(credentials(1), (config) => response(config, credentials(2)))
  const accountA = auth.getAuthSession()
  await auth.login('account-b', 'test-password')
  const accountB = auth.getAuthSession()
  assert.equal(accountA.authenticated, true)
  assert.equal(accountB.authenticated, true)
  assert.notEqual(accountB.generation, accountA.generation)
})

test('failed login preserves the existing account session', async () => {
  const auth = await setup(credentials(1), (config) => fail(config))
  const before = auth.getAuthSession()
  const access = auth.storage.get('access')
  await assert.rejects(auth.login('account-b', 'wrong-password'), (error) => error.response?.status === 401)
  assert.equal(auth.getAuthSession(), before)
  assert.equal(auth.storage.get('access'), access)
  assert.equal(auth.calls.length, 1)
})

test('cross-tab account switching notifies subscribers even when authentication stays true', async () => {
  const auth = await setup(credentials(1))
  const accountA = auth.getAuthSession()
  const seen = []
  const unsubscribe = auth.subscribeAuth(() => seen.push(auth.getAuthSession()))
  try {
    auth.otherTabLogin(2)
    const accountB = auth.getAuthSession()
    assert.equal(accountB.authenticated, true)
    assert.notEqual(accountB.generation, accountA.generation)
    assert.equal(seen.at(-1), accountB)
  } finally { unsubscribe() }
})

test('cross-tab token replacement detects a different account even without a session marker', async () => {
  const auth = await setup(credentials(1))
  const accountA = auth.getAuthSession()
  const next = credentials(2)
  auth.storage.set('access', next.access)
  auth.storage.set('refresh', next.refresh)
  auth.storageEvent('access')
  assert.equal(auth.getAuthSession().authenticated, true)
  assert.notEqual(auth.getAuthSession().generation, accountA.generation)
})

test('cross-tab logout and storage.clear end the session', async () => {
  for (const clearAll of [false, true]) {
    const auth = await setup({ ...credentials(1), 'auth-session': 'tab-a' })
    const accountA = auth.getAuthSession()
    const seen = []
    const unsubscribe = auth.subscribeAuth(() => seen.push(auth.getAuthSession()))
    try {
      if (clearAll) auth.storage.clear()
      else for (const key of ['access', 'refresh', 'auth-session']) auth.storage.delete(key)
      auth.storageEvent(clearAll ? null : 'auth-session')
      assert.equal(auth.isAuthenticated(), false)
      assert.notEqual(auth.getAuthSession().generation, accountA.generation)
      assert.equal(seen.at(-1).authenticated, false)
    } finally { unsubscribe() }
  }
})

for (const status of [200, 500, 401]) {
  for (const method of ['get', 'post']) {
    test(`obsolete account A ${method.toUpperCase()} response ${status} is canceled without replay as B`, async () => {
      const started = deferred()
      const release = deferred()
      const auth = await setup(credentials(1), async (config) => {
        started.resolve()
        await release.promise
        if (status !== 200) fail(config, status)
        return response(config, { owner: 'account-a' })
      })
      const request = method === 'get'
        ? auth.api.get('/my/enrollments/')
        : auth.api.post('/lessons/15/complete/', {})
      const rejected = assert.rejects(request, canceled)
      await started.promise
      const accountB = auth.otherTabLogin(2)
      release.resolve()
      await rejected
      assert.equal(auth.calls.length, 1)
      assert.equal(auth.storage.get('access'), accountB.access)
      assert.equal(auth.isAuthenticated(), true)
    })
  }
}

test('logout cancels an in-flight successful private response', async () => {
  const started = deferred()
  const release = deferred()
  const auth = await setup(credentials(1), async (config) => {
    started.resolve()
    await release.promise
    return response(config, { private: true })
  })
  const rejected = assert.rejects(auth.api.get('/auth/me/'), canceled)
  await started.promise
  auth.logout()
  release.resolve()
  await rejected
  assert.equal(auth.isAuthenticated(), false)
})

test('same-account refresh and refresh-token rotation preserve the session generation', async () => {
  const fresh = credentials(1)
  const auth = await setup(credentials(1, -30), (config) => {
    if (config.url === '/auth/token/refresh/') return response(config, fresh)
    if (config.headers.Authorization !== `Bearer ${fresh.access}`) fail(config)
    return response(config, { owner: 'account-a' })
  })
  const before = auth.getAuthSession()
  const marker = auth.storage.get('auth-session')
  assert.equal((await auth.api.get('/auth/me/')).data.owner, 'account-a')
  assert.equal(auth.getAuthSession(), before)
  assert.equal(auth.storage.get('refresh'), fresh.refresh)
  assert.equal(auth.storage.get('auth-session'), marker)
  assert.equal(auth.calls.filter((call) => call.url === '/auth/token/refresh/').length, 1)
})

test('same-account refresh in another tab preserves the cached session snapshot', async () => {
  const auth = await setup({ ...credentials(1), 'auth-session': 'unchanged-sign-in' })
  const before = auth.getAuthSession()
  const next = credentials(1)
  auth.storage.set('access', next.access)
  auth.storage.set('refresh', next.refresh)
  auth.storageEvent('access')
  auth.storageEvent('refresh')
  assert.equal(auth.getAuthSession(), before)
  assert.equal(auth.isAuthenticated(), true)
})

test('concurrent same-account expired requests share one refresh', async () => {
  const fresh = token(1)
  const refreshStarted = deferred()
  const release = deferred()
  const auth = await setup(credentials(1, -30), async (config) => {
    if (config.url === '/auth/token/refresh/') {
      refreshStarted.resolve()
      await release.promise
      return response(config, { access: fresh })
    }
    if (config.headers.Authorization !== `Bearer ${fresh}`) fail(config)
    return response(config, [])
  })
  const pending = Promise.all([auth.api.get('/auth/me/'), auth.api.get('/my/enrollments/')])
  await refreshStarted.promise
  release.resolve()
  await pending
  assert.equal(auth.calls.filter((call) => call.url === '/auth/token/refresh/').length, 1)
})

for (const oldRefreshSucceeds of [true, false]) {
  test(`B can refresh while obsolete A refresh ${oldRefreshSucceeds ? 'succeeds' : 'fails'} without restoring or clearing B`, async () => {
    const pairA = credentials(1, -30)
    const pairB = credentials(2)
    const freshB = token(2)
    const startedA = deferred()
    const releaseA = deferred()
    const auth = await setup(pairA, async (config) => {
      if (config.url === '/auth/token/') return response(config, pairB)
      if (config.url === '/auth/token/refresh/') {
        const submitted = JSON.parse(config.data).refresh
        if (submitted === pairA.refresh) {
          startedA.resolve()
          await releaseA.promise
          if (!oldRefreshSucceeds) fail(config)
          return response(config, { access: token(1) })
        }
        assert.equal(submitted, pairB.refresh)
        return response(config, { access: freshB })
      }
      if (config.headers.Authorization !== `Bearer ${freshB}`) fail(config)
      return response(config, { owner: 'account-b' })
    })
    const oldRejected = assert.rejects(auth.api.get('/auth/me/'), canceled)
    await startedA.promise
    await auth.login('account-b', 'test-password')
    const sessionB = auth.getAuthSession()
    // B must recover independently, not wait on or reuse A's refresh promise.
    assert.equal((await auth.api.get('/my/enrollments/')).data.owner, 'account-b')
    releaseA.resolve()
    await oldRejected
    assert.equal(auth.storage.get('access'), freshB)
    assert.equal(auth.getAuthSession(), sessionB)
    assert.equal(auth.isAuthenticated(), true)
  })
}

test('failed refresh ends the current session and never retries protected writes anonymously', async () => {
  const auth = await setup(credentials(1, -30), (config) => fail(config))
  await assert.rejects(auth.api.post('/lessons/15/complete/', {}), (error) => error.response?.status === 401)
  assert.equal(auth.isAuthenticated(), false)
  for (const key of ['access', 'refresh', 'auth-session']) assert.equal(auth.storage.has(key), false)
  assert.equal(auth.calls.filter((call) => call.url === '/lessons/15/complete/').length, 1)
})

test('failed refresh allows exactly one anonymous public read retry', async () => {
  const auth = await setup(credentials(1, -30), (config) => {
    if (config.url === '/auth/token/refresh/' || config.headers.Authorization) fail(config)
    return response(config, { public: true })
  })
  assert.equal((await auth.api.get('/courses/ai/reviews/')).data.public, true)
  assert.equal(auth.calls.filter((call) => call.url === '/courses/ai/reviews/').length, 2)
  assert.equal(auth.calls.at(-1).authorization, undefined)
  assert.equal(auth.isAuthenticated(), false)
})

for (const url of ['/courses/?search=ai', '/courses/ai-fundamentals-work-study/']) {
  for (const method of ['get', 'head']) {
    test(`public ${method.toUpperCase()} ${url} never attaches JWTs or refreshes`, async () => {
      const auth = await setup(credentials(1, -30), (config) => {
        assert.equal(config.url, url)
        assert.equal(config.headers.Authorization, undefined)
        return response(config, { public: true })
      })
      const before = auth.getAuthSession()
      assert.equal((await auth.api[method](url)).data.public, true)
      assert.equal(auth.calls.length, 1)
      assert.equal(auth.getAuthSession(), before)
    })
  }
  test(`pending public ${url} remains usable after an account switch`, async () => {
    const started = deferred()
    const release = deferred()
    const auth = await setup(credentials(1), async (config) => {
      assert.equal(config.headers.Authorization, undefined)
      started.resolve()
      await release.promise
      return response(config, { title: 'Public course content' })
    })
    const pending = auth.api.get(url)
    await started.promise
    const accountB = auth.otherTabLogin(2)
    release.resolve()
    assert.equal((await pending).data.title, 'Public course content')
    assert.equal(auth.calls.length, 1)
    assert.equal(auth.storage.get('access'), accountB.access)
  })
}

test('a public course 401 does not refresh or end the signed-in session', async () => {
  const auth = await setup(credentials(1), (config) => {
    assert.equal(config.url, '/courses/')
    assert.equal(config.headers.Authorization, undefined)
    fail(config)
  })
  const before = auth.getAuthSession()
  await assert.rejects(auth.api.get('/courses/'), (error) => error.response?.status === 401)
  assert.equal(auth.calls.length, 1)
  assert.equal(auth.getAuthSession(), before)
})

test('personalized review responses remain isolated from the next account', async () => {
  const started = deferred()
  const release = deferred()
  const auth = await setup(credentials(1), async (config) => {
    assert.ok(config.headers.Authorization)
    started.resolve()
    await release.promise
    return response(config, { my_review: { text: 'Account A private review' } })
  })
  const rejected = assert.rejects(auth.api.get('/courses/ai/reviews/'), canceled)
  await started.promise
  auth.otherTabLogin(2)
  release.resolve()
  await rejected
  assert.equal(auth.calls.length, 1)
})

test('expired credentials are discarded and public requests stay usable', async () => {
  const auth = await setup({ access: token(1, -30), refresh: token(1, -30), 'auth-session': 'expired' }, (config) => {
    assert.equal(config.headers.Authorization, undefined)
    return response(config, [])
  })
  assert.equal(auth.isAuthenticated(), false)
  await auth.api.get('/courses/')
  assert.equal(auth.calls.length, 1)
  for (const key of ['access', 'refresh', 'auth-session']) assert.equal(auth.storage.has(key), false)
})

test('subscribers are notified when the last recoverable JWT expires', async (context) => {
  context.mock.timers.enable({ apis: ['Date', 'setTimeout'], now: 1800000000000 })
  const auth = await setup({ access: token(1, 1), refresh: token(1, 2) })
  const before = auth.getAuthSession()
  const seen = []
  const unsubscribe = auth.subscribeAuth(() => seen.push(auth.getAuthSession()))
  try {
    context.mock.timers.tick(2001)
    assert.equal(auth.isAuthenticated(), false)
    assert.notEqual(auth.getAuthSession().generation, before.generation)
    assert.equal(seen.at(-1).authenticated, false)
  } finally { unsubscribe() }
})

for (const newerAction of ['login', 'logout']) {
  test(`late A login cannot overwrite a newer ${newerAction}`, async () => {
    const started = deferred()
    const release = deferred()
    const pairB = credentials(2)
    const auth = await setup({}, async (config) => {
      if (JSON.parse(config.data).username === 'account-a') {
        started.resolve()
        await release.promise
        return response(config, credentials(1))
      }
      return response(config, pairB)
    })
    const stale = assert.rejects(auth.login('account-a', 'test-password'), canceled)
    await started.promise
    if (newerAction === 'login') await auth.login('account-b', 'test-password')
    else auth.logout()
    release.resolve()
    await stale
    assert.equal(auth.isAuthenticated(), newerAction === 'login')
    assert.equal(auth.storage.get('access'), newerAction === 'login' ? pairB.access : undefined)
  })
}

test('late registration cannot start automatic login after logout', async () => {
  const started = deferred()
  const release = deferred()
  const auth = await setup({}, async (config) => {
    assert.equal(config.url, '/auth/register/')
    started.resolve()
    await release.promise
    return response(config, {})
  })
  const rejected = assert.rejects(auth.register('account-a', '', 'test-password'), canceled)
  await started.promise
  auth.logout()
  release.resolve()
  await rejected
  assert.equal(auth.calls.length, 1)
  assert.equal(auth.isAuthenticated(), false)
})

test('mismatched access/refresh account identities fail closed', async () => {
  const auth = await setup({ access: token(1), refresh: token(2, 3600) }, (config) => {
    assert.equal(config.headers.Authorization, undefined)
    return response(config, [])
  })
  assert.equal(auth.isAuthenticated(), false)
  await auth.api.get('/courses/')
  assert.equal(auth.calls.length, 1)
})

test('mismatched token accounts cannot issue a protected read or write', async () => {
  const auth = await setup({ access: token(1), refresh: token(2, 3600) })
  await assert.rejects(auth.api.get('/my/enrollments/'), canceled)
  await assert.rejects(auth.api.post('/lessons/15/complete/', {}), canceled)
  assert.equal(auth.calls.length, 0)
})

test('a clean login recovers a mismatched stored token pair', async () => {
  const pair = credentials(2)
  const auth = await setup({ access: token(1), refresh: token(2, 3600) }, (config) => {
    assert.equal(config.url, '/auth/token/')
    assert.equal(config.headers.Authorization, undefined)
    return response(config, pair)
  })
  assert.equal(auth.isAuthenticated(), false)
  await auth.login('account-b', 'test-password')
  assert.equal(auth.isAuthenticated(), true)
  assert.equal(auth.storage.get('access'), pair.access)
  assert.equal(auth.storage.get('refresh'), pair.refresh)
})

test('a refresh response for another account is rejected and never used for a protected retry', async () => {
  const wrongAccount = token(2)
  const auth = await setup(credentials(1, -30), (config) => {
    if (config.url === '/auth/token/refresh/') return response(config, { access: wrongAccount })
    fail(config)
  })
  await assert.rejects(auth.api.get('/auth/me/'))
  assert.equal(auth.calls.filter((call) => call.url === '/auth/me/').length, 1)
  assert.equal(auth.storage.has('access'), false)
  assert.equal(auth.isAuthenticated(), false)
})

test('theme and locale storage events do not replace the auth snapshot or notify consumers', async () => {
  const auth = await setup(credentials(1))
  const before = auth.getAuthSession()
  let changes = 0
  const unsubscribe = auth.subscribeAuth(() => { changes += 1 })
  try {
    const initialChanges = changes
    auth.storage.set('theme', 'dark')
    auth.storageEvent('theme')
    auth.storage.set('language', 'kk')
    auth.storageEvent('language')
    assert.equal(auth.getAuthSession(), before)
    assert.equal(changes, initialChanges)
  } finally { unsubscribe() }
})
