import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useLocation, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, BookOpen, CircleCheck, LockKeyhole } from 'lucide-react'
import api from '../api'
import useAuth from '../hooks/useAuth'
import LessonCourseSidebar from '../components/LessonCourseSidebar'
import LessonQuiz from '../components/LessonQuiz'
import { lessonErrorKey, lessonNavigation, loadCourseOutline, loadEnrollmentProgress, saveLessonCompletion } from '../utils/lessons'
import './LessonView.css'

export default function LessonView() {
  const { id } = useParams()
  const { state } = useLocation()
  const authed = useAuth()
  // Changing lesson or logging out must discard the previous lesson's private state.
  return authed ? <LessonWorkspace key={`${id}:${authed}`} id={id} courseSlug={state?.courseSlug} />
    : <LessonWorkspaceStatus error="lessonWorkspace.signIn" courseSlug={state?.courseSlug} />
}

export function LessonWorkspaceStatus({ error, courseSlug, onRetry }) {
  const { t } = useTranslation()
  return <section className="lesson-workspace lesson-workspace-status" role={error ? 'alert' : 'status'} aria-busy={!error}>
    {error ? <LockKeyhole size={28} aria-hidden="true" /> : <BookOpen size={28} aria-hidden="true" />}
    <h1>{t(error || 'common.loading')}</h1>
    {error && <>
      <p>{t(`${error}Description`)}</p>
      <div className="lesson-workspace-status-actions">
        {error === 'lessonWorkspace.signIn' && <Link className="academic-button" to="/login">{t('header.login')}</Link>}
        {onRetry && error !== 'lessonWorkspace.signIn' && <button className="academic-button" type="button" onClick={onRetry}>{t('common.retry')}</button>}
        <Link to={courseSlug ? `/courses/${encodeURIComponent(courseSlug)}` : '/'}>
          {t(courseSlug ? 'lessonWorkspace.backToCourse' : 'courseOverview.backToCatalog')}
        </Link>
      </div>
    </>}
  </section>
}

export function LessonMaterial({ lesson }) {
  const { t } = useTranslation()
  return <div className="lesson-material">
    {lesson.text_content?.trim() ? <div className="lesson-material-text">
      {lesson.text_content.split(/\n\s*\n/).map((paragraph, index) => <p key={index}>{paragraph}</p>)}
    </div> : <div className="lesson-material-empty"><BookOpen size={24} aria-hidden="true" /><p>{t('lessonWorkspace.emptyMaterial')}</p></div>}
    {lesson.images?.length > 0 && <div className="lesson-material-images">
      {lesson.images.map((image) => <img key={image.id} src={image.image} alt="" loading="lazy" />)}
    </div>}
    {lesson.assignments?.length > 0 && <section className="lesson-material-assignments" aria-labelledby="lesson-assignments-title">
      <p className="eyebrow">{t('lessonWorkspace.practice')}</p>
      <h2 id="lesson-assignments-title">{t('lesson.assignment')}</h2>
      {lesson.assignments.map((assignment) => <p key={assignment.id}>{assignment.description}</p>)}
    </section>}
  </div>
}

function LessonWorkspace({ id, courseSlug }) {
  const { t } = useTranslation()
  const activeRef = useRef(true)
  const submittingRef = useRef(false)
  const [lesson, setLesson] = useState(null)
  const [error, setError] = useState('')
  const [retry, setRetry] = useState(0)
  const [outline, setOutline] = useState(null)
  const [outlineError, setOutlineError] = useState(false)
  const [outlineRetry, setOutlineRetry] = useState(0)
  const [completing, setCompleting] = useState(false)
  const [completeError, setCompleteError] = useState('')
  const [progressLoading, setProgressLoading] = useState(false)
  const [progressError, setProgressError] = useState(false)

  useEffect(() => {
    activeRef.current = true
    return () => { activeRef.current = false }
  }, [])

  useEffect(() => {
    let active = true
    api.get(`/lessons/${encodeURIComponent(id)}/`).then(({ data }) => {
      if (active) setLesson(data)
    }).catch((failure) => { if (active) setError(lessonErrorKey(failure)) })
    return () => { active = false }
  }, [id, retry])

  const slug = lesson?.course_slug
  useEffect(() => {
    if (!slug) return
    let active = true
    loadCourseOutline(api, slug).then((data) => {
      if (active) setOutline(data)
    }).catch(() => { if (active) setOutlineError(true) })
    return () => { active = false }
  }, [slug, outlineRetry])

  function retryLesson() {
    setError('')
    setRetry((value) => value + 1)
  }

  function retryOutline() {
    setOutlineError(false)
    setOutlineRetry((value) => value + 1)
  }

  async function refreshProgress() {
    setProgressLoading(true)
    setProgressError(false)
    try {
      const enrollment = await loadEnrollmentProgress(api, slug)
      if (activeRef.current) setOutline((current) => ({ ...current, enrollment }))
    } catch {
      if (activeRef.current) setProgressError(true)
    } finally {
      if (activeRef.current) setProgressLoading(false)
    }
  }

  async function handleComplete() {
    if (lesson.completed_at || submittingRef.current || !outline?.enrollment) return
    submittingRef.current = true
    setCompleting(true)
    setCompleteError('')
    try {
      const completedAt = await saveLessonCompletion(api, id)
      if (!activeRef.current) return
      setLesson((current) => ({ ...current, completed_at: completedAt }))
      await refreshProgress()
    } catch (failure) {
      if (activeRef.current) setCompleteError(failure.response?.status === 403 ? 'lessonWorkspace.accessDenied' : 'lesson.completeError')
    } finally {
      submittingRef.current = false
      if (activeRef.current) setCompleting(false)
    }
  }

  if (error || !lesson) return <LessonWorkspaceStatus error={error} courseSlug={courseSlug} onRetry={retryLesson} />

  const navigation = outline ? lessonNavigation(outline.course.modules, id) : null
  const completed = Boolean(lesson.completed_at)
  // The current lesson's detail/POST confirmation stays authoritative even if a progress refresh fails.
  const completedIds = (outline?.enrollment?.completed_lesson_ids || []).filter((lessonId) => lessonId !== lesson.id)
  if (completed) completedIds.push(lesson.id)
  const courseLink = `/courses/${encodeURIComponent(lesson.course_slug)}`

  return <div className="lesson-workspace">
    <div className="lesson-workspace-grid">
      {outline ? <LessonCourseSidebar course={outline.course} lessonId={id} completedIds={completedIds}
        enrollment={outline.enrollment} progressLoading={progressLoading} progressError={progressError} onRefresh={refreshProgress} />
        : <aside className="lesson-course-sidebar lesson-outline-state" aria-label={t('lessonWorkspace.outline')}>
          <BookOpen size={22} aria-hidden="true" />
          {outlineError ? <div role="alert"><p>{t('lessonWorkspace.outlineError')}</p>
            <button className="lesson-text-button" type="button" onClick={retryOutline}>{t('common.retry')}</button></div>
            : <p role="status">{t('common.loading')}</p>}
          <Link to={courseLink}>{t('lessonWorkspace.backToCourse')}</Link>
        </aside>}

      <article className="lesson-reading-area" aria-labelledby="lesson-title">
        <header className="lesson-reading-header">
          <Link className="lesson-reading-back" to={courseLink}><ArrowLeft size={16} aria-hidden="true" />{t('lessonWorkspace.backToCourse')}</Link>
          <p className="eyebrow">{navigation ? t('lessonWorkspace.moduleLabel', { number: navigation.module.order ?? navigation.moduleIndex + 1 }) : t('lessonWorkspace.learningSpace')}</p>
          {navigation && <p className="lesson-module-name">{navigation.module.title}</p>}
          <div className="lesson-title-row">
            <h1 id="lesson-title">{lesson.title}</h1>
            {completed && <span className="lesson-completed-badge"><CircleCheck size={16} aria-hidden="true" />{t('profile.completed')}</span>}
          </div>
          {navigation && <p className="lesson-position">{t('lessonWorkspace.lessonPosition', {
            number: navigation.lessonIndex + 1, total: navigation.module.lessons.length,
          })}</p>}
        </header>

        <LessonMaterial lesson={lesson} />
        {outline?.enrollment && <LessonQuiz key={lesson.id} lessonId={lesson.id} />}

        <section className="lesson-completion" aria-label={t('lessonWorkspace.completion')} aria-busy={completing}>
          <div><h2>{t(completed ? 'lessonWorkspace.savedTitle' : 'lessonWorkspace.finishTitle')}</h2>
            <p>{t(completed ? 'lessonWorkspace.savedDescription' : 'lessonWorkspace.finishDescription')}</p></div>
          <button className="academic-button lesson-complete-button" type="button" onClick={handleComplete}
            disabled={completed || completing || !outline?.enrollment}>
            <CircleCheck size={18} aria-hidden="true" />{t(completed ? 'lesson.completed' : completing ? 'lesson.completing' : 'lesson.complete')}
          </button>
          {completeError && <p className="error" role="alert">{t(completeError)}</p>}
          {!outline?.enrollment && <p className="lesson-completion-hint">{t(outline ? 'lessonWorkspace.previewOnly' : 'lessonWorkspace.checkingProgress')}</p>}
        </section>

        {navigation ? <nav className="lesson-pagination" aria-label={t('lessonWorkspace.lessonNavigation')}>
          {navigation.previous && <Link className="lesson-pagination-link lesson-previous" to={`/lessons/${navigation.previous.id}`} state={{ courseSlug: lesson.course_slug }}>
            <ArrowLeft size={18} aria-hidden="true" /><span><small>{t('lessonWorkspace.previous')}</small>{navigation.previous.title}</span>
          </Link>}
          {navigation.next && <Link className="lesson-pagination-link lesson-next" to={`/lessons/${navigation.next.id}`} state={{ courseSlug: lesson.course_slug }}>
            <span><small>{t('lessonWorkspace.next')}</small>{navigation.next.title}</span><ArrowRight size={18} aria-hidden="true" />
          </Link>}
          {!navigation.next && <Link className="lesson-pagination-link lesson-next" to={courseLink}>
            <span><small>{t('lessonWorkspace.endOfCurriculum')}</small>{t('lessonWorkspace.backToCourse')}</span><ArrowRight size={18} aria-hidden="true" />
          </Link>}
        </nav> : outline && <p className="lesson-curriculum-changed" role="status">{t('lessonWorkspace.curriculumChanged')}</p>}
      </article>
    </div>
  </div>
}
