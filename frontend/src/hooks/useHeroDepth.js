import { useEffect } from 'react'
import { useMediaQuery, useReducedMotion } from './useMotionPreferences'

// Separate from idle ASCII: one bounded depth shift, natural passive scrolling.
export default function useHeroDepth(ref) {
  const reduced = useReducedMotion()
  const mobile = useMediaQuery('(max-width: 767px)', true)
  useEffect(() => {
    const node = ref.current
    if (!node || reduced || mobile) return
    let visible = true, frame = 0
    const paint = () => { frame = 0; if (visible && !document.hidden) node.style.setProperty('--hero-depth', `${Math.max(-32, Math.min(12, node.getBoundingClientRect().top * .06))}px`) }
    const schedule = () => { if (visible && !document.hidden && !frame) frame = requestAnimationFrame(paint) }
    const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; schedule() })
    observer.observe(node)
    window.addEventListener('scroll', schedule, { passive: true })
    document.addEventListener('visibilitychange', schedule)
    schedule()
    return () => { observer.disconnect(); cancelAnimationFrame(frame); window.removeEventListener('scroll', schedule); document.removeEventListener('visibilitychange', schedule); node.style.removeProperty('--hero-depth') }
  }, [ref, reduced, mobile])
}
