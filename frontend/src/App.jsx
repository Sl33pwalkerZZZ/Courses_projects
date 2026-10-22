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
const CertificateVerification = lazy(() => import('./pages/CertificateVerification'))
const InstructorPreview = lazy(() => import('./pages/InstructorPreview'))
const StudioAccessGuard = lazy(() => import('./pages/instructor/InstructorStudio').then(module => ({ default: module.StudioAccessGuard })))
const InstructorStudio = lazy(() => import('./pages/instructor/InstructorStudio'))
const Dashboard = lazy(() => import('./pages/instructor/CourseEditor').then(module => ({ default: module.Dashboard })))
const StudioCourseList = lazy(() => import('./pages/instructor/CourseEditor').then(module => ({ default: module.CourseList })))
const NewCourse = lazy(() => import('./pages/instructor/CourseEditor').then(module => ({ default: module.NewCourse })))
const CourseWorkspace = lazy(() => import('./pages/instructor/CourseEditor').then(module => ({ default: module.CourseWorkspace })))
const CourseSettings = lazy(() => import('./pages/instructor/CourseEditor').then(module => ({ default: module.CourseSettings })))
const Curriculum = lazy(() => import('./pages/instructor/Curriculum'))
const Assessment = lazy(() => import('./pages/instructor/Assessment'))
const Publication = lazy(() => import('./pages/instructor/Publication'))
const Submissions = lazy(() => import('./pages/instructor/Publication').then(module => ({ default: module.Submissions })))
const PublicationReviews = lazy(() => import('./pages/instructor/Publication').then(module => ({ default: module.PublicationReviews })))
const InstructorManagement = lazy(() => import('./pages/instructor/Publication').then(module => ({ default: module.InstructorManagement })))
const EnrollmentRequests = lazy(() => import('./pages/instructor/EnrollmentRequests'))
const WordImport = lazy(() => import('./pages/instructor/WordImport'))

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
              <Route path="/certificates/verify/:verificationId" element={<CertificateVerification key={pathname} />} />
              <Route path="/profile" element={authed ? <Profile key={session.generation} /> : <Navigate to="/login" replace />} />
              <Route path="/courses/:slug" element={<CourseDetail key={session.generation} />} />
              <Route path="/instructor" element={<InstructorStudio key={session.generation} />}>
                <Route index element={<Dashboard />} />
                <Route path="courses" element={<StudioCourseList />} />
                <Route path="courses/new" element={<NewCourse />} />
                <Route path="import" element={<WordImport />} />
                <Route path="enrollment-requests" element={<StudioAccessGuard moderator><EnrollmentRequests /></StudioAccessGuard>} />
                <Route path="reviews" element={<StudioAccessGuard moderator><PublicationReviews /></StudioAccessGuard>} />
                <Route path="instructors" element={<StudioAccessGuard moderator><InstructorManagement /></StudioAccessGuard>} />
                <Route path="courses/:id" element={<CourseWorkspace key={pathname.split('/')[3]} />}>
                  <Route index element={<Navigate to="edit" replace />} />
                  <Route path="edit" element={<CourseSettings />} />
                  <Route path="curriculum" element={<Curriculum />} />
                  <Route path="assessment" element={<Assessment />} />
                  <Route path="submissions" element={<Submissions />} />
                  <Route path="publication" element={<Publication />} />
                </Route>
                <Route path="*" element={<NotFound />} />
              </Route>
              <Route path="/instructor/courses/:slug/preview" element={<StudioAccessGuard key={session.generation}><InstructorPreview /></StudioAccessGuard>} />
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
