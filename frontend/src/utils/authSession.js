import { readPreference } from './preferences.js'

const authKeys = new Set(['access', 'refresh', 'auth-session'])

// These claims identify client state; Django still verifies JWT signatures/access.
export function readToken(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    const userId = payload.user_id
    if (!Number.isFinite(payload.exp) || !['string', 'number'].includes(typeof userId) || String(userId) === '') return null
    return { accountId: String(userId), expiresAt: payload.exp * 1000 }
  } catch {
    return null
  }
}

export function tokenIsCurrent(token) {
  const claims = readToken(token)
  return Boolean(claims && claims.expiresAt > Date.now())
}

export function createAuthSessionStore() {
  let snapshot
  let observedAccount = null
  let observedMarker = null
  let timer
  const listeners = new Set()

  function read(forceChange = false) {
    const access = readPreference('access')
    const refresh = readPreference('refresh')
    const marker = readPreference('auth-session')
    const accessClaims = readToken(access)
    const refreshClaims = readToken(refresh)
    // A partially replaced or corrupted pair must never mix two accounts.
    const mixedAccounts = Boolean(accessClaims && refreshClaims && accessClaims.accountId !== refreshClaims.accountId)
    const accountId = mixedAccounts ? null
      : tokenIsCurrent(refresh) ? refreshClaims.accountId
        : tokenIsCurrent(access) ? accessClaims.accountId : null
    const authenticated = accountId !== null

    if (!snapshot) {
      snapshot = Object.freeze({ authenticated, generation: 0 })
    } else if (forceChange || observedAccount !== accountId || observedMarker !== marker || snapshot.authenticated !== authenticated) {
      snapshot = Object.freeze({ authenticated, generation: snapshot.generation + 1 })
    }
    observedAccount = accountId
    observedMarker = marker
    return { access, refresh, accountId, mixedAccounts, snapshot }
  }

  function update() {
    clearTimeout(timer)
    const session = read()
    for (const listener of listeners) listener()
    if (!listeners.size || !session.snapshot.authenticated) return
    const expiry = Math.max(readToken(session.access)?.expiresAt || 0, readToken(session.refresh)?.expiresAt || 0)
    timer = setTimeout(update, Math.min(expiry - Date.now() + 1, 2147483647))
  }

  if (typeof window !== 'undefined') {
    window.addEventListener('auth-change', update)
    window.addEventListener('storage', (event) => {
      if (event.key == null || authKeys.has(event.key)) update()
    })
  }

  return {
    read,
    getSnapshot: () => read().snapshot,
    // Explicit logout invalidates even requests started while already anonymous.
    invalidate: () => read(true),
    subscribe(listener) {
      listeners.add(listener)
      update()
      return () => {
        listeners.delete(listener)
        if (!listeners.size) clearTimeout(timer)
      }
    },
  }
}
