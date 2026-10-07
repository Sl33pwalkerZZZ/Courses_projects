import { createContext, useContext } from 'react'
import { readPreference } from '../utils/preferences'

export const THEME_KEY = 'ai-courses-theme'
export const ThemeContext = createContext(null)

export function getPreferredTheme() {
  const saved = readPreference(THEME_KEY)
  if (saved === 'dark' || saved === 'light') return saved
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function useTheme() {
  return useContext(ThemeContext)
}
