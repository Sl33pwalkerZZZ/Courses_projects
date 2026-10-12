import { motion, useReducedMotion, useScroll } from 'motion/react'

export default function ScrollProgress() {
  const { scrollYProgress } = useScroll()
  const reduceMotion = useReducedMotion()

  if (reduceMotion) return null
  return <motion.div className="scroll-progress" style={{ scaleX: scrollYProgress }} aria-hidden="true" />
}
