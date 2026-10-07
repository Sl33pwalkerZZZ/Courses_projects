import { useEffect, useId, useRef, useState } from 'react'
import { Star } from 'lucide-react'
import { Trans, useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import api, { isAuthenticated } from '../api'
import Reveal from './Reveal'
import ReviewDeleteDialog from './ReviewDeleteDialog'
import './CourseReviews.css'

function RatingStars({ rating }) {
  const { t, i18n } = useTranslation()
  const value = new Intl.NumberFormat(i18n.resolvedLanguage, { maximumFractionDigits: 1 }).format(rating)
  return (
    <span className="review-stars" role="img" aria-label={t('reviews.ratingOutOfFive', { rating: value })}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span className="review-star" key={star} aria-hidden="true">
          <Star size={18} />
          <span className="review-star-fill" style={{ width: `${Math.min(1, Math.max(0, rating - star + 1)) * 100}%` }}>
            <Star size={18} fill="currentColor" />
          </span>
        </span>
      ))}
    </span>
  )
}

function ReviewEntry({ review }) {
  const { i18n } = useTranslation()
  const date = new Intl.DateTimeFormat(i18n.resolvedLanguage, { dateStyle: 'medium' }).format(new Date(review.created_at))
  return (
    <article className="review-entry">
      <header className="review-entry-heading">
        <span className="review-author">{review.author}</span>
        <time dateTime={review.created_at}>{date}</time>
      </header>
      <RatingStars rating={review.rating} />
      <p className="review-text">{review.text}</p>
    </article>
  )
}

function submissionErrorKey(error, fallback = 'reviews.submitError') {
  const response = error.response
  if (response?.status === 401) return 'reviews.sessionExpired'
  if (response?.data?.code === 'duplicate_review') return 'reviews.duplicateError'
  if (response?.data?.code === 'not_enrolled') return 'reviews.enrollmentRequired'
  if (response?.data?.rating) return 'reviews.ratingError'
  if (response?.data?.text) return 'reviews.textError'
  return fallback
}

export default function CourseReviews({ slug, enrolled = false }) {
  const { t, i18n } = useTranslation()
  const formId = useId()
  const fetchVersion = useRef(0)
  const editButtonRef = useRef(null)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [reload, setReload] = useState(0)
  const [rating, setRating] = useState(0)
  const [text, setText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [success, setSuccess] = useState('')
  const [editing, setEditing] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')
  const authed = isAuthenticated()
  const endpoint = `/courses/${encodeURIComponent(slug)}/reviews/`

  useEffect(() => {
    let active = true
    const version = ++fetchVersion.current
    api.get(endpoint).then((response) => {
      if (active && version === fetchVersion.current) setData(response.data)
    }).catch((error) => {
      if (active && version === fetchVersion.current) setLoadError(error.response?.status === 401 ? 'reviews.sessionExpired' : 'reviews.loadError')
    }).finally(() => { if (active && version === fetchVersion.current) setLoading(false) })
    return () => { active = false }
  }, [endpoint, reload])

  function reloadReviews() {
    // Invalidate an older fetch immediately, before the next effect runs.
    fetchVersion.current += 1
    setLoading(true)
    setLoadError('')
    setReload((value) => value + 1)
  }

  function startEditing() {
    setRating(data.my_review.rating)
    setText(data.my_review.text)
    setSubmitError('')
    setSuccess('')
    setEditing(true)
    requestAnimationFrame(() => document.getElementById(`${formId}-star-${data.my_review.rating}`)?.focus())
  }

  function cancelEditing() {
    setEditing(false)
    setRating(0)
    setText('')
    setSubmitError('')
    requestAnimationFrame(() => editButtonRef.current?.focus())
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (submitting || loading || deleting) return
    setSubmitError('')
    if (!rating) { setSubmitError('reviews.ratingError'); return }
    if (!text.trim()) { setSubmitError('reviews.textError'); return }
    if (editing && !data.my_review) { setSubmitError('reviews.updateError'); return }
    setSubmitting(true)
    setSuccess('')
    try {
      const payload = { rating, text: text.trim() }
      const response = editing
        ? await api.patch(`/reviews/${data.my_review.id}/`, payload)
        : await api.post(endpoint, payload)
      // A pending review belongs in the private panel, never the public list.
      setData((current) => ({
        ...current, my_review: response.data,
        reviews: editing ? current.reviews.filter((review) => review.id !== response.data.id) : current.reviews,
      }))
      setSuccess(editing ? 'reviews.reviewUpdated' : 'reviews.moderationMessage')
      setEditing(false)
      if (editing) reloadReviews()
      requestAnimationFrame(() => document.getElementById(`${formId}-own-title`)?.focus())
    } catch (error) {
      setSubmitError(submissionErrorKey(error, editing ? 'reviews.updateError' : 'reviews.submitError'))
      if (error.response?.data?.code === 'duplicate_review') reloadReviews()
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete() {
    if (deleting || !deleteTarget) return
    setDeleting(true)
    setDeleteError('')
    try {
      await api.delete(`/reviews/${deleteTarget.id}/`)
      setData((current) => ({
        ...current, my_review: null,
        reviews: current.reviews.filter((review) => review.id !== deleteTarget.id),
      }))
      setDeleteTarget(null)
      setEditing(false)
      setRating(0)
      setText('')
      setSubmitError('')
      setSuccess('reviews.reviewDeleted')
      reloadReviews()
      requestAnimationFrame(() => document.getElementById(`${formId}-form-title`)?.focus())
    } catch (error) {
      setDeleteError(submissionErrorKey(error, 'reviews.deleteError'))
    } finally {
      setDeleting(false)
    }
  }

  const average = data?.average_rating == null ? null : new Intl.NumberFormat(i18n.resolvedLanguage, {
    minimumFractionDigits: 1, maximumFractionDigits: 1,
  }).format(data.average_rating)

  return (
    <Reveal className="course-reviews-reveal">
      <section className="course-reviews" aria-labelledby={`${formId}-title`} aria-busy={loading}>
        <div className="reviews-heading">
          <div><p className="eyebrow">{t('reviews.eyebrow')}</p><h2 id={`${formId}-title`}>{t('reviews.title')}</h2></div>
          {data && <div className="reviews-summary">
            {loading ? <p role="status">{t('common.loading')}</p> : loadError ? null : average !== null ? <>
              <strong className="reviews-average" aria-label={t('reviews.ratingOutOfFive', { rating: average })}>{average}</strong>
              <div><RatingStars rating={data.average_rating} /><p>{t('reviews.count', { count: data.review_count })}</p></div>
            </> : <p>{t('reviews.noReviews')}</p>}
          </div>}
        </div>
        {loading && !data && <p className="reviews-state" role="status">{t('common.loading')}</p>}
        {loadError && <div className="reviews-load-error">
          <p className="reviews-error" role="alert">{t(loadError)}</p>
          <button className="reviews-retry" type="button" onClick={reloadReviews} disabled={loading || submitting || deleting}>{t('common.retry')}</button>
          {loadError === 'reviews.sessionExpired' && <Link to="/login">{t('header.login')}</Link>}
        </div>}
        {data && <>
          <div className="reviews-list">
            {data.reviews.length ? data.reviews.map((review) => <ReviewEntry key={review.id} review={review} />) : (
              <p className="reviews-state">{t('reviews.noReviewsDescription')}</p>
            )}
          </div>
          <div className="reviews-participation">
            {submitError && <p className="reviews-error" role="alert">{t(submitError)}</p>}
            {success && <p className="reviews-success" role="status">
              {t(success)}{success === 'reviews.reviewUpdated' && <> {t('reviews.editedModerationMessage')}</>}
            </p>}
            {!authed ? (
              <p className="reviews-state"><Trans i18nKey="reviews.loginToReview" components={{ signIn: <Link to="/login" /> }} /></p>
            ) : data.my_review && !editing ? (
              <div className="reviews-own">
                <div className="reviews-own-heading"><h3 id={`${formId}-own-title`} tabIndex={-1}>{t('reviews.yourReview')}</h3>
                  <span className="review-status" data-status={data.my_review.status}>{t(`reviews.${data.my_review.status}`)}</span>
                </div>
                <ReviewEntry review={data.my_review} />
                {data.my_review.status === 'pending' && !success && <p className="reviews-state">{t('reviews.moderationMessage')}</p>}
                <div className="review-own-actions">
                  <button ref={editButtonRef} className="review-secondary-button review-edit-button" type="button"
                    disabled={loading || submitting || deleting} onClick={startEditing}>{t('reviews.editReview')}</button>
                  <button className="review-delete-button" type="button" disabled={loading || submitting || deleting}
                    onClick={() => { setDeleteError(''); setDeleteTarget(data.my_review) }}>{t('reviews.deleteReview')}</button>
                </div>
              </div>
            ) : editing || data.can_review || enrolled ? (
              <form className="review-form" onSubmit={handleSubmit} aria-labelledby={`${formId}-form-title`} aria-busy={submitting}>
                <h3 id={`${formId}-form-title`} tabIndex={-1}>{t(editing ? 'reviews.editReview' : 'reviews.writeReview')}</h3>
                <fieldset className="review-rating-field" disabled={submitting || loading}>
                  <legend>{t('reviews.yourRating')} <span aria-hidden="true">*</span></legend>
                  <div className="review-rating-options">
                    {[1, 2, 3, 4, 5].map((value) => (
                      <span key={value}>
                        <input className="sr-only review-rating-input" type="radio" name={`${formId}-rating`} id={`${formId}-star-${value}`}
                          value={value} required checked={rating === value} onChange={() => setRating(value)} />
                        <label className="review-rating-choice" htmlFor={`${formId}-star-${value}`} data-selected={value <= rating}
                          aria-label={t('reviews.starLabel', { count: value })}>
                          <Star size={26} fill={value <= rating ? 'currentColor' : 'none'} aria-hidden="true" />
                        </label>
                      </span>
                    ))}
                  </div>
                </fieldset>
                <label className="review-text-label" htmlFor={`${formId}-text`}>{t('reviews.yourReview')} <span aria-hidden="true">*</span></label>
                <textarea id={`${formId}-text`} name="text" required rows={5} value={text} disabled={submitting || loading}
                  onChange={(event) => setText(event.target.value)} aria-describedby={`${formId}-moderation`} />
                <p className="review-form-hint" id={`${formId}-moderation`}>{t(editing ? 'reviews.editModerationHint' : 'reviews.moderationHint')}</p>
                <div className="review-form-actions">
                  <button className="academic-button" type="submit" disabled={submitting || loading}>
                    {t(submitting ? (editing ? 'reviews.saving' : 'reviews.submitting') : (editing ? 'reviews.saveChanges' : 'reviews.submitReview'))}
                  </button>
                  {editing && <button className="review-secondary-button review-cancel-edit" type="button"
                    disabled={submitting || loading} onClick={cancelEditing}>{t('reviews.cancel')}</button>}
                </div>
              </form>
            ) : <p className="reviews-state">{t('reviews.enrollmentRequired')}</p>}
          </div>
        </>}
        {deleteTarget && <ReviewDeleteDialog busy={deleting} error={deleteError}
          onCancel={() => setDeleteTarget(null)} onConfirm={handleDelete} />}
      </section>
    </Reveal>
  )
}
