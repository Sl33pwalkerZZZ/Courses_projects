import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { Moon, Sun } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useTheme } from '../theme/useTheme'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const { t } = useTranslation()
  const reduceMotion = useReducedMotion()
  const label = t(theme === 'dark' ? 'theme.light' : 'theme.dark')

  return (
    <button className="theme-toggle" type="button" onClick={toggleTheme} aria-label={label} title={label}>
      <AnimatePresence initial={false} mode="wait">
        <motion.span key={theme}
          initial={reduceMotion ? false : { opacity: 0, rotate: -24 }}
          animate={{ opacity: 1, rotate: 0 }}
          exit={reduceMotion ? { opacity: 1 } : { opacity: 0, rotate: 24 }}
          transition={{ duration: reduceMotion ? 0 : 0.16 }}>
          {theme === 'dark' ? <Sun size={18} aria-hidden="true" /> : <Moon size={18} aria-hidden="true" />}
        </motion.span>
      </AnimatePresence>
    </button>
  )
}
