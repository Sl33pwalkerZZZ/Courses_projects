import { useTranslation, Trans } from 'react-i18next'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../api'
import useAuth from '../hooks/useAuth'
import CourseReviews from '../components/CourseReviews'

export default function CourseDetail() {
  const { slug } = useParams()
  const authed = useAuth()
  // Reset private course state when the route or authentication changes.
  return <CourseContent key={`${slug}:${authed}`} slug={slug} authed={authed} />
}

function CourseContent({ slug, authed }) {
  const { t } = useTranslation()
  const [course, setCourse] = useState(null)
  const [error, setError] = useState(null)
  const [enrollment, setEnrollment] = useState(null)
  const [checkingEnrollment, setCheckingEnrollment] = useState(authed)
  const [enrollmentError, setEnrollmentError] = useState(null)
  const [enrollmentRetry, setEnrollmentRetry] = useState(0)
  const [enrolling, setEnrolling] = useState(false)
  const [enrollError, setEnrollError] = useState(null)

  useEffect(() => {
    let active = true
    api.get(`/courses/${encodeURIComponent(slug)}/`)
      .then((res) => { if (active) setCourse(res.data) })
      .catch(() => { if (active) setError('course.notFound') })
    return () => { active = false }
  }, [slug])

  useEffect(() => {
    let active = true
    if (authed) {
      api.get('/my/enrollments/')
        .then((res) => {
          if (active) setEnrollment(res.data.find((item) => item.course.slug === slug) || null)
        })
        .catch(() => { if (active) setEnrollmentError('course.enrollmentStatusError') })
        .finally(() => { if (active) setCheckingEnrollment(false) })
    }
    return () => { active = false }
  }, [slug, authed, enrollmentRetry])

  function retryEnrollment() {
    setCheckingEnrollment(true)
    setEnrollmentError(null)
    setEnrollmentRetry((value) => value + 1)
  }

  async function handleEnroll() {
    if (!authed || enrolling || enrollment || checkingEnrollment || enrollmentError) return
    setEnrolling(true)
    setEnrollError(null)
    try {
      const { data } = await api.post(`/courses/${encodeURIComponent(slug)}/enroll/`)
      // A new enrollment starts at the first lesson; no extra request is needed.
      const firstLesson = course.modules.flatMap((module) => module.lessons)[0]
      setEnrollment({ ...data, next_lesson_id: firstLesson?.id ?? null })
    } catch {
      setEnrollError('course.enrollError')
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

      {authed ? (
        enrollment ? <>
          <button className="btn-primary" disabled>{t('course.enrolled')}</button>
          {enrollment.next_lesson_id != null && <p>
            <Link to={`/lessons/${enrollment.next_lesson_id}`}>{t('profile.continueLearning')}</Link>
          </p>}
        </> : enrollmentError ? <div>
          <p className="error" role="alert">{t(enrollmentError)}</p>
          <button className="btn-primary" onClick={retryEnrollment}>{t('common.retry')}</button>
        </div> : (
          <button className="btn-primary" onClick={handleEnroll} disabled={checkingEnrollment || enrolling}>
            {t(checkingEnrollment ? 'common.loading' : enrolling ? 'course.enrolling' : 'course.start')}
          </button>
        )
      ) : (
        <p><Trans i18nKey="course.signInToStart" components={{ signIn: <Link to="/login" /> }} /></p>
      )}
      {enrollError && <p className="error" role="alert">{t(enrollError)}</p>}

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
      <CourseReviews key={slug} slug={slug} enrolled={authed && Boolean(enrollment)} />
    </div>
  )
}
