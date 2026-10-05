import { useTranslation } from 'react-i18next'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../api'

export default function LessonView() {
  const { t } = useTranslation()
  const { id } = useParams()
  const [lesson, setLesson] = useState(null)
  const [error, setError] = useState(null)
  const [completed, setCompleted] = useState(false)

  useEffect(() => {
    api.get(`/lessons/${id}/`)
      .then((res) => setLesson(res.data))
      .catch(() => setError('lesson.accessError'))
  }, [id])

  async function handleComplete() {
    await api.post(`/lessons/${id}/complete/`)
    setCompleted(true)
  }

  if (error) return <p className="error">{t(error)}</p>
  if (!lesson) return <p>{t('common.loading')}</p>

  return (
    <div className="lesson">
      <Link to={`/courses/${lesson.course_slug}`}>{t('lesson.back')}</Link>
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
          <h2>{t('lesson.assignment')}</h2>
          {lesson.assignments.map((a) => (
            <p key={a.id}>{a.description}</p>
          ))}
        </div>
      )}

      <button className="btn-primary" onClick={handleComplete} disabled={completed}>
        {t(completed ? 'lesson.completed' : 'lesson.complete')}
      </button>
    </div>
  )
}
