import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { ThemeContext, THEME_KEY, getPreferredTheme } from './useTheme'
import { flushSync } from 'react-dom'
import { createThemeTransition } from './themeTransition'
import './theme-transition.css'
import { savePreference } from '../utils/preferences'

export default function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(getPreferredTheme)

  const requestedTheme = useRef(theme)
  const transition = useRef(null)

  useEffect(() => {
    transition.current = createThemeTransition(document, window)
    return () => transition.current?.dispose()
  }, [])

  useLayoutEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)')
    const syncTheme = () => {
      transition.current?.cancel()
      requestedTheme.current = getPreferredTheme()
      setTheme(requestedTheme.current)
    }
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

  function toggleTheme(event) {
    const nextTheme = requestedTheme.current === 'dark' ? 'light' : 'dark'
    requestedTheme.current = nextTheme
    savePreference(THEME_KEY, nextTheme)
    const rect = event?.currentTarget?.getBoundingClientRect()
    const apply = () => flushSync(() => setTheme(nextTheme))
    if (transition.current) transition.current.change(apply, rect)
    else apply()
  }

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>
}
