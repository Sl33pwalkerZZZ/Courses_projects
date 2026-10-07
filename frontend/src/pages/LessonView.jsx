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
  const [completing, setCompleting] = useState(false)
  const [completeError, setCompleteError] = useState(null)

  useEffect(() => {
    let active = true
    api.get(`/lessons/${id}/`)
      .then((res) => {
        if (active) {
          setLesson(res.data)
          setCompleted(Boolean(res.data.completed_at))
        }
      })
      .catch(() => { if (active) setError('lesson.accessError') })
    return () => { active = false }
  }, [id])

  async function handleComplete() {
    if (completed || completing) return
    setCompleting(true)
    setCompleteError(null)
    try {
      const { data } = await api.post(`/lessons/${id}/complete/`)
      if (!data.completed_at) throw new Error('Completion was not confirmed')
      setCompleted(true)
    } catch {
      setCompleteError('lesson.completeError')
    } finally {
      setCompleting(false)
    }
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

      {completeError && <p className="error" role="alert">{t(completeError)}</p>}
      <button className="btn-primary" onClick={handleComplete} disabled={completed || completing}>
        {t(completed ? 'lesson.completed' : completing ? 'lesson.completing' : 'lesson.complete')}
      </button>
    </div>
  )
}
