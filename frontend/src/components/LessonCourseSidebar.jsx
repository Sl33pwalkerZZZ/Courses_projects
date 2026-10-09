import { useEffect, useId, useState } from 'react'
import { BookOpen, ChevronDown, Circle, CircleCheck, ListTree, ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion, useReducedMotion } from 'motion/react'
import { orderCurriculum } from '../utils/lessons'

export default function LessonCourseSidebar({ course, lessonId, completedIds = [], enrollment, progressLoading, progressError, onRefresh }) {
  const { t, i18n } = useTranslation()
  const reducedMotion = useReducedMotion()
  const outlineId = useId()
  const modules = orderCurriculum(course.modules)
  const [expanded, setExpanded] = useState(() => new Set(
    modules.filter((module) => module.lessons.some((lesson) => lesson.id === Number(lessonId))).map((module) => module.id),
  ))
  const [compact, setCompact] = useState(() => typeof window !== 'undefined' && window.matchMedia('(max-width: 900px)').matches)
  const [outlineOpen, setOutlineOpen] = useState(false)
  const completed = new Set(completedIds)
  const number = new Intl.NumberFormat(i18n.resolvedLanguage, { minimumIntegerDigits: 2 })
  const percent = enrollment ? new Intl.NumberFormat(i18n.resolvedLanguage, {
    style: 'percent', maximumFractionDigits: 1,
  }).format(enrollment.progress_percent / 100) : null

  useEffect(() => {
    const media = window.matchMedia('(max-width: 900px)')
    const update = () => setCompact(media.matches)
    update()
    media.addEventListener('change', update)
    return () => media.removeEventListener('change', update)
  }, [])

  function toggleModule(id) {
    setExpanded((current) => {
      const next = new Set(current)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return <aside className="lesson-course-sidebar" aria-label={t('lessonWorkspace.outline')}>
    <details className="lesson-outline-disclosure" open={!compact || outlineOpen}
      onToggle={(event) => { if (compact) setOutlineOpen(event.currentTarget.open) }}>
      <summary className="lesson-outline-toggle"><ListTree size={19} aria-hidden="true" />
        <span>{t('lessonWorkspace.outline')}</span><ChevronDown size={18} aria-hidden="true" />
      </summary>
      <div className="lesson-outline-body">
        <div className="lesson-outline-course">
          <p className="eyebrow">{t('lessonWorkspace.yourCourse')}</p>
          <h2>{course.title}</h2>
          <Link className="lesson-outline-back" to={`/courses/${encodeURIComponent(course.slug)}`}>
            <ArrowLeft size={15} aria-hidden="true" />{t('lessonWorkspace.backToCourse')}
          </Link>
        </div>
        <div className="lesson-outline-progress" aria-busy={progressLoading}>
          {enrollment ? <>
            <div className="lesson-outline-progress-label"><span>{t('profile.progress')}</span><strong>{percent}</strong></div>
            <progress max={100} value={enrollment.progress_percent} aria-label={t('profile.progressLabel', { course: course.title })} />
            <p>{t('profile.lessonsCompleted', { completed: enrollment.completed_lessons, total: enrollment.total_lessons })}</p>
          </> : <p>{t('lessonWorkspace.previewOnly')}</p>}
          {progressLoading && <p role="status">{t('lessonWorkspace.updatingProgress')}</p>}
          {progressError && <div className="lesson-outline-progress-error" role="alert">
            <p>{t('lessonWorkspace.progressError')}</p>
            <button className="lesson-text-button" type="button" onClick={onRefresh} disabled={progressLoading}>{t('common.retry')}</button>
          </div>}
        </div>
        <nav className="lesson-outline-modules" aria-label={t('lessonWorkspace.lessonNavigation')}>
          {modules.map((module, index) => {
            const isExpanded = expanded.has(module.id)
            const buttonId = `${outlineId}-${module.id}`
            return <div className="lesson-outline-module" key={module.id}>
              <h3><button className="lesson-outline-module-toggle" type="button" id={buttonId} aria-expanded={isExpanded}
                aria-controls={`${buttonId}-panel`} onClick={() => toggleModule(module.id)}>
                <span className="lesson-outline-module-number">{number.format(module.order ?? index + 1)}</span>
                <span>{module.title}</span><ChevronDown size={16} aria-hidden="true" />
              </button></h3>
              <motion.div id={`${buttonId}-panel`} className="lesson-outline-panel" role="region" aria-labelledby={buttonId}
                aria-hidden={!isExpanded} inert={!isExpanded} initial={false}
                animate={isExpanded ? { height: 'auto', opacity: 1 } : { height: 0, opacity: 0 }}
                transition={{ duration: reducedMotion ? 0 : 0.18 }}>
                {module.lessons.length ? <ol className="lesson-outline-lessons">
                  {module.lessons.map((lesson, lessonIndex) => {
                    const isCurrent = lesson.id === Number(lessonId)
                    const isCompleted = completed.has(lesson.id)
                    return <li key={lesson.id}><Link className={`lesson-outline-link${isCompleted ? ' is-completed' : ''}`}
                      to={`/lessons/${lesson.id}`} state={{ courseSlug: course.slug }} aria-current={isCurrent ? 'page' : undefined}>
                      {isCompleted ? <CircleCheck size={17} aria-hidden="true" /> : <Circle size={15} aria-hidden="true" />}
                      <span><span className="lesson-outline-lesson-number">{number.format(lesson.order ?? lessonIndex + 1)}</span>{lesson.title}</span>
                      {isCompleted && <span className="sr-only">{t('lessonWorkspace.completedLesson')}</span>}
                    </Link></li>
                  })}
                </ol> : <p className="lesson-outline-empty">{t('courseOverview.noLessons')}</p>}
              </motion.div>
            </div>
          })}
          {!modules.length && <p className="lesson-outline-empty"><BookOpen size={17} aria-hidden="true" />{t('courseOverview.noModules')}</p>}
        </nav>
      </div>
    </details>
  </aside>
}
