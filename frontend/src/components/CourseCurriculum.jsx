import { useId, useState } from 'react'
import { ArrowUpRight, BookOpen, ChevronDown, LockKeyhole } from 'lucide-react'
import { motion, useReducedMotion } from 'motion/react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import './CourseCurriculum.css'

export default function CourseCurriculum({ modules = [], canAccessLessons = false }) {
  const { t, i18n } = useTranslation()
  const reducedMotion = useReducedMotion()
  const curriculumId = useId()
  const [expanded, setExpanded] = useState(() => new Set(modules.length ? [modules[0].id] : []))
  const allExpanded = modules.length > 0 && modules.every((module) => expanded.has(module.id))
  const numberFormat = new Intl.NumberFormat(i18n.resolvedLanguage, { minimumIntegerDigits: 2 })

  function toggleModule(id) {
    setExpanded((current) => {
      const next = new Set(current)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <section className="course-curriculum" id="course-curriculum" aria-labelledby="course-curriculum-title">
      <div className="course-curriculum-heading">
        <div><p className="eyebrow">{t('courseOverview.curriculumEyebrow')}</p><h2 id="course-curriculum-title">{t('course.curriculum')}</h2></div>
        {modules.length > 1 && <button className="curriculum-expand-all" type="button"
          onClick={() => setExpanded(allExpanded ? new Set() : new Set(modules.map((module) => module.id)))}>
          {t(allExpanded ? 'courseOverview.collapseAll' : 'courseOverview.expandAll')}
        </button>}
      </div>
      {!canAccessLessons && modules.length > 0 && <p className="curriculum-preview-note"><LockKeyhole size={14} aria-hidden="true" />{t('courseOverview.previewNote')}</p>}
      {modules.length ? <div className="curriculum-modules">
        {modules.map((module, index) => {
          const isExpanded = expanded.has(module.id)
          const lessons = module.lessons || []
          const buttonId = `${curriculumId}-module-${module.id}`
          const panelId = `${buttonId}-panel`
          return (
            <div className="curriculum-module" id={`course-module-${module.id}`} key={module.id} data-expanded={isExpanded}>
              <h3 className="curriculum-module-heading">
                <button className="curriculum-module-toggle" id={buttonId} type="button" aria-expanded={isExpanded}
                  aria-controls={panelId} onClick={() => toggleModule(module.id)}>
                  <span className="curriculum-module-number" aria-hidden="true">{numberFormat.format(module.order ?? index + 1)}</span>
                  <span className="curriculum-module-name"><span>{module.title}</span><span className="curriculum-module-count">{t('courseOverview.lessonCount', { count: lessons.length })}</span></span>
                  <ChevronDown className="curriculum-module-chevron" size={19} aria-hidden="true" />
                </button>
              </h3>
              <motion.div className="curriculum-module-panel" id={panelId} role="region" aria-labelledby={buttonId}
                aria-hidden={!isExpanded} inert={!isExpanded} initial={false}
                animate={isExpanded ? { height: 'auto', opacity: 1 } : { height: 0, opacity: 0 }}
                transition={{ duration: reducedMotion ? 0 : 0.2, ease: 'easeOut' }}>
                <div className="curriculum-module-content">
                  {module.description && <p className="curriculum-module-description">{module.description}</p>}
                  {lessons.length ? <ol className="curriculum-lessons">
                    {lessons.map((lesson) => <li key={lesson.id}>
                      {canAccessLessons ? <Link className="curriculum-lesson curriculum-lesson-link" to={`/lessons/${lesson.id}`}>
                        <BookOpen size={15} aria-hidden="true" /><span>{lesson.title}</span><ArrowUpRight size={16} aria-hidden="true" />
                      </Link> : <div className="curriculum-lesson curriculum-lesson-locked">
                        <BookOpen size={15} aria-hidden="true" /><span>{lesson.title}</span><LockKeyhole size={15} aria-hidden="true" />
                        <span className="sr-only">{t('courseOverview.lockedLesson')}</span>
                      </div>}
                    </li>)}
                  </ol> : <p className="curriculum-empty-lessons">{t('courseOverview.noLessons')}</p>}
                </div>
              </motion.div>
            </div>
          )
        })}
      </div> : <div className="curriculum-empty"><BookOpen size={24} aria-hidden="true" /><p>{t('courseOverview.noModules')}</p></div>}
    </section>
  )
}
