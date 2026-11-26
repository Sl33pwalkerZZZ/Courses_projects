import { ArrowUpRight, Cpu, Layers3, Network, Star, UserRound, Workflow } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion } from 'motion/react'
import { useReducedMotion } from '../hooks/useMotionPreferences'
import './CourseCard.css'

const SYMBOLS = [Cpu, Workflow, Layers3, Network]

// A stable decorative identity for each real direction, independent of sort/filter.
function subjectIdentity(slug = '') {
  return [...slug].reduce((hash, character) => (hash * 31 + character.codePointAt(0)) >>> 0, 0) % SYMBOLS.length
}

export default function CourseCard({ course, index = 0 }) {
  const { t, i18n } = useTranslation()
  const reducedMotion = useReducedMotion()
  const identity = subjectIdentity(course.direction.slug)
  const Symbol = SYMBOLS[identity]
  const hasReviews = course.review_count > 0 && course.average_rating != null
  const rating = hasReviews ? new Intl.NumberFormat(i18n.resolvedLanguage, {
    minimumFractionDigits: 1, maximumFractionDigits: 1,
  }).format(course.average_rating) : null

  return (
    <motion.div layout="position" className="course-card-reveal"
      initial={reducedMotion ? false : { y: 12 }} whileInView={{ y: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: reducedMotion ? 0 : 0.24, delay: reducedMotion ? 0 : Math.min(index, 4) * 0.04, ease: [0.2, 0.8, 0.2, 1] }}>
      <Link to={`/courses/${encodeURIComponent(course.slug)}`} className="academic-course-card" aria-labelledby={`course-title-${course.id}`}>
        <div className={`course-card-cover studio-subject--${identity}`} aria-hidden="true">
          <svg viewBox="0 0 240 220" focusable="false">
            <g className="course-cover-orbits" transform={`rotate(${identity * 30} 120 110)`}>
              <ellipse cx="120" cy="110" rx="88" ry="35" />
              <ellipse cx="120" cy="110" rx="88" ry="35" transform="rotate(60 120 110)" />
              <ellipse cx="120" cy="110" rx="88" ry="35" transform="rotate(120 120 110)" />
              <circle cx="120" cy="110" r="67" />
            </g>
          </svg>
          <span className="course-cover-symbol"><Symbol size={34} strokeWidth={1.4} /></span>
        </div>
        <div className="course-card-content">
          <div className="course-card-category">{course.direction.name}</div>
          <h3 id={`course-title-${course.id}`}>{course.title}</h3>
          <p className="academic-card-description">{course.description}</p>
          <div className="course-card-details">
            <div className="academic-card-meta"><UserRound size={16} aria-hidden="true" /><span>{course.author}</span></div>
            <div className="academic-card-rating">
              {hasReviews ? <>
                <span className="card-rating-value" aria-label={t('reviews.ratingOutOfFive', { rating })}>
                  <Star size={16} fill="currentColor" aria-hidden="true" />{rating}
                </span>
                <span>{t('reviews.count', { count: course.review_count })}</span>
              </> : <span>{t('reviews.noReviews')}</span>}
            </div>
          </div>
          <div className="academic-card-bottom">
            <span>{t(`levels.${course.level}`, { defaultValue: course.level })}</span>
            <span className="card-open">{t('card.open')}<ArrowUpRight size={16} aria-hidden="true" /></span>
          </div>
        </div>
      </Link>
    </motion.div>
  )
}
