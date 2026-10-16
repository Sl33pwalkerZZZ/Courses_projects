import { motion } from 'motion/react'
import { useReducedMotion } from '../../hooks/useMotionPreferences'
import { useTranslation } from 'react-i18next'

export default function ProgressRing({ value = 0, label, size = 88 }) {
  const reduced = useReducedMotion()
  const { i18n } = useTranslation()
  const bounded = Math.max(0, Math.min(100, value))
  return <span className="play-progress-ring" role="img" aria-label={label} style={{ width: size, height: size }}>
    <svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="42" />
      <motion.circle cx="50" cy="50" r="42" pathLength="100" strokeDasharray="100" initial={reduced ? false : { strokeDashoffset: 100 }}
        animate={{ strokeDashoffset: 100 - bounded }} transition={{ duration: reduced ? 0 : .35 }} />
    </svg><strong aria-hidden="true">{new Intl.NumberFormat(i18n.resolvedLanguage, { style: 'percent', maximumFractionDigits: 1 }).format(bounded / 100)}</strong>
  </span>
}
