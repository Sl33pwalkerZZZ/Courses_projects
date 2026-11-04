import { useEffect, useRef } from 'react'
import { motion, useMotionValue, useSpring } from 'motion/react'
import { useMediaQuery, useSceneActivity } from '../motion/useSceneActivity'
import { useReducedMotion } from '../../hooks/useMotionPreferences'

export default function DepthSurface({ children, className = '' }) {
  const ref = useRef(null)
  const reduced = useReducedMotion()
  const fine = useMediaQuery('(min-width: 901px) and (hover: hover) and (pointer: fine)')
  const active = useSceneActivity(ref, fine && !reduced)
  const x = useMotionValue(0), y = useMotionValue(0)
  const rotateX = useSpring(x, { stiffness: 160, damping: 26 })
  const rotateY = useSpring(y, { stiffness: 160, damping: 26 })
  const reset = () => { x.set(0); y.set(0) }
  useEffect(() => { if (!active) { x.set(0); y.set(0) } }, [active, x, y])
  function move(event) {
    if (!active) return
    const box = event.currentTarget.getBoundingClientRect()
    x.set(-(event.clientY - box.top - box.height / 2) / box.height * 7)
    y.set((event.clientX - box.left - box.width / 2) / box.width * 9)
  }
  return <motion.div ref={ref} className={`cinema-depth ${className}`.trim()}
    onPointerMove={move} onPointerLeave={reset} onPointerCancel={reset}
    style={active ? { rotateX, rotateY, transformPerspective: 1100 } : undefined}>
    {children}
  </motion.div>
}
