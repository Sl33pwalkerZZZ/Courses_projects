import { motion, useReducedMotion } from 'motion/react'

export default function Reveal({ children, className, delay = 0, immediate = false }) {
  const reduceMotion = useReducedMotion()

  return (
    <motion.div className={className}
      initial={reduceMotion ? false : { opacity: 0, y: 16 }}
      animate={immediate || reduceMotion ? { opacity: 1, y: 0 } : undefined}
      whileInView={immediate || reduceMotion ? undefined : { opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: reduceMotion ? 0 : 0.5, delay: reduceMotion ? 0 : delay, ease: 'easeOut' }}>
      {children}
    </motion.div>
  )
}
