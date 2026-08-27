import { Route, Routes } from 'react-router-dom'
import Header from './components/Header'
import CourseCatalog from './pages/CourseCatalog'
import CourseDetail from './pages/CourseDetail'
import LessonView from './pages/LessonView'
import Login from './pages/Login'
import Register from './pages/Register'

export default function App() {
  return (
    <>
      <Header />
      <main className="container">
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
