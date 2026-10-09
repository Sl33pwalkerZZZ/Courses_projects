import { useEffect, useState } from 'react'
import { ArrowUpRight, BookOpen, CircleCheck, UserRound } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../api'
import Reveal from '../components/Reveal'
import EnrollmentApplications from '../components/EnrollmentApplications'
import ProfileLearningActivity from '../components/ProfileLearningActivity'
import './Profile.css'

function EnrollmentCard({ enrollment, index }) {
  const { t, i18n } = useTranslation()
  const { id, course, total_lessons, completed_lessons, progress_percent, is_completed, next_lesson_id, next_lesson_title } = enrollment
  const titleId = `enrollment-course-${id}`
  const percentage = new Intl.NumberFormat(i18n.resolvedLanguage, {
    style: 'percent', maximumFractionDigits: 1,
  }).format(progress_percent / 100)
  const lessonCount = t('profile.lessonsCompleted', { completed: completed_lessons, total: total_lessons })

  return (
    <Reveal className="profile-course-reveal" delay={Math.min(index, 3) * 0.06}>
      <article className="profile-course-card" aria-labelledby={titleId}>
        <div className="profile-course-topline">
          <span className="profile-course-direction">{course.direction.name}</span>
          {is_completed && <span className="profile-completed"><CircleCheck size={15} aria-hidden="true" />{t('profile.completed')}</span>}
        </div>
        <h3 id={titleId}><Link to={`/courses/${encodeURIComponent(course.slug)}`}>{course.title}</Link></h3>
        <p className="profile-course-description">{course.description}</p>
        <div className="profile-course-meta">
          <span><UserRound size={14} aria-hidden="true" />{course.author}</span>
          <span>{t(`levels.${course.level}`, { defaultValue: course.level })}</span>
        </div>
        <div className="profile-course-progress">
          <div className="profile-progress-heading"><span>{t('profile.progress')}</span><strong>{percentage}</strong></div>
          <progress className="profile-progress-bar" max={100} value={progress_percent}
            aria-label={t('profile.progressLabel', { course: course.title })} aria-valuetext={`${lessonCount} · ${percentage}`} />
          <p className="profile-lesson-count">{lessonCount}</p>
        </div>
        <div className="profile-course-actions">
          {!is_completed && next_lesson_id !== null ? (
            <>
              <p className="profile-next-lesson">{t('profile.nextLesson', { title: next_lesson_title })}</p>
              <Link className="academic-button profile-continue" to={`/lessons/${next_lesson_id}`}>
                {t('profile.continueLearning')} <ArrowUpRight size={17} aria-hidden="true" />
              </Link>
            </>
          ) : (
            <>
              {!is_completed && <p className="profile-next-lesson">{t('profile.noLessons')}</p>}
              <Link className="profile-curriculum-link" to={`/courses/${encodeURIComponent(course.slug)}`}>
                {t('profile.viewCurriculum')} <ArrowUpRight size={16} aria-hidden="true" />
              </Link>
            </>
          )}
        </div>
      </article>
    </Reveal>
  )
}

export function ProfileLearningSections({ enrollments }) {
  const { t } = useTranslation()
  return <>
    <section aria-labelledby="profile-courses-title">
      <div className="profile-courses-heading">
        <h2 id="profile-courses-title">{t('profile.coursesTitle')}</h2>
        <p>{t('profile.coursesDescription')}</p>
      </div>
      {enrollments.length ? (
        <div className="academic-course-grid">
          {enrollments.map((enrollment, index) => <EnrollmentCard key={enrollment.id} enrollment={enrollment} index={index} />)}
        </div>
      ) : (
        <div className="catalog-state">
          <BookOpen size={30} aria-hidden="true" /><h3>{t('profile.emptyTitle')}</h3>
          <p>{t('profile.emptyDescription')}</p>
          <Link className="academic-button" to="/">{t('header.catalog')}</Link>
        </div>
      )}
    </section>
    <EnrollmentApplications />
  </>
}

export default function Profile() {
  const { t } = useTranslation()
  const [account, setAccount] = useState(null)
  const [error, setError] = useState(false)
  const [retry, setRetry] = useState(0)

  useEffect(() => {
    let active = true
    Promise.all([api.get('/auth/me/'), api.get('/my/enrollments/')])
      .then(([user, enrollments]) => {
        if (active) setAccount({ user: user.data, enrollments: enrollments.data })
      })
      .catch(() => { if (active) setError(true) })
    return () => { active = false }
  }, [retry])

  function retryLoading() {
    setError(false)
    setAccount(null)
    setRetry((value) => value + 1)
  }

  return (
    <section className="profile-page" aria-labelledby="profile-title" aria-busy={!account && !error}>
      <Reveal className="profile-heading" immediate>
        <p className="eyebrow">{t('profile.eyebrow')}</p>
        <h1 id="profile-title">{t('header.profile')}</h1>
        {account && (
          <div className="profile-account">
            <span className="profile-avatar"><UserRound size={24} aria-hidden="true" /></span>
            <div>
              <p className="profile-username">{account.user.username}</p>
              <dl className="profile-account-details">
                <div><dt>{t('auth.email')}</dt><dd>{account.user.email || t('profile.emailNotProvided')}</dd></div>
                <div><dt>{t('profile.role')}</dt><dd><span className="profile-role-badge">
                  {t(`profile.roles.${account.user.role}`, { defaultValue: account.user.role })}
                </span></dd></div>
              </dl>
            </div>
            <button className="profile-refresh" type="button" onClick={retryLoading}>{t('enrollment.refreshStatus')}</button>
          </div>
        )}
      </Reveal>
      <ProfileLearningActivity key={retry} />
      {error ? (
        <div className="catalog-state" role="alert">
          <UserRound size={30} aria-hidden="true" /><h2>{t('profile.errorTitle')}</h2>
          <p>{t('profile.error')}</p>
          <button className="academic-button" type="button" onClick={retryLoading}>{t('common.retry')}</button>
          <Link className="profile-sign-in" to="/login">{t('header.login')}</Link>
        </div>
      ) : !account ? <p className="profile-loading" role="status">{t('common.loading')}</p> : <>
        <ProfileLearningSections enrollments={account.enrollments} />
      </>}
    </section>
  )
}
