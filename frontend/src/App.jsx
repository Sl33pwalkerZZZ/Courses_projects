import { lazy, Suspense, useLayoutEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import CourseCatalog from './pages/CourseCatalog'
import Reveal from './components/Reveal'
import ScrollProgress from './components/ScrollProgress'
import useAuth from './hooks/useAuth'

const CourseDetail = lazy(() => import('./pages/CourseDetail'))
const LessonView = lazy(() => import('./pages/LessonView'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const Profile = lazy(() => import('./pages/Profile'))

export default function App() {
  const authed = useAuth()
  const { pathname } = useLocation()
  const { t } = useTranslation()
  const isAuthPage = pathname === '/login' || pathname === '/register'
  const pageClassName = isAuthPage ? 'auth-container'
    : pathname === '/' || pathname === '/profile' ? 'catalog-container' : 'container legacy-page'

  // React Router preserves scroll by default; a catalog card may be far down the page.
  useLayoutEffect(() => {
    if (!window.location.hash) {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
      document.getElementById('main-content')?.focus({ preventScroll: true })
    }
  }, [pathname])

  return (
    <>
      <ScrollProgress />
      <Header />
      <main id="main-content" tabIndex={-1} className={pageClassName}>
        <Reveal key={pathname} immediate>
          <Suspense fallback={<p role="status">{t('common.loading')}</p>}>
            <Routes>
              <Route path="/" element={<CourseCatalog />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/profile" element={authed ? <Profile /> : <Navigate to="/login" replace />} />
              <Route path="/courses/:slug" element={<CourseDetail />} />
              <Route path="/lessons/:id" element={<LessonView />} />
            </Routes>
          </Suspense>
        </Reveal>
      </main>
      <Footer />
    </>
  )
}
