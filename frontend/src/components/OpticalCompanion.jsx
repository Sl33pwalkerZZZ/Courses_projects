import { useEffect, useRef } from 'react'
import { useReducedMotion } from '../hooks/useMotionPreferences'
import './OpticalCompanion.css'

// Decorative optics follow pointer geometry only. They never inspect form fields.
export default function OpticalCompanion() {
  const object = useRef(null)
  const reduced = useReducedMotion()
  useEffect(() => {
    const node = object.current
    if (reduced || !node) return undefined
    let frame = 0
    let visible = true
    let x = 0, y = 0, targetX = 0, targetY = 0
    const reset = () => { targetX = 0; targetY = 0 }
    const pointer = (event) => {
      const rect = node.getBoundingClientRect()
      targetX = Math.max(-1, Math.min(1, (event.clientX - rect.left - rect.width / 2) / rect.width))
      targetY = Math.max(-1, Math.min(1, (event.clientY - rect.top - rect.height / 2) / rect.height))
    }
    const draw = (time) => {
      frame = 0
      if (!visible || document.hidden) return
      x += (targetX - x) * .08
      y += (targetY - y) * .08
      node.style.setProperty('--optic-x', `${(x * 14).toFixed(2)}px`)
      node.style.setProperty('--optic-y', `${(y * 10).toFixed(2)}px`)
      node.style.setProperty('--optic-float', `${(Math.sin(time / 2200) * 5).toFixed(2)}px`)
      frame = requestAnimationFrame(draw)
    }
    const sync = () => {
      cancelAnimationFrame(frame)
      frame = 0
      if (visible && !document.hidden) frame = requestAnimationFrame(draw)
    }
    const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; sync() })
    observer.observe(node)
    window.addEventListener('pointermove', pointer, { passive: true })
    window.addEventListener('pointerout', reset)
    document.addEventListener('visibilitychange', sync)
    sync()
    return () => {
      cancelAnimationFrame(frame)
      observer.disconnect()
      window.removeEventListener('pointermove', pointer)
      window.removeEventListener('pointerout', reset)
      document.removeEventListener('visibilitychange', sync)
      node.style.removeProperty('--optic-x')
      node.style.removeProperty('--optic-y')
      node.style.removeProperty('--optic-float')
    }
  }, [reduced])
  return (
    <div ref={object} className="optical-companion" aria-hidden="true" data-motion={reduced ? 'static' : 'responsive'}>
      <div className="optical-bridge" />
      {[0, 1].map((lens) => <div className={`optical-lens optical-lens--${lens}`} key={lens}>
        <div className="optical-lens-rim" />
        <div className="optical-iris"><span className="optical-pupil" /></div>
        <div className="optical-reflection" />
      </div>)}
      <div className="optical-base" />
    </div>
  )
}
