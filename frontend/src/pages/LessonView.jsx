import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../api'

export default function LessonView() {
  const { id } = useParams()
  const [lesson, setLesson] = useState(null)
  const [error, setError] = useState(null)
  const [completed, setCompleted] = useState(false)

  useEffect(() => {
    api.get(`/lessons/${id}/`)
      .then((res) => setLesson(res.data))
      .catch(() => setError('Нет доступа к уроку — возможно, вы не записаны на курс.'))
  }, [id])

  async function handleComplete() {
    await api.post(`/lessons/${id}/complete/`)
    setCompleted(true)
  }

  if (error) return <p className="error">{error}</p>
  if (!lesson) return <p>Загрузка…</p>

  return (
    <div className="lesson">
      <Link to={`/courses/${lesson.course_slug}`}>← к программе курса</Link>
      <h1>{lesson.title}</h1>
      <p className="lesson-text">{lesson.text_content}</p>

      {lesson.images.length > 0 && (
        <div className="lesson-images">
          {lesson.images.map((img) => (
            <img key={img.id} src={img.image} alt="" />
          ))}
        </div>
      )}

      {lesson.assignments.length > 0 && (
        <div className="assignments">
          <h2>Задание</h2>
          {lesson.assignments.map((a) => (
            <p key={a.id}>{a.description}</p>
          ))}
        </div>
      )}

      <button className="btn-primary" onClick={handleComplete} disabled={completed}>
        {completed ? 'Урок пройден ✓' : 'Отметить пройденным'}
      </button>
    </div>
  )
}
