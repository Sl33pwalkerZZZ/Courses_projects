import { useTranslation } from 'react-i18next'
import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { ArrowLeft, ArrowUpRight, BookOpen, Layers3, Star, UserRound } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import api from '../api'
import useAuth from '../hooks/useAuth'
import CourseReviews from '../components/CourseReviews'
import CourseEnrollment from '../components/CourseEnrollment'
import CourseCurriculum from '../components/CourseCurriculum'
import Reveal from '../components/Reveal'
import './CourseDetail.css'

export default function CourseDetail() {
  const { slug } = useParams()
  const authed = useAuth()
  // Reset private course state when the route or authentication changes.
  return <CourseContent key={`${slug}:${authed}`} slug={slug} authed={authed} />
}

function CourseContent({ slug, authed }) {
  const { t, i18n } = useTranslation()
  const pageRef = useRef(null)
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

  useLayoutEffect(() => {
    if (!course) return
    let target
    try {
      const id = decodeURIComponent(window.location.hash.slice(1))
      target = id ? document.getElementById(id) : null
    } catch {
      target = null
    }
    // Wait for API content before restoring a valid anchor. Otherwise start at the hero.
    if (target && pageRef.current?.contains(target)) target.scrollIntoView({ behavior: 'instant', block: 'start' })
    else window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }, [course])

  if (error) return <div className="course-overview course-overview-state" role="alert">
    <BookOpen size={28} aria-hidden="true" /><h1>{t(error)}</h1>
    <Link className="course-overview-back" to="/"><ArrowLeft size={17} aria-hidden="true" />{t('courseOverview.backToCatalog')}</Link>
  </div>
  if (!course) return <div className="course-overview course-overview-state" role="status" aria-busy="true">
    <BookOpen size={28} aria-hidden="true" /><p>{t('common.loading')}</p>
  </div>

  const modules = course.modules || []
  const lessonCount = modules.reduce((total, module) => total + (module.lessons?.length || 0), 0)
  const hasRating = course.review_count > 0 && course.average_rating != null
  const rating = hasRating ? new Intl.NumberFormat(i18n.resolvedLanguage, {
    minimumFractionDigits: 1, maximumFractionDigits: 1,
  }).format(course.average_rating) : null
  const canAccessLessons = authed && Boolean(enrollment)

  return (
    <article className="course-overview" ref={pageRef} aria-labelledby="course-overview-title">
      <nav className="course-overview-breadcrumb" aria-label={t('courseOverview.breadcrumb')}>
        <Link className="course-overview-back" to="/"><ArrowLeft size={16} aria-hidden="true" />{t('courseOverview.backToCatalog')}</Link>
        <span aria-hidden="true">/</span><span>{t('courseOverview.courseLabel')}</span>
      </nav>

      <Reveal className="course-overview-hero" immediate>
        <header>
          <div className="course-overview-kicker">
            <span className="eyebrow">{t('courseOverview.eyebrow')}</span>
            {course.direction?.name && <span className="course-overview-direction">{course.direction.name}</span>}
          </div>
          <h1 id="course-overview-title">{course.title}</h1>
          {course.description && <p className="course-overview-intro">{course.description}</p>}
          <ul className="course-overview-meta" aria-label={t('courseOverview.summaryLabel')}>
            {course.level && <li><span className="course-overview-level">{t(`levels.${course.level}`, { defaultValue: course.level })}</span></li>}
            <li><Layers3 size={16} aria-hidden="true" />{t('courseOverview.moduleCount', { count: modules.length })}</li>
            <li><BookOpen size={16} aria-hidden="true" />{t('courseOverview.lessonCount', { count: lessonCount })}</li>
            {hasRating && <li><a className="course-overview-rating" href="#course-reviews">
              <span aria-label={t('reviews.ratingOutOfFive', { rating })}><Star size={16} fill="currentColor" aria-hidden="true" />{rating}</span>
              <span>{t('reviews.count', { count: course.review_count })}</span>
            </a></li>}
          </ul>
          {course.author && <p className="course-overview-author"><UserRound size={15} aria-hidden="true" />{t('course.author', { author: course.author })}</p>}
        </header>
      </Reveal>

      <nav className="course-overview-sections" aria-label={t('courseOverview.sectionNavigation')}>
        <a href="#course-about">{t('courseOverview.about')}</a>
        <a href="#course-curriculum">{t('course.curriculum')}</a>
        <a href="#course-reviews">{t('reviews.title')}</a>
      </nav>

      <div className="course-overview-grid">
        <aside className="course-overview-sidebar" aria-labelledby="course-access-title">
          <Reveal immediate delay={0.1}>
            <div className="course-overview-access" id="course-access">
              <span className="course-overview-access-icon" aria-hidden="true"><BookOpen size={23} strokeWidth={1.4} /></span>
              <p className="eyebrow">{t('courseOverview.accessEyebrow')}</p>
              <h2 id="course-access-title">{t('courseOverview.accessTitle')}</h2>
              <p className="course-overview-access-policy">{t(course.enrollment_mode === 'open' ? 'courseOverview.openAccess' : 'courseOverview.approvalAccess')}</p>
              <CourseEnrollment course={course} authed={authed} onEnrollmentChange={setEnrollment} />
              <a className="course-overview-syllabus-link" href="#course-curriculum">{t('profile.viewCurriculum')}<ArrowUpRight size={16} aria-hidden="true" /></a>
            </div>
          </Reveal>
        </aside>
        <div className="course-overview-main">
          <Reveal immediate delay={0.05}>
            <section className="course-overview-about" id="course-about" aria-labelledby="course-about-title">
              <p className="eyebrow">{t('courseOverview.aboutEyebrow')}</p>
              <h2 id="course-about-title">{t('courseOverview.about')}</h2>
              <div className="course-overview-description">
                {course.description ? course.description.split(/\n\s*\n/).map((paragraph, index) => <p key={index}>{paragraph}</p>)
                  : <p>{t('courseOverview.noDescription')}</p>}
              </div>
            </section>
          </Reveal>
          <Reveal immediate delay={0.1}>
            <CourseCurriculum modules={modules} canAccessLessons={canAccessLessons} />
          </Reveal>
        </div>
      </div>

      <div className="course-overview-reviews" id="course-reviews">
        <CourseReviews key={slug} slug={slug} enrolled={canAccessLessons} />
      </div>
    </article>
  )
}
