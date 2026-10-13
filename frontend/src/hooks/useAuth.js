import { useSyncExternalStore } from 'react'
import { getAuthSession, subscribeAuth } from '../api'

const serverSession = Object.freeze({ authenticated: false, generation: 0 })

export function useAuthSession() {
  return useSyncExternalStore(subscribeAuth, getAuthSession, () => serverSession)
}

export default function useAuth() {
  return useAuthSession().authenticated
}
