import { Link } from 'react-router-dom'
import { ArrowUpRight, BookOpen, Layers3, Plus, FileUp } from 'lucide-react'
import { motion } from 'motion/react'
import { useTranslation } from 'react-i18next'
import { useReducedMotion } from '../../hooks/useMotionPreferences'
import Button from '../ui/Button'

export default function StudioCourseCollection({ courses, compact = false }) {
  const { t, i18n } = useTranslation()
  const reduced = useReducedMotion()
  const number = value => new Intl.NumberFormat(i18n.resolvedLanguage).format(value)
  if (!courses.length) return <div className="studio-empty-projects">
    <BookOpen size={36} strokeWidth={1.2} aria-hidden="true" /><h3>{t('instructorStudio.noCourses')}</h3>
    <p>{t('studioVisual.emptyDescription')}</p><div className="studio-action-group"><Button to="/instructor/courses/new"><Plus size={18} aria-hidden="true" />{t('instructorStudio.newCourse')}</Button>
      <Button to="/instructor/import" variant="secondary"><FileUp size={18} aria-hidden="true" />{t('instructorStudio.import')}</Button></div>
  </div>
  return <div className={`studio-project-grid${compact ? ' studio-project-grid--compact' : ''}`}>
    {courses.map((course, index) => <motion.article className={`studio-project${index === 0 ? ' studio-project--lead' : ''}`} key={course.id}
      whileHover={reduced ? undefined : { y: -3 }} transition={{ duration: .2, ease: [.2,.8,.2,1] }}>
      <header className="studio-project-top"><span className="studio-project-number" aria-hidden="true">{String(index + 1).padStart(2,'0')}</span>
        <span className="studio-project-status" data-published={course.is_published}>{t(`instructorStudio.${course.is_published ? 'published' : 'draft'}`)}</span>
        {course.language && <span className="studio-project-language">{course.language.toUpperCase()}</span>}</header>
      <div className="studio-project-content"><p className="studio-project-direction">{course.direction?.name}</p>
        <h3><Link to={`/instructor/courses/${course.id}/edit`}>{course.title}</Link></h3>
        <p className="studio-project-description">{course.description}</p>
      </div>
      <dl className="studio-project-meta">
        {Number.isFinite(course.module_count) && <div><dt><Layers3 size={16} aria-hidden="true" />{t('studioVisual.modules')}</dt><dd>{number(course.module_count)}</dd></div>}
        {Number.isFinite(course.lesson_count) && <div><dt><BookOpen size={16} aria-hidden="true" />{t('studioVisual.lessons')}</dt><dd>{number(course.lesson_count)}</dd></div>}
        {course.level && <div><dt>{t('instructorStudio.level')}</dt><dd>{t(`levels.${course.level}`, { defaultValue: course.level })}</dd></div>}
      </dl>
      <footer className="studio-project-actions"><Link to={`/instructor/courses/${course.id}/curriculum`} aria-label={`${t('instructorStudio.curriculum')}: ${course.title}`}>{t('instructorStudio.curriculum')}<ArrowUpRight size={18} aria-hidden="true" /></Link>
        <Link to={`/instructor/courses/${course.id}/edit`} aria-label={`${t('instructorStudio.edit')}: ${course.title}`}>{t('instructorStudio.edit')}</Link></footer>
    </motion.article>)}
  </div>
}
