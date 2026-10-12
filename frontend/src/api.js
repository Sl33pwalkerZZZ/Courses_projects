import axios from 'axios'
import { readPreference } from './utils/preferences.js'

const API_URL = import.meta.env?.VITE_API_URL || 'http://127.0.0.1:8000/api'

const api = axios.create({ baseURL: API_URL })
// Auth requests must not carry an old access token or trigger their own refresh.
const authApi = axios.create({ baseURL: API_URL })
let refreshPromise = null
let sessionVersion = 0

function tokenExpiry(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return Number.isFinite(payload.exp) ? payload.exp * 1000 : 0
  } catch {
    return 0
  }
}

function tokenIsCurrent(token) {
  return tokenExpiry(token) > Date.now()
}

function notifyAuthChange() {
  window.dispatchEvent(new Event('auth-change'))
}

export function isAuthenticated() {
  // An expired access token can still be recovered with a current refresh token.
  return tokenIsCurrent(readPreference('access')) || tokenIsCurrent(readPreference('refresh'))
}

export function subscribeAuth(listener) {
  let timer
  function update() {
    clearTimeout(timer)
    listener()
    const expiry = Math.max(tokenExpiry(readPreference('access')), tokenExpiry(readPreference('refresh')))
    if (expiry > Date.now()) {
      timer = setTimeout(update, Math.min(expiry - Date.now() + 1, 2147483647))
    }
  }
  window.addEventListener('auth-change', update)
  window.addEventListener('storage', update)
  update()
  return () => {
    clearTimeout(timer)
    window.removeEventListener('auth-change', update)
    window.removeEventListener('storage', update)
  }
}

function isPublicRead(config) {
  const path = config.url.split('?')[0]
  return ['get', 'head'].includes(config.method)
    && /^\/courses\/(?:[^/]+\/(?:reviews\/)?)?$/.test(path)
}

async function refreshAccessToken() {
  if (!refreshPromise) {
    const refresh = readPreference('refresh')
    const version = sessionVersion
    refreshPromise = (async () => {
      try {
        if (!tokenIsCurrent(refresh)) throw new Error('Refresh token expired')
        const { data } = await authApi.post('/auth/token/refresh/', { refresh })
        // A logout or a new login while refreshing must not restore the old session.
        if (sessionVersion !== version || readPreference('refresh') !== refresh) throw new Error('Session changed')
        if (!tokenIsCurrent(data.access)) throw new Error('Invalid access token')
        localStorage.setItem('access', data.access)
        if (data.refresh) localStorage.setItem('refresh', data.refresh)
        notifyAuthChange()
      } catch (error) {
        if (sessionVersion === version && readPreference('refresh') === refresh) logout()
        throw error
      }
    })().finally(() => { refreshPromise = null })
  }
  return refreshPromise
}

api.interceptors.request.use((config) => {
  if (!isAuthenticated() && (readPreference('access') || readPreference('refresh'))) logout()
  const access = readPreference('access')
  if (access && !config._anonymous) {
    config.headers.Authorization = `Bearer ${access}`
  } else {
    delete config.headers.Authorization
  }
  config._sessionVersion = sessionVersion
  return config
})

api.interceptors.response.use((response) => response, async (error) => {
  const config = error.config
  if (error.response?.status !== 401 || !config) throw error

  // Do not replay a previous user's protected request after logout or login.
  if (config._sessionVersion !== sessionVersion) {
    if (!isPublicRead(config) || config._retried) throw error
    config._retried = true
    config._anonymous = true
    return api(config)
  }

  if (config._retried) {
    if (config.headers.Authorization === `Bearer ${readPreference('access')}`) logout()
    throw error
  }
  config._retried = true

  const access = readPreference('access')
  // Another request may already have refreshed this request's old token.
  if (tokenIsCurrent(access) && config.headers.Authorization !== `Bearer ${access}`) {
    return api(config)
  }

  try {
    await refreshAccessToken()
  } catch {
    if (!isPublicRead(config)) throw error
    config._anonymous = true
  }
  return api(config)
})

export default api

export async function login(username, password) {
  const { data } = await authApi.post('/auth/token/', { username, password })
  localStorage.setItem('access', data.access)
  localStorage.setItem('refresh', data.refresh)
  sessionVersion += 1
  notifyAuthChange()
  return data
}

export async function register(username, email, password) {
  await authApi.post('/auth/register/', { username, email, password })
  return login(username, password)
}

export function logout() {
  sessionVersion += 1
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  notifyAuthChange()
}
