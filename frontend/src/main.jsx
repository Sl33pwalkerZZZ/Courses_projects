import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { MotionConfig } from 'motion/react'
import './i18n'
import ThemeProvider from './theme/ThemeProvider'
import { getPreferredTheme } from './theme/useTheme'
import './index.css'
import App from './App.jsx'

document.documentElement.dataset.theme = getPreferredTheme()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <MotionConfig reducedMotion="user">
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </MotionConfig>
    </ThemeProvider>
  </StrictMode>,
)
