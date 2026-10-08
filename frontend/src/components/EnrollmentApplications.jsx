import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../api'
import { enrollmentErrorKey } from '../utils/enrollment'

export default function EnrollmentApplications() {
  const { t, i18n } = useTranslation()
  const [applications, setApplications] = useState(null)
  const [error, setError] = useState('')
  const [reload, setReload] = useState(0)

  useEffect(() => {
    let active = true
    api.get('/my/enrollment-requests/').then(({ data }) => {
      if (active) setApplications(data)
    }).catch((failure) => {
      if (active) setError(enrollmentErrorKey(failure, 'enrollment.applicationsError'))
    })
    return () => { active = false }
  }, [reload])

  function refresh() {
    setApplications(null)
    setError('')
    setReload((value) => value + 1)
  }

  const dateFormat = new Intl.DateTimeFormat(i18n.resolvedLanguage, { dateStyle: 'medium' })

  return (
    <section className="profile-applications" aria-labelledby="profile-applications-title" aria-busy={!applications && !error}>
      <div className="profile-courses-heading">
        <h2 id="profile-applications-title">{t('enrollment.applicationsTitle')}</h2>
        <p>{t('enrollment.applicationsDescription')}</p>
      </div>
      {error ? <div role="alert">
        <p className="error">{t(error)}</p>
        <button className="academic-button" type="button" onClick={refresh}>{t('common.retry')}</button>
      </div> : !applications ? <p className="profile-loading" role="status">{t('common.loading')}</p>
        : applications.length ? <ul className="profile-application-list">
          {applications.map((application) => (
            <li className="profile-application" key={application.id}>
              <div className="profile-application-heading">
                <h3><Link to={`/courses/${encodeURIComponent(application.course.slug)}`}>{application.course.title}</Link></h3>
                <span className="profile-application-status">{t(`enrollment.status.${application.status}`)}</span>
              </div>
              <p className="profile-application-date">{t('enrollment.appliedOn', { date: dateFormat.format(new Date(application.created_at)) })}</p>
              {application.reviewed_at && <p className="profile-application-date">{t('enrollment.reviewedOn', { date: dateFormat.format(new Date(application.reviewed_at)) })}</p>}
              {application.status === 'rejected' && application.admin_note && <p className="profile-application-note">{t('enrollment.decisionReason', { reason: application.admin_note })}</p>}
              <Link className="profile-curriculum-link" to={`/courses/${encodeURIComponent(application.course.slug)}`}>
                {t(application.status === 'rejected' ? 'enrollment.viewAndReapply' : 'enrollment.viewApplication')}
              </Link>
            </li>
          ))}
        </ul> : <p className="profile-loading">{t('enrollment.noApplications')}</p>}
    </section>
  )
}
