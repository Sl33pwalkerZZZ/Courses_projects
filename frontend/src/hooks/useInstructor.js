import { useEffect, useState } from 'react'
import api from '../api'
import { useAuthSession } from './useAuth'

// The API, rather than a decoded/display role, decides who can enter Studio.
// One identity flight per session also serves desktop/mobile Header navigation.
const identities = new Map()
export default function useInstructor() {
  const session = useAuthSession()
  const [result, setResult] = useState(null)
  const [revision, setRevision] = useState(0)
  useEffect(() => {
    if (!session.authenticated) return
    let active = true
    const key = session.generation
    if (!identities.has(key)) {
      identities.clear()
      identities.set(key, api.get('/studio/me/').then(({ data }) => ({ identity: data })).catch(error => {
        const forbidden = [401, 403].includes(error.response?.status)
        if (!forbidden) identities.delete(key)
        return { identity: null, error: !forbidden }
      }))
    }
    identities.get(key).then(value => { if (active) setResult({ key, ...value }) })
    return () => { active = false }
  }, [session.authenticated, session.generation, revision])
  const current = session.authenticated && result?.key === session.generation
  return { identity: current ? result.identity : null, error: current ? result.error : false, loading: session.authenticated && !current,
    retry: () => { identities.delete(session.generation); setResult(null); setRevision(value => value + 1) } }
}
