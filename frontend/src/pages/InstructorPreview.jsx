import { useEffect, useState } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../api'
import useAuth from '../hooks/useAuth'
import { ContentLanguageNotice } from '../components/learning/LearningContent'
import { orderCurriculum } from '../utils/lessons'

export default function InstructorPreview() {
  const authed = useAuth()
  const { slug } = useParams()
  return authed ? <Preview key={`${slug}:${authed}`} slug={slug} /> : <Navigate to="/login" replace />
}
function Preview({ slug }) {
  const { t } = useTranslation()
  const [course, setCourse] = useState(null)
  const [error, setError] = useState(false)
  const [retry, setRetry] = useState(0)
  useEffect(() => {
    let active = true
    api.get(`/instructor/courses/${encodeURIComponent(slug)}/preview/`).then(({ data }) => { if (active) setCourse(data) }).catch(() => { if (active) setError(true) })
    return () => { active = false }
  }, [slug, retry])
  if (error) return <section role="alert"><p>{t('instructorPreview.loadError')}</p><button type="button" onClick={() => { setError(false); setRetry(value => value + 1) }}>{t('common.retry')}</button></section>
  if (!course) return <p role="status">{t('common.loading')}</p>
  return <article className="instructor-preview"><p className="eyebrow">{t('instructorPreview.title')}</p><h1 lang={course.content_language || undefined}>{course.title}</h1>
    <p>{t('instructorPreview.notice')}</p><ContentLanguageNotice language={course.content_language} />
    <p lang={course.content_language || undefined}>{course.description}</p>
    {orderCurriculum(course.modules).map(module => <section key={module.id} lang={course.content_language || undefined}><h2>{module.title}</h2>
      <ol>{module.lessons.map(lesson => <li key={lesson.id}><Link to={`/lessons/${lesson.id}`} state={{ courseSlug: course.slug, preview: true }}>{lesson.title}</Link></li>)}</ol></section>)}
    <p>{t('instructorPreview.quiz')}</p>
  </article>
}
