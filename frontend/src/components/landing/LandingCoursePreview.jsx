import { ArrowUpRight, BookOpen, UserRound, Layers3 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

// Only the public catalog response is presented; never invent personal progress.
export default function LandingCoursePreview({ course, loading = false, failed = false }) {
  const { t } = useTranslation()
  return <div className="cinema-course-preview">
    <div className="cinema-preview-bar"><span>AI Courses</span><span>{t('cinema.overview')}</span><Layers3 size={16} aria-hidden="true" /></div>
    {course ? <>
      <div className="cinema-preview-body">
        <p className="cinema-preview-direction"><BookOpen size={16} aria-hidden="true" />{course.direction.name}</p>
        <h3>{course.title}</h3>
        <p className="cinema-preview-description">{course.description}</p>
        <p className="cinema-preview-author"><UserRound size={16} aria-hidden="true" />{course.author}</p>
      </div>
      <div className="cinema-preview-bottom"><span>{t(`levels.${course.level}`, { defaultValue: course.level })}</span>
        <Link aria-label={`${t('card.open')}: ${course.title}`} to={`/courses/${encodeURIComponent(course.slug)}`}>{t('card.open')}<ArrowUpRight size={18} aria-hidden="true" /></Link></div>
    </> : <div className="cinema-preview-body cinema-preview-fallback">
      <BookOpen size={36} strokeWidth={1.2} aria-hidden="true" />
      <h3>{t('cinema.previewTitle')}</h3><p>{t('cinema.previewDescription')}</p>
      <span role="status">{t(failed ? 'catalog.unavailable' : loading ? 'catalog.loading' : 'catalog.emptyTitle')}</span>
    </div>}
  </div>
}
