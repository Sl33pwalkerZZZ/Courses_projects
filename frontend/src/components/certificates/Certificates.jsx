import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api, { getAuthSession } from '../../api'
import { useAuthSession } from '../../hooks/useAuth'
import './certificates.css'

function useCertificateRead(path) {
  const session = useAuthSession()
  const [response, setResponse] = useState(null)
  const [retry, setRetry] = useState(0)
  const requestKey = `${session.generation}:${path}:${retry}`
  useEffect(() => {
    let active = true
    if (session.authenticated) api.get(path).then(({ data }) => {
      if (active) setResponse({ requestKey, data })
    }).catch(failure => { if (active) {
      if (failure.response?.status === 404) setResponse({ requestKey, data: path === '/my/certificates/' ? [] : { enabled: false } })
      else setResponse({ requestKey, error: true })
    } })
    return () => { active = false }
  }, [path, requestKey, session.authenticated])
  const current = response?.requestKey === requestKey && session.authenticated ? response : null
  return { result: current?.data ?? null, error: current?.error || false, refresh: () => setRetry(value => value + 1) }
}

export function CertificateCard({ certificate }) {
  const { t, i18n } = useTranslation()
  const session = useAuthSession()
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState(false)
  const active = useRef(true)
  useEffect(() => { active.current = true; return () => { active.current = false } }, [session.generation])
  async function download() {
    const generation = session.generation
    setDownloading(true)
    setError(false)
    try {
      const response = await api.get(`/certificates/${encodeURIComponent(certificate.verification_code)}/download/`, { responseType: 'blob' })
      if (!active.current || getAuthSession().generation !== generation) return
      const url = URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.download = `certificate-${certificate.verification_code}.pdf`
      link.click()
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch { if (active.current && getAuthSession().generation === generation) setError(true) }
    finally { if (active.current && getAuthSession().generation === generation) setDownloading(false) }
  }
  return <article className="certificate-card">
    <h3>{certificate.course_title}</h3>
    <p>{t(certificate.revoked ? 'certificates.status.revoked' : 'certificates.status.issued')}</p>
    <p>{t('certificates.issuedOn', { date: new Intl.DateTimeFormat(i18n.resolvedLanguage, { dateStyle: 'medium' }).format(new Date(certificate.issued_at)) })}</p>
    <div className="certificate-actions">
      <Link to={`/certificates/verify/${encodeURIComponent(certificate.verification_code)}`}>{t('certificates.verify')}</Link>
      {session.authenticated && !certificate.revoked && <button type="button" className="academic-button" onClick={download} disabled={downloading}>{t(downloading ? 'common.loading' : 'certificates.download')}</button>}
    </div>
    {error && <p role="alert">{t('certificates.downloadError')}</p>}
  </article>
}

export function CertificateStatusContent({ result }) {
  const { t } = useTranslation()
  if (!result?.enabled) return <p>{t('certificates.disabled')}</p>
  return <>
    <p>{t(result.eligible ? 'certificates.eligible' : 'certificates.notEligible')}</p>
    <ul className="certificate-requirements">{(result.requirements || []).map((requirement, index) => <li key={`${requirement.key}-${index}`}>
      <span>{t(`certificates.requirements.${requirement.key}`)}</span>{' — '}
      <strong>{t(requirement.met ? 'certificates.met' : 'certificates.notMet')}</strong>
    </li>)}</ul>
    {result.certificate ? <CertificateCard certificate={result.certificate} /> : <p>{t('certificates.adminIssue')}</p>}
  </>
}

function CertificateReadState({ error, refresh, children }) {
  const { t } = useTranslation()
  return error ? <div role="alert"><p>{t('certificates.loadError')}</p><button type="button" className="academic-button" onClick={refresh}>{t('common.retry')}</button></div> : children
}

export function CourseCertificateStatus({ courseId }) {
  const { t } = useTranslation()
  const state = useCertificateRead(`/courses/${courseId}/certificate-status/`)
  return <section className="certificate-section" aria-labelledby="course-certificate-title">
    <h2 id="course-certificate-title">{t('certificates.courseTitle')}</h2>
    <p>{t('certificates.completionDifference')}</p>
    <CertificateReadState {...state}>{state.result ? <CertificateStatusContent result={state.result} /> : <p role="status">{t('common.loading')}</p>}</CertificateReadState>
  </section>
}

export default function MyCertificates() {
  const { t } = useTranslation()
  const state = useCertificateRead('/my/certificates/')
  const items = Array.isArray(state.result) ? state.result : state.result?.results
  return <section className="certificate-section" aria-labelledby="my-certificates-title">
    <h2 id="my-certificates-title">{t('certificates.myTitle')}</h2>
    <p>{t('certificates.completionDifference')}</p>
    <CertificateReadState {...state}>{items ? items.length ? <div className="certificate-grid">{items.map(item => <CertificateCard key={item.verification_code} certificate={item} />)}</div> : <p>{t('certificates.empty')}</p> : <p role="status">{t('common.loading')}</p>}</CertificateReadState>
  </section>
}
