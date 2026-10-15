import { lazy, Suspense, useLayoutEffect } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import CourseCatalog from './pages/CourseCatalog'
import Reveal from './components/Reveal'
import { NotFound, PageErrorBoundary, PageLoading } from './components/GlobalState'
import ScrollProgress from './components/ScrollProgress'
import { useAuthSession } from './hooks/useAuth'

const CourseDetail = lazy(() => import('./pages/CourseDetail'))
const LessonView = lazy(() => import('./pages/LessonView'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const Profile = lazy(() => import('./pages/Profile'))

export default function App() {
  const session = useAuthSession()
  const authed = session.authenticated
  const { pathname } = useLocation()
  const isAuthPage = pathname === '/login' || pathname === '/register'
  const pageClassName = isAuthPage ? 'auth-container'
    : pathname === '/' ? 'catalog-container v2-home'
      : pathname === '/profile' ? 'dashboard-container' : 'container'

  // React Router preserves scroll by default; a catalog card may be far down the page.
  useLayoutEffect(() => {
    if (!window.location.hash) {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
      document.getElementById('main-content')?.focus({ preventScroll: true })
    }
  }, [pathname])

  return (
    <>
      <ScrollProgress studio />
      <Header />
      <main id="main-content" tabIndex={-1} className={pageClassName}>
        <Reveal key={pathname} immediate>
          <PageErrorBoundary resetKey={`${pathname}:${session.generation}`}>
            <Suspense fallback={<PageLoading />}>
            {/* Private routes share a session key; refresh preserves it and public pages stay mounted. */}
            <Routes>
              <Route path="/" element={<CourseCatalog />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/profile" element={authed ? <Profile key={session.generation} /> : <Navigate to="/login" replace />} />
              <Route path="/courses/:slug" element={<CourseDetail key={session.generation} />} />
              <Route path="/lessons/:id" element={<LessonView key={session.generation} />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
            </Suspense>
          </PageErrorBoundary>
        </Reveal>
      </main>
      <Footer studio home={pathname === '/'} />
    </>
  )
}
