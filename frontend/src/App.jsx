import { Route, Routes, useLocation } from 'react-router-dom'
import Header from './components/Header'
import CourseCatalog from './pages/CourseCatalog'
import CourseDetail from './pages/CourseDetail'
import LessonView from './pages/LessonView'
import Login from './pages/Login'
import Register from './pages/Register'

export default function App() {
  const { pathname } = useLocation()

  return (
    <>
      <Header />
      <main id="main-content" tabIndex={-1} className={pathname === '/' ? 'catalog-container' : 'container legacy-page'}>
        <Routes>
          <Route path="/" element={<CourseCatalog />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/courses/:slug" element={<CourseDetail />} />
          <Route path="/lessons/:id" element={<LessonView />} />
        </Routes>
      </main>
    </>
  )
}
