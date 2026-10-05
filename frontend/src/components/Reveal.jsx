import { motion, useReducedMotion } from 'motion/react'

export default function Reveal({ children, className, delay = 0 }) {
  const reduceMotion = useReducedMotion()

  return (
    <motion.div className={className}
      initial={reduceMotion ? false : { opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: 0.5, delay: reduceMotion ? 0 : delay, ease: 'easeOut' }}>
      {children}
    </motion.div>
  )
}
