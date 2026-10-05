import { lazy, Suspense } from 'react'
import { useTranslation } from 'react-i18next'
import { Route, Routes, useLocation } from 'react-router-dom'
import Header from './components/Header'
import CourseCatalog from './pages/CourseCatalog'
import Reveal from './components/Reveal'
import ScrollProgress from './components/ScrollProgress'

const CourseDetail = lazy(() => import('./pages/CourseDetail'))
const LessonView = lazy(() => import('./pages/LessonView'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))

export default function App() {
  const { pathname } = useLocation()
  const { t } = useTranslation()

  return (
    <>
      <ScrollProgress />
      <Header />
      <main id="main-content" tabIndex={-1} className={pathname === '/' ? 'catalog-container' : 'container legacy-page'}>
        <Reveal key={pathname} immediate>
          <Suspense fallback={<p role="status">{t('common.loading')}</p>}>
            <Routes>
              <Route path="/" element={<CourseCatalog />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/courses/:slug" element={<CourseDetail />} />
              <Route path="/lessons/:id" element={<LessonView />} />
            </Routes>
          </Suspense>
        </Reveal>
      </main>
    </>
  )
}
