import { ArrowUpRight, BookOpen, Star, UserRound } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion, useMotionValue, useReducedMotion } from 'motion/react'
import './CourseCard.css'

const MotionLink = motion.create(Link)

export default function CourseCard({ course, index = 0 }) {
  const { t, i18n } = useTranslation()
  const reducedMotion = useReducedMotion()
  const pointerX = useMotionValue('0px')
  const pointerY = useMotionValue('0px')
  const tiltX = useMotionValue('0deg')
  const tiltY = useMotionValue('0deg')
  const shineX = useMotionValue('50%')
  const shineY = useMotionValue('50%')

  function resetPointer() {
    pointerX.set('0px')
    pointerY.set('0px')
    tiltX.set('0deg')
    tiltY.set('0deg')
    shineX.set('50%')
    shineY.set('50%')
  }

  function movePointer(event) {
    if (reducedMotion || !window.matchMedia('(hover: hover) and (pointer: fine)').matches
      || event.currentTarget.matches(':focus-visible')) {
      resetPointer()
      return
    }
    // Measure the landed wrapper, so the card's tilt does not change these bounds.
    const bounds = event.currentTarget.parentElement.getBoundingClientRect()
    const x = Math.max(-1, Math.min(1, (event.clientX - bounds.left) / bounds.width * 2 - 1))
    const y = Math.max(-1, Math.min(1, (event.clientY - bounds.top) / bounds.height * 2 - 1))
    pointerX.set(`${x * 4.5}px`)
    pointerY.set(`${y * 3.5}px`)
    tiltX.set(`${-y * 2.5}deg`)
    tiltY.set(`${x * 3}deg`)
    shineX.set(`${(x + 1) * 50}%`)
    shineY.set(`${(y + 1) * 50}%`)
  }

  const hasReviews = course.review_count > 0 && course.average_rating != null
  const rating = hasReviews ? new Intl.NumberFormat(i18n.resolvedLanguage, {
    minimumFractionDigits: 1, maximumFractionDigits: 1,
  }).format(course.average_rating) : null
  return (
    <motion.div className="course-card-reveal"
      initial={reducedMotion ? false : { opacity: 0, y: 36, scale: 0.975, rotateX: 3 }}
      whileInView={{ opacity: 1, y: 0, scale: 1, rotateX: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: reducedMotion ? 0 : 0.6, delay: reducedMotion ? 0 : Math.min(index, 5) * 0.055, ease: [0.22, 1, 0.36, 1] }}>
      <MotionLink to={`/courses/${encodeURIComponent(course.slug)}`} className="academic-course-card" aria-labelledby={`course-title-${course.id}`}
        style={{ '--pointer-x': pointerX, '--pointer-y': pointerY, '--pointer-tilt-x': tiltX, '--pointer-tilt-y': tiltY, '--shine-x': shineX, '--shine-y': shineY }}
        onPointerMove={movePointer} onPointerLeave={resetPointer} onBlur={resetPointer}
        onFocus={(event) => { if (event.currentTarget.matches(':focus-visible')) resetPointer() }}>
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
      </MotionLink>
    </motion.div>
  )
}
