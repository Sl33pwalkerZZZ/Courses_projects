import axios from 'axios'
import { revokeVideoGrant } from './utils/lessonVideo.js'
import { createAuthSessionStore, readToken, tokenIsCurrent } from './utils/authSession.js'

const API_URL = import.meta.env?.VITE_API_URL || 'http://127.0.0.1:8000/api'
const api = axios.create({ baseURL: API_URL })
// Login/refresh requests never carry an old access token or refresh themselves.
const authApi = axios.create({ baseURL: API_URL })
const sessions = createAuthSessionStore()
let refreshFlight = null
let loginAttempt = 0

export const getAuthSession = sessions.getSnapshot
export const subscribeAuth = sessions.subscribe
export const isAuthenticated = () => getAuthSession().authenticated

function notifyAuthChange() {
  window.dispatchEvent(new Event('auth-change'))
}

function sessionChanged() {
  // Keep obsolete responses and their credentials out of application callbacks.
  return new axios.CanceledError('Session changed')
}

function requireSession(generation, allowMixed = false) {
  const current = sessions.read()
  if (current.snapshot.generation !== generation || (current.mixedAccounts && !allowMixed)) throw sessionChanged()
  return current
}

function requireRequestSession(config) {
  // Only requests actually sent without credentials are independent of account.
  if (config._anonymous && isPublicRead(config)) return sessions.read()
  return requireSession(config._sessionGeneration)
}

function isPublicCatalogRead(config) {
  return ['get', 'head'].includes(config.method)
    && config.url.split('?')[0] === '/courses/'
}

function isPublicRead(config) {
  const path = config.url.split('?')[0]
  return ['get', 'head'].includes(config.method)
    && /^\/courses\/(?:[^/]+\/(?:reviews\/)?)?$/.test(path)
}

function validPair(data, accountId) {
  return tokenIsCurrent(data.access) && readToken(data.access).accountId === accountId
    && (!data.refresh || (tokenIsCurrent(data.refresh) && readToken(data.refresh).accountId === accountId))
}

async function refreshAccessToken(generation) {
  const initial = requireSession(generation)
  if (!refreshFlight || refreshFlight.generation !== generation) {
    const flight = { generation }
    refreshFlight = flight
    flight.promise = (async () => {
      try {
        if (!tokenIsCurrent(initial.refresh)) throw new Error('Refresh token expired')
        const { data } = await authApi.post('/auth/token/refresh/', { refresh: initial.refresh })
        const current = requireSession(generation)
        // Another tab may have already refreshed/rotated this same session.
        if (current.refresh !== initial.refresh) {
          if (tokenIsCurrent(current.access)) return
          throw sessionChanged()
        }
        if (!validPair(data, initial.accountId)) throw new Error('Invalid refresh response')
        localStorage.setItem('access', data.access)
        if (data.refresh) localStorage.setItem('refresh', data.refresh)
        notifyAuthChange()
      } catch (error) {
        const current = sessions.read()
        if (current.snapshot.generation !== generation || current.mixedAccounts) throw sessionChanged()
        if (current.refresh !== initial.refresh) {
          if (tokenIsCurrent(current.access)) return
          throw sessionChanged()
        }
        logout()
        throw error
      }
    })().finally(() => {
      // An old flight must not clear a newer account's refresh flight.
      if (refreshFlight === flight) refreshFlight = null
    })
  }
  return refreshFlight.promise
}

function anonymizePublicRead(config) {
  if (!isPublicRead(config)) throw sessionChanged()
  config._anonymous = true
  config._sessionGeneration = getAuthSession().generation
  delete config.headers.Authorization
  return config
}

// Axios runs request interceptors in reverse registration order, so this runs
// after the synchronous session/header capture below, only for refresh-only
// requests. Recover before sending: anonymous draft details return 404, not 401.
api.interceptors.request.use(async (config) => {
  let current = requireRequestSession(config)
  if (!current.access) {
    config._retried = true
    try {
      await refreshAccessToken(config._sessionGeneration)
      current = requireSession(config._sessionGeneration)
    } catch (error) {
      if (axios.isCancel(error) || sessions.read().snapshot.authenticated) throw sessionChanged()
      if (!isPublicRead(config)) throw sessionChanged()
      return anonymizePublicRead(config)
    }
  }
  config.headers.Authorization = `Bearer ${current.access}`
  return config
}, undefined, { runWhen(config) {
  const current = sessions.read()
  if (config._anonymous || isPublicCatalogRead(config) || current.access || !current.snapshot.authenticated) return false
  // runWhen is evaluated immediately, before an async interceptor is queued.
  // Capture here too so a queued refresh-only request cannot adopt account B.
  config._sessionGeneration ??= current.snapshot.generation
  return true
} })

api.interceptors.request.use((config) => {
  if (config._sessionGeneration !== undefined) requireRequestSession(config)
  let current = sessions.read()
  // Catalog responses are public. Detail/reviews carry the current session,
  // including access to enrolled drafts and the current user's own review.
  if (isPublicCatalogRead(config) || (!current.snapshot.authenticated && isPublicRead(config))) {
    config._anonymous = true
  }
  if (current.mixedAccounts) {
    if (!isPublicRead(config)) throw sessionChanged()
    // Public browsing can continue anonymously during a partially replaced pair.
    // Do not erase credentials another tab may still be committing.
    config._anonymous = true
  }
  if (!current.mixedAccounts && !current.snapshot.authenticated && (current.access || current.refresh)) {
    logout()
    current = sessions.read()
    config._sessionGeneration = current.snapshot.generation
  }
  // Synchronous capture also protects requests queued just before a new login.
  config._sessionGeneration ??= current.snapshot.generation
  if (current.access && !config._anonymous) config.headers.Authorization = `Bearer ${current.access}`
  else delete config.headers.Authorization
  return config
}, (error) => { throw error }, { synchronous: true })

api.interceptors.response.use((response) => {
  try {
    requireRequestSession(response.config)
  } catch (error) {
    // Revoke obsolete grants without using a replacement account's JWT.
    const config = response.config
    const match = config.method === 'post' && config.baseURL === '/api'
      && /^\/lesson-attachments\/([1-9]\d*)\/playback-grant\/$/.exec(config.url)
    if (axios.isCancel(error) && match) revokeVideoGrant(Number(match[1]), response.data?.revoke_token)
    throw error
  }
  return response
}, async (error) => {
  const config = error.config
  if (!config) throw error
  requireRequestSession(config)
  if (error.response?.status !== 401) throw error
  if (config._anonymous) throw error
  if (config._retried) {
    if (config.headers.Authorization === `Bearer ${sessions.read().access}`) logout()
    if (isPublicRead(config) && !sessions.read().snapshot.authenticated) return api(anonymizePublicRead(config))
    throw error
  }
  config._retried = true
  const current = sessions.read()
  // A late 401 may follow a refresh performed by another request/tab.
  if (tokenIsCurrent(current.access) && config.headers.Authorization !== `Bearer ${current.access}`) return api(config)

  try {
    await refreshAccessToken(config._sessionGeneration)
    requireSession(config._sessionGeneration)
  } catch (refreshError) {
    if (axios.isCancel(refreshError) || sessions.read().snapshot.authenticated) throw sessionChanged()
    if (!isPublicRead(config)) throw error
    // Failed refresh ended the session: only a public read can retry anonymously.
    anonymizePublicRead(config)
  }
  return api(config)
})

export default api

export async function login(username, password) {
  const generation = getAuthSession().generation
  const attempt = ++loginAttempt
  const { data } = await authApi.post('/auth/token/', { username, password })
  requireSession(generation, true)
  if (attempt !== loginAttempt) throw sessionChanged()
  const accountId = readToken(data.access)?.accountId
  if (!accountId || !data.refresh || !validPair(data, accountId)) throw new Error('Invalid login response')
  localStorage.setItem('access', data.access)
  localStorage.setItem('refresh', data.refresh)
  // One opaque marker per sign-in, shared across tabs; JWT rotation keeps it stable.
  localStorage.setItem('auth-session', crypto.randomUUID())
  notifyAuthChange()
  return data
}

export async function register(username, email, password) {
  const generation = getAuthSession().generation
  const attempt = ++loginAttempt
  await authApi.post('/auth/register/', { username, email, password })
  requireSession(generation, true)
  if (attempt !== loginAttempt) throw sessionChanged()
  return login(username, password)
}

export function logout() {
  loginAttempt += 1
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('auth-session')
  sessions.invalidate()
  notifyAuthChange()
}
