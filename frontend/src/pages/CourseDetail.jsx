import { useTranslation } from 'react-i18next'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../api'
import useAuth from '../hooks/useAuth'
import CourseReviews from '../components/CourseReviews'
import CourseEnrollment from '../components/CourseEnrollment'

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

  useEffect(() => {
    let active = true
    api.get(`/courses/${encodeURIComponent(slug)}/`)
      .then((res) => { if (active) setCourse(res.data) })
      .catch(() => { if (active) setError('course.notFound') })
    return () => { active = false }
  }, [slug])

  if (error) return <p className="error">{t(error)}</p>
  if (!course) return <p>{t('common.loading')}</p>

  return (
    <div className="course-detail">
      <span className="course-direction">{course.direction.name}</span>
      <h1>{course.title}</h1>
      <p>{course.description}</p>
      <p className="author">{t('course.author', { author: course.author })}</p>

      <CourseEnrollment course={course} authed={authed} onEnrollmentChange={setEnrollment} />

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
