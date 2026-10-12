import { useEffect, useState } from 'react'
import { ThemeContext, THEME_KEY, getPreferredTheme } from './useTheme'
import { savePreference } from '../utils/preferences'

export default function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(getPreferredTheme)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)')
    const syncTheme = () => setTheme(getPreferredTheme())
    const syncStorage = (event) => {
      if (event.key === THEME_KEY || event.key === null) syncTheme()
    }
    media.addEventListener('change', syncTheme)
    window.addEventListener('storage', syncStorage)
    return () => {
      media.removeEventListener('change', syncTheme)
      window.removeEventListener('storage', syncStorage)
    }
  }, [])

  function toggleTheme() {
    const nextTheme = theme === 'dark' ? 'light' : 'dark'
    savePreference(THEME_KEY, nextTheme)
    setTheme(nextTheme)
  }

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>
}
