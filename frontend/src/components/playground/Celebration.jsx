import { motion, useReducedMotion } from 'motion/react'

// Mount only after a confirmed success. Finite, decorative, no overlay capture.
export default function Celebration() {
  const reduced = useReducedMotion()
  if (reduced) return null
  return <span className="play-celebration" aria-hidden="true">
    {Array.from({ length: 10 }, (_, i) => <motion.i key={i}
      initial={{ opacity: 1, x: 0, y: 0, rotate: 0 }}
      animate={{ opacity: 0, x: Math.cos(i * .63) * 60, y: Math.sin(i * .63) * 50, rotate: i * 30 }}
      transition={{ duration: .65, ease: 'easeOut' }} />)}
  </span>
}
