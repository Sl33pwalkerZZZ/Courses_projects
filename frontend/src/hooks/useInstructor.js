import { useEffect, useSyncExternalStore } from 'react'
import { useLocation } from 'react-router-dom'
import api from '../api'
import { useAuthSession } from './useAuth'
import { createInstructorIdentityStore } from '../utils/instructorIdentity'

const identities = createInstructorIdentityStore(async () => (await api.get('/studio/me/')).data)
export function refreshInstructorPermissions() {
  window.dispatchEvent(new Event('instructor-permissions-changed'))
}
export default function useInstructor() {
  const session = useAuthSession()
  const { key: navigationKey } = useLocation()
  const key = session.authenticated ? session.generation : null
  const result = useSyncExternalStore(identities.subscribe, () => identities.getSnapshot(key), () => identities.getSnapshot(null))
  useEffect(() => {
    identities.refresh(key)
  }, [key, navigationKey])
  useEffect(() => {
    if (key == null) return
    const refresh = () => { if (document.visibilityState !== 'hidden') identities.refresh(key, true) }
    window.addEventListener('focus', refresh)
    window.addEventListener('instructor-permissions-changed', refresh)
    document.addEventListener('visibilitychange', refresh)
    // Server-side role changes must not remain cached for an entire login.
    const timer = window.setInterval(refresh, 60000)
    return () => {
      window.removeEventListener('focus', refresh)
      window.removeEventListener('instructor-permissions-changed', refresh)
      document.removeEventListener('visibilitychange', refresh)
      window.clearInterval(timer)
    }
  }, [key])
  return { ...result, loading: session.authenticated && (result.loading || !result.checked),
    retry: () => identities.refresh(key, true) }
}
