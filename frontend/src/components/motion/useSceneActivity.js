import { useEffect, useState } from 'react'

// Visibility changes are rare state updates; pointer animation never uses React state.
export function useSceneActivity(ref, enabled = true) {
  const [active, setActive] = useState(false)
  useEffect(() => {
    if (!enabled || !ref.current) return
    let visible = false
    const sync = () => setActive(visible && !document.hidden)
    const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; sync() })
    observer.observe(ref.current)
    document.addEventListener('visibilitychange', sync)
    return () => { observer.disconnect(); document.removeEventListener('visibilitychange', sync) }
  }, [ref, enabled])
  return enabled && active
}

export { useMediaQuery } from '../../hooks/useMotionPreferences'
