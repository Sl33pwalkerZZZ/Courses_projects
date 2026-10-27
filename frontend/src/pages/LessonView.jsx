import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useLocation, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, BookOpen, CircleCheck, LockKeyhole } from 'lucide-react'
import api from '../api'
import useAuth from '../hooks/useAuth'
import LessonCourseSidebar from '../components/LessonCourseSidebar'
import LessonQuiz from '../components/LessonQuiz'
import ProtectedLessonImage from '../components/ProtectedLessonImage'
import Celebration from '../components/playground/Celebration'
import ReadingProgress from '../components/playground/ReadingProgress'
import { lessonErrorKey, lessonNavigation, loadCourseOutline, loadEnrollmentProgress, saveLessonCompletion } from '../utils/lessons'
import LearningContent, { ContentLanguageNotice, SourceParagraph } from '../components/learning/LearningContent'
import SelectionMap from '../components/learning/SelectionMap'
import { lessonPresentation, lessonReadingBlocks, studentAssignmentDescription, verifiedCourse8Practice } from '../utils/lessonPresentation'
import { studentSourceHeading } from '../utils/sourceHeadings'
import { getCourse8Reading } from '../utils/course8Reading'
import Course8Reading from '../components/learning/Course8Reading'
import MediaLessonReading from '../components/learning/MediaLessonReading'
import { mediaLessonSections } from '../utils/mediaLessonPresentation'
import PracticeCheck from '../components/learning/PracticeCheck'
import LessonResources from '../components/learning/LessonResources'
import './LessonView.css'

export default function LessonView() {
  const { id } = useParams()
  const { state } = useLocation()
  const authed = useAuth()
  // Changing lesson or logging out must discard the previous lesson's private state.
  return authed ? <LessonWorkspace key={`${id}:${authed}`} id={id} courseSlug={state?.courseSlug} preview={Boolean(state?.preview)} />
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

export function LessonMaterial({ lesson, preview = false }) {
  const { t } = useTranslation()
  const presentation = lessonPresentation(lesson)
  const curatedReading = getCourse8Reading(lesson)
  const mediaSections = mediaLessonSections(lesson)
  const verifiedPractice = verifiedCourse8Practice(lesson)
  const language = lesson.content_language || lesson.learning_content?.content_language
  const paragraphs = values => lessonReadingBlocks(values, lesson).map((block, index) => {
    if (block.type === 'instructions') return <ol className="lesson-practice-instructions" key={index}>{block.items.map(item => <li key={item}>{item}</li>)}</ol>
    if (block.type === 'examples') return <section className="lesson-ai-examples" key={index}>
      <h2>{block.heading}</h2><ul>{block.items.map(item => <li key={item}>{item}</li>)}</ul>
    </section>
    const paragraph = block.text
    return /^(?:1\.\d\. |Шаг \d\.|Основные ограничения ИИ$|Связь между ИИ, машинным и глубоким обучением$)/u.test(paragraph.trim())
      ? <h2 key={index}>{studentSourceHeading(paragraph, lesson)}</h2>
      : lesson.learning_content ? <SourceParagraph key={index} text={paragraph} /> : <p key={index}>{paragraph}</p>
  })
  return <div className="lesson-material">
    <ContentLanguageNotice language={language} />
    {lesson.learning_content?.objectives?.length > 0 && <LearningContent content={{ content_language: language, objectives: lesson.learning_content.objectives }} showLanguageNotice={false} />}
    {curatedReading ? <Course8Reading lesson={lesson} /> : lesson.text_content?.trim() ? <div className="lesson-material-text" lang={lesson.content_language || lesson.learning_content?.content_language || undefined}>
      {mediaSections ? <MediaLessonReading sections={mediaSections} /> : paragraphs(presentation.reading)}
    </div> : <div className="lesson-material-empty"><BookOpen size={24} aria-hidden="true" /><p>{t('lessonWorkspace.emptyMaterial')}</p></div>}
    {!curatedReading && (presentation.content?.interactions?.length > 0 || presentation.content?.takeaways?.length > 0) && <LearningContent content={presentation.content} showLanguageNotice={false} />}
    {curatedReading && presentation.content?.takeaways?.length > 0 && <LearningContent content={{ ...presentation.content, interactions: [] }} showLanguageNotice={false} />}
    {curatedReading && <PracticeCheck key={lesson.id} lessonId={lesson.id} />}
    {lesson.images?.length > 0 && <div className="lesson-material-images">
      {lesson.images.map((image) => <ProtectedLessonImage key={image.id} image={image} />)}
    </div>}
    {lesson.assignments?.length > 0 && <section className="lesson-material-assignments" aria-labelledby="lesson-assignments-title">
      <p className="eyebrow">{t('lessonWorkspace.practice')}</p>
      <h2 id="lesson-assignments-title">{t('lesson.assignment')}</h2>
      {lesson.assignments.map((assignment) => <div key={assignment.id}>{assignment.learning_activity === 'ai_selection_map' ? <>
        <p>{t('learning.practiceTransition')}</p>
        {verifiedPractice && <p className="learning-source-note">{t('selectionMap.safety')}</p>}
        <details className="lesson-practice-disclosure"><summary>{t('learning.openPractice')}</summary><SelectionMap key={assignment.id} assignment={assignment} preview={preview} /></details>
        {!verifiedPractice && <details className="lesson-source-disclosure"><summary>{t('learning.practiceReference')}</summary>
          <p lang={language}>{studentAssignmentDescription(assignment.description)}</p>
          {presentation.templates.length > 0 && <LearningContent content={{ content_language: language, interactions: presentation.templates }} showLanguageNotice={false} />}
        </details>}
      </> : <p lang={language}>{assignment.description}</p>}</div>)}
    </section>}
    {presentation.conclusions.length > 0 && <section className="lesson-source-closing lesson-material-text" lang={language}>{paragraphs(presentation.conclusions)}</section>}
    <LessonResources paragraphs={presentation.resources} language={language} />
  </div>
}

function LessonWorkspace({ id, courseSlug, preview }) {
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
  const [celebrate, setCelebrate] = useState(false)
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
    loadCourseOutline(api, slug, preview).then((data) => {
      if (active) setOutline(data)
    }).catch(() => { if (active) setOutlineError(true) })
    return () => { active = false }
  }, [slug, outlineRetry, preview])

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
      setCelebrate(true)
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
  const courseLink = preview ? `/instructor/courses/${encodeURIComponent(lesson.course_slug)}/preview` : `/courses/${encodeURIComponent(lesson.course_slug)}`

  return <div className="lesson-workspace">
    <div className="lesson-workspace-grid">
      {outline ? <LessonCourseSidebar course={outline.course} lessonId={id} completedIds={completedIds}
        preview={preview} enrollment={outline.enrollment} progressLoading={progressLoading} progressError={progressError} onRefresh={refreshProgress} />
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
            <h1 id="lesson-title" lang={lesson.content_language || lesson.learning_content?.content_language || undefined}>{lesson.title}</h1>
            {completed && <span className="lesson-completed-badge"><CircleCheck size={16} aria-hidden="true" />{t('profile.completed')}</span>}
          </div>
          {navigation && <p className="lesson-position">{t('lessonWorkspace.lessonPosition', {
            number: navigation.lessonIndex + 1, total: navigation.module.lessons.length,
          })}</p>}
        </header>

        <ReadingProgress />
        {preview && <p className="learning-source-note">{t('instructorPreview.notice')}</p>}
        <LessonMaterial lesson={lesson} preview={preview} />
        {preview && <p>{t('instructorPreview.quiz')}</p>}
        {outline?.enrollment && <LessonQuiz key={lesson.id} lessonId={lesson.id} />}

        <section className="lesson-completion" aria-label={t('lessonWorkspace.completion')} aria-busy={completing}>
          {celebrate && <Celebration />}
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
          {navigation.previous && <Link className="lesson-pagination-link lesson-previous" to={`/lessons/${navigation.previous.id}`} state={{ courseSlug: lesson.course_slug, preview }}>
            <ArrowLeft size={18} aria-hidden="true" /><span><small>{t('lessonWorkspace.previous')}</small>{navigation.previous.title}</span>
          </Link>}
          {navigation.next && <Link className="lesson-pagination-link lesson-next" to={`/lessons/${navigation.next.id}`} state={{ courseSlug: lesson.course_slug, preview }}>
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
