import { ArrowUpRight, BookOpen, Star, UserRound } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Reveal from './Reveal'
import './CourseCard.css'

export default function CourseCard({ course, index = 0 }) {
  const { t, i18n } = useTranslation()
  const hasReviews = course.review_count > 0 && course.average_rating != null
  const rating = hasReviews ? new Intl.NumberFormat(i18n.resolvedLanguage, {
    minimumFractionDigits: 1, maximumFractionDigits: 1,
  }).format(course.average_rating) : null
  return (
    <Reveal className="course-card-reveal" delay={Math.min(index, 3) * 0.06}>
      <Link to={`/courses/${encodeURIComponent(course.slug)}`} className="academic-course-card" aria-labelledby={`course-title-${course.id}`}>
        <div className={`course-art course-art-${index % 3}`} aria-hidden="true">
          <span className="art-circle art-circle-one" /><span className="art-circle art-circle-two" />
          <span className="art-crosshair" /><BookOpen size={32} strokeWidth={1} />
          <span className="art-caption">{t('card.artLabel')}</span>
          <span className="art-arrow"><ArrowUpRight size={19} /></span>
        </div>
        <div className="academic-card-body">
          <span className="academic-badge">{course.direction.name}</span>
          <h3 id={`course-title-${course.id}`}>{course.title}</h3>
          <p className="academic-card-description">{course.description}</p>
          <div className="academic-card-meta"><UserRound size={14} aria-hidden="true" /><span>{course.author}</span></div>
          <div className="academic-card-rating">
            {hasReviews ? <>
              <span className="card-rating-value" aria-label={t('reviews.ratingOutOfFive', { rating })}>
                <Star size={14} fill="currentColor" aria-hidden="true" />{rating}
              </span>
              <span>{t('reviews.count', { count: course.review_count })}</span>
            </> : <span>{t('reviews.noReviews')}</span>}
          </div>
          <div className="academic-card-bottom">
            <span>{t(`levels.${course.level}`, { defaultValue: course.level })}</span>
            <span className="card-open">{t('card.open')} <ArrowUpRight size={15} aria-hidden="true" /></span>
          </div>
        </div>
      </Link>
    </Reveal>
  )
}
