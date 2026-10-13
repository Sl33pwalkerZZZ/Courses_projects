import axios from 'axios'
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
  if (config._publicCourseRead) return sessions.read()
  return requireSession(config._sessionGeneration, config._anonymous && isPublicRead(config))
}

function isPublicCourseRead(config) {
  return ['get', 'head'].includes(config.method)
    && /^\/courses\/(?:[^/]+\/)?$/.test(config.url.split('?')[0])
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

api.interceptors.request.use((config) => {
  // These serializers contain only public metadata. Reviews remain session-bound
  // because their response also includes the current user's own review.
  config._publicCourseRead = isPublicCourseRead(config)
  if (config._publicCourseRead) config._anonymous = true
  let current = sessions.read()
  if (current.mixedAccounts) {
    if (!isPublicRead(config)) throw sessionChanged()
    // Public browsing can continue anonymously during a partially replaced pair.
    // Do not erase credentials another tab may still be committing.
    config._anonymous = true
  }
  if (config._sessionGeneration !== undefined) requireRequestSession(config)
  if (!current.mixedAccounts && !current.snapshot.authenticated && (current.access || current.refresh)) {
    logout()
    current = sessions.read()
  }
  // Synchronous capture also protects requests queued just before a new login.
  config._sessionGeneration ??= current.snapshot.generation
  if (current.access && !config._anonymous) config.headers.Authorization = `Bearer ${current.access}`
  else delete config.headers.Authorization
  return config
}, (error) => { throw error }, { synchronous: true })

api.interceptors.response.use((response) => {
  requireRequestSession(response.config)
  return response
}, async (error) => {
  const config = error.config
  if (!config) throw error
  requireRequestSession(config)
  if (error.response?.status !== 401) throw error
  if (config._publicCourseRead) throw error
  if (config._retried) {
    if (config.headers.Authorization === `Bearer ${sessions.read().access}`) logout()
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
    config._anonymous = true
    config._sessionGeneration = getAuthSession().generation
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
