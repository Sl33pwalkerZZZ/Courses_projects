import { motion } from 'motion/react'
import { useReducedMotion } from '../hooks/useMotionPreferences'

export default function AuthError({ children }) {
  const reducedMotion = useReducedMotion()
  return <motion.p className="auth-error" role="alert"
    initial={reducedMotion ? false : { y: -4 }} animate={{ y: 0 }}
    transition={{ duration: reducedMotion ? 0 : 0.16 }}>{children}</motion.p>
}
