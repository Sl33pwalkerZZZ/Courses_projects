import { useEffect, useId, useRef, useState } from 'react'
import { Trans, useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import api from '../api'
import { enrollmentErrorKey, loadCourseEnrollment } from '../utils/enrollment'
import './CourseEnrollment.css'

export default function CourseEnrollment({ course, authed, onEnrollmentChange }) {
  const { t } = useTranslation()
  const formId = useId()
  const submittingRef = useRef(false)
  const [state, setState] = useState({ enrollment: null, application: null })
  const [loading, setLoading] = useState(authed)
  const [loadError, setLoadError] = useState('')
  const [reload, setReload] = useState(0)
  const [showForm, setShowForm] = useState(false)
  const [message, setMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [success, setSuccess] = useState('')
  const requiresApproval = course.enrollment_mode !== 'open'
  const { enrollment, application } = state

  useEffect(() => {
    let active = true
    if (authed) {
      loadCourseEnrollment(api, course.slug, requiresApproval).then((data) => {
        if (active) {
          setState(data)
          onEnrollmentChange(data.enrollment)
        }
      }).catch((error) => {
        if (active) setLoadError(enrollmentErrorKey(error, 'enrollment.loadError'))
      }).finally(() => { if (active) setLoading(false) })
    }
    return () => { active = false }
  }, [course.slug, authed, requiresApproval, reload, onEnrollmentChange])

  function refreshState() {
    setLoading(true)
    setLoadError('')
    setReload((value) => value + 1)
  }

  async function handleEnroll() {
    if (submittingRef.current || loading || loadError || enrollment) return
    submittingRef.current = true
    setSubmitting(true)
    setSubmitError('')
    try {
      const { data } = await api.post(`/courses/${encodeURIComponent(course.slug)}/enroll/`)
      const firstLesson = course.modules.flatMap((module) => module.lessons)[0]
      const enrolled = { ...data, next_lesson_id: firstLesson?.id ?? null }
      setState((current) => ({ ...current, enrollment: enrolled }))
      onEnrollmentChange(enrolled)
    } catch (error) {
      setSubmitError(enrollmentErrorKey(error, 'course.enrollError'))
    } finally {
      submittingRef.current = false
      setSubmitting(false)
    }
  }

  async function handleRequest(event) {
    event.preventDefault()
    if (submittingRef.current || loading || loadError || enrollment || application?.status === 'pending') return
    setSubmitError('')
    const motivation = message.trim()
    if (motivation.length < 20 || motivation.length > 1000) {
      setSubmitError('enrollment.messageError')
      return
    }
    submittingRef.current = true
    setSubmitting(true)
    setSuccess('')
    try {
      const { data } = await api.post(`/courses/${encodeURIComponent(course.slug)}/enrollment-requests/`, { message: motivation })
      setState((current) => ({ ...current, application: data }))
      setShowForm(false)
      setMessage('')
      setSuccess('enrollment.submitted')
    } catch (error) {
      setSubmitError(enrollmentErrorKey(error))
      if (['duplicate_pending', 'already_enrolled'].includes(error.response?.data?.code)) {
        setShowForm(false)
        refreshState()
      }
    } finally {
      submittingRef.current = false
      setSubmitting(false)
    }
  }

  let content
  if (!authed) {
    content = <p><Trans i18nKey={requiresApproval ? 'enrollment.signInToRequest' : 'course.signInToStart'}
      components={{ signIn: <Link to="/login" /> }} /></p>
  } else if (loading) {
    content = <p role="status">{t('common.loading')}</p>
  } else if (loadError) {
    content = <>
      <p className="error" role="alert">{t(loadError)}</p>
      <button className="btn-primary" type="button" onClick={refreshState}>{t('common.retry')}</button>
    </>
  } else if (enrollment) {
    const nextLesson = enrollment.next_lesson_id ?? course.modules.flatMap((module) => module.lessons)[0]?.id
    content = <>
      <p>{t('course.enrolled')}</p>
      {nextLesson != null
        ? <Link className="btn-primary enrollment-continue" to={`/lessons/${nextLesson}`}>{t('profile.continueLearning')}</Link>
        : <p>{t('profile.noLessons')}</p>}
    </>
  } else if (!requiresApproval) {
    content = <button className="btn-primary" type="button" onClick={handleEnroll} disabled={submitting}>
      {t(submitting ? 'course.enrolling' : 'course.start')}
    </button>
  } else if (application?.status === 'pending') {
    content = <>
      <p className="enrollment-status" role="status">{t('enrollment.awaitingApproval')}</p>
      <p className="enrollment-hint">{t('enrollment.pendingDescription')}</p>
      <button className="enrollment-text-button" type="button" onClick={refreshState}>{t('enrollment.refreshStatus')}</button>
    </>
  } else if (application?.status === 'approved') {
    content = <>
      <p role="status">{t('enrollment.approvedRefresh')}</p>
      <button className="btn-primary" type="button" onClick={refreshState}>{t('enrollment.refreshStatus')}</button>
    </>
  } else {
    content = <>
      {application?.status === 'rejected' && <div className="enrollment-decision">
        <p className="enrollment-status">{t('enrollment.declined')}</p>
        {application.admin_note && <p className="enrollment-note">{t('enrollment.decisionReason', { reason: application.admin_note })}</p>}
      </div>}
      {showForm ? (
        <form className="enrollment-form" onSubmit={handleRequest} aria-busy={submitting}>
          <h2>{t('enrollment.formTitle', { course: course.title })}</h2>
          <label htmlFor={`${formId}-message`}>{t('enrollment.messageLabel')}</label>
          <textarea id={`${formId}-message`} value={message} onChange={(event) => setMessage(event.target.value)}
            required minLength={20} maxLength={1000} rows={5} disabled={submitting}
            placeholder={t('enrollment.messagePlaceholder')} aria-describedby={`${formId}-hint`} />
          <p className="enrollment-hint" id={`${formId}-hint`}>{t('enrollment.messageHint')}</p>
          <div className="enrollment-form-actions">
            <button className="btn-primary" type="submit" disabled={submitting}>{t(submitting ? 'enrollment.submitting' : 'enrollment.submit')}</button>
            <button className="enrollment-text-button" type="button" disabled={submitting} onClick={() => { setShowForm(false); setSubmitError('') }}>{t('enrollment.cancel')}</button>
          </div>
        </form>
      ) : (
        <button className="btn-primary" type="button" onClick={() => { setShowForm(true); setSubmitError(''); setSuccess('') }}>
          {t(application?.status === 'rejected' ? 'enrollment.reapply' : 'enrollment.request')}
        </button>
      )}
    </>
  }

  return (
    <section className="course-enrollment" aria-label={t('enrollment.sectionLabel')} aria-busy={loading || submitting}>
      {content}
      {success && <p className="enrollment-success" role="status">{t(success)}</p>}
      {submitError && <p className="error" role="alert">{t(submitError)}</p>}
    </section>
  )
}
