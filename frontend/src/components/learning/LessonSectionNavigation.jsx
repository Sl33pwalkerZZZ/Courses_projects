import { List } from 'lucide-react'
import { useTranslation } from 'react-i18next'

// Headings and targets come from the same renderer; no lesson IDs or source edits.
export default function LessonSectionNavigation({ sections, prefix }) {
  const { t } = useTranslation()
  if (sections.length < 2) return null
  return <details className="lesson-section-navigation">
    <summary><List size={18} strokeWidth={1.5} aria-hidden="true" />{t('studentVisual.onThisPage')}<span>{sections.length}</span></summary>
    <nav aria-label={t('studentVisual.onThisPage')}><ol>{sections.map((section,index) => <li key={section.heading}>
      <a href={`#${encodeURIComponent(`${prefix}-${index}`)}`}>{section.heading}</a>
    </li>)}</ol></nav>
  </details>
}
