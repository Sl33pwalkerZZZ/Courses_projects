import { Moon, Sun } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useTheme } from '../theme/useTheme'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const { t } = useTranslation()
  const label = t(theme === 'dark' ? 'theme.light' : 'theme.dark')
  return (
    <button className="theme-toggle" type="button" onClick={toggleTheme} aria-label={label} title={label}>
      <span className="theme-toggle-icon" aria-hidden="true">
        <Sun size={18} className="theme-icon-sun" />
        <Moon size={18} className="theme-icon-moon" />
      </span>
    </button>
  )
}
