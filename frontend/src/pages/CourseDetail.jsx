import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api, { isAuthenticated } from '../api'

export default function CourseDetail() {
  const { slug } = useParams()
  const [course, setCourse] = useState(null)
  const [error, setError] = useState(null)
  const [enrolled, setEnrolled] = useState(false)
  const [enrolling, setEnrolling] = useState(false)

  useEffect(() => {
    api.get(`/courses/${slug}/`)
      .then((res) => setCourse(res.data))
      .catch(() => setError('Курс не найден.'))
  }, [slug])

  async function handleEnroll() {
    setEnrolling(true)
    try {
      await api.post(`/courses/${slug}/enroll/`)
      setEnrolled(true)
    } catch {
      setError('Не удалось записаться на курс. Убедитесь, что вы вошли в систему.')
    } finally {
      setEnrolling(false)
    }
  }

  if (error) return <p className="error">{error}</p>
  if (!course) return <p>Загрузка…</p>

  return (
    <div className="course-detail">
      <span className="course-direction">{course.direction.name}</span>
      <h1>{course.title}</h1>
      <p>{course.description}</p>
      <p className="author">Автор: {course.author}</p>

      {isAuthenticated() ? (
        <button className="btn-primary" onClick={handleEnroll} disabled={enrolling || enrolled}>
          {enrolled ? 'Вы записаны' : enrolling ? 'Запись…' : 'Начать курс'}
        </button>
      ) : (
        <p><Link to="/login">Войдите</Link>, чтобы начать курс.</p>
      )}

      <h2>Программа курса</h2>
      {course.modules.map((module) => (
        <div key={module.id} className="module">
          <h3>{module.title}</h3>
          <ul>
            {module.lessons.map((lesson) => (
              <li key={lesson.id}>
                <Link to={`/lessons/${lesson.id}`}>{lesson.title}</Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}
