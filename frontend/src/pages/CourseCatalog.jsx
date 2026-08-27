import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'

const LEVEL_LABELS = {
  beginner: 'Начинающий',
  intermediate: 'Средний',
  advanced: 'Продвинутый',
}

export default function CourseCatalog() {
  const [courses, setCourses] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.get('/courses/')
      .then((res) => setCourses(res.data))
      .catch(() => setError('Не удалось загрузить каталог курсов.'))
  }, [])

  if (error) return <p className="error">{error}</p>
  if (!courses) return <p>Загрузка…</p>

  return (
    <div className="catalog">
      <h1>Каталог курсов</h1>
      <div className="course-grid">
        {courses.map((course) => (
          <Link to={`/courses/${course.slug}`} key={course.id} className="course-card">
            <span className="course-direction">{course.direction.name}</span>
            <h2>{course.title}</h2>
            <p>{course.description}</p>
            <div className="course-card-footer">
              <span>{LEVEL_LABELS[course.level] || course.level}</span>
              <span>{course.author}</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
