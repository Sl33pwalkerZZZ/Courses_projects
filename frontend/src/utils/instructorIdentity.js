// Shared, token-free capability cache. A session change immediately isolates the
// old identity; late responses cannot publish capabilities into another session.
export function createInstructorIdentityStore(loadIdentity, now = Date.now) {
  const empty = Object.freeze({ identity: null, loading: false, error: false, checked: false })
  let sessionKey, snapshot = empty, flight = null, checkedAt = 0
  const listeners = new Set()
  const notify = () => listeners.forEach(listener => listener())
  function select(key) {
    if (key === sessionKey) return
    sessionKey = key
    snapshot = empty
    flight = null
    checkedAt = 0
    notify()
  }
  return {
    subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener) },
    getSnapshot(key) { return key === sessionKey ? snapshot : empty },
    async refresh(key, force = false) {
      select(key)
      if (key == null) return
      if (flight) return flight
      if (!force && checkedAt && now() - checkedAt < 15000) return
      snapshot = { ...snapshot, loading: !snapshot.identity, error: false }
      notify()
      const request = Promise.resolve().then(loadIdentity).then(identity => ({ identity, loading: false, error: false }), error => ({ identity: null, loading: false, error: ![401, 403].includes(error.response?.status) }))
      flight = request
      const result = await request
      if (sessionKey !== key || flight !== request) return
      snapshot = { ...result, checked: true }
      checkedAt = now()
      flight = null
      notify()
    },
  }
}

export function canEnterStudio(identity) { return identity?.can_access_studio === true }
