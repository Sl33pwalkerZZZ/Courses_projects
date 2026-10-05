import { useTranslation, Trans } from 'react-i18next'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api, { isAuthenticated } from '../api'

export default function CourseDetail() {
  const { t } = useTranslation()
  const { slug } = useParams()
  const [course, setCourse] = useState(null)
  const [error, setError] = useState(null)
  const [enrolled, setEnrolled] = useState(false)
  const [enrolling, setEnrolling] = useState(false)

  useEffect(() => {
    api.get(`/courses/${slug}/`)
      .then((res) => setCourse(res.data))
      .catch(() => setError('course.notFound'))
  }, [slug])

  async function handleEnroll() {
    setEnrolling(true)
    try {
      await api.post(`/courses/${slug}/enroll/`)
      setEnrolled(true)
    } catch {
      setError('course.enrollError')
    } finally {
      setEnrolling(false)
    }
  }

  if (error) return <p className="error">{t(error)}</p>
  if (!course) return <p>{t('common.loading')}</p>

  return (
    <div className="course-detail">
      <span className="course-direction">{course.direction.name}</span>
      <h1>{course.title}</h1>
      <p>{course.description}</p>
      <p className="author">{t('course.author', { author: course.author })}</p>

      {isAuthenticated() ? (
        <button className="btn-primary" onClick={handleEnroll} disabled={enrolling || enrolled}>
          {t(enrolled ? 'course.enrolled' : enrolling ? 'course.enrolling' : 'course.start')}
        </button>
      ) : (
        <p><Trans i18nKey="course.signInToStart" components={{ signIn: <Link to="/login" /> }} /></p>
      )}

      <h2>{t('course.curriculum')}</h2>
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
