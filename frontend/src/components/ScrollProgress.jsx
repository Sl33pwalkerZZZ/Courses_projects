import { motion, useScroll } from 'motion/react'
import { useReducedMotion } from '../hooks/useMotionPreferences'

export default function ScrollProgress({ studio = false }) {
  const { scrollYProgress } = useScroll()
  const reduceMotion = useReducedMotion()

  if (reduceMotion) return null
  return <motion.div className={`scroll-progress${studio ? ' studio-scroll-progress' : ''}`} style={{ scaleX: scrollYProgress }} aria-hidden="true" />
}
