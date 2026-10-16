import { useCallback, useSyncExternalStore } from 'react'

export function useMediaQuery(query, serverValue = false) {
  const subscribe = useCallback((notify) => {
    const media = window.matchMedia(query)
    media.addEventListener('change', notify)
    return () => media.removeEventListener('change', notify)
  }, [query])
  const snapshot = useCallback(() => window.matchMedia(query).matches, [query])
  return useSyncExternalStore(subscribe, snapshot, () => serverValue)
}

// Motion's animation policy remains configured globally, while this reactive
// subscription also swaps Canvas, story and companion implementations live.
export function useReducedMotion() {
  return useMediaQuery('(prefers-reduced-motion: reduce)', true)
}
