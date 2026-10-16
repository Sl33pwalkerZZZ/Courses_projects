import { motion, useScroll } from 'motion/react'
import { useReducedMotion } from '../../hooks/useMotionPreferences'

// A quiet document-position cue, independent of saved lesson completion.
export default function ReadingProgress() {
  const { scrollYProgress } = useScroll()
  const reduced = useReducedMotion()
  return reduced ? null : <div className="play-reading-position" aria-hidden="true"><motion.span style={{ scaleX: scrollYProgress }} /></div>
}
