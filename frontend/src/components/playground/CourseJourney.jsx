import { useTranslation } from 'react-i18next'
import { ArrowDownRight } from 'lucide-react'

export default function CourseJourney({ modules = [] }) {
  const { t } = useTranslation()
  if (!modules.length) return null
  return <nav className="play-course-journey" aria-label={t('course.curriculum')}>
    <p className="eyebrow">{t('courseOverview.curriculumEyebrow')}</p>
    <ol>{modules.map((module, index) => <li key={module.id}>
      <a href={`#course-module-${module.id}`}><span aria-hidden="true">{String(index + 1).padStart(2, '0')}</span><strong>{module.title}</strong><ArrowDownRight size={18} aria-hidden="true" /></a>
    </li>)}</ol>
  </nav>
}
