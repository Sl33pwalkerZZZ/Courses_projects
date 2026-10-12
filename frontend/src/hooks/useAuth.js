import { useSyncExternalStore } from 'react'
import { isAuthenticated, subscribeAuth } from '../api'

export default function useAuth() {
  return useSyncExternalStore(subscribeAuth, isAuthenticated)
}
