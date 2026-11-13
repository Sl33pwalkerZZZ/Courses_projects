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
      if (failure.response?.status === 404) setResponse({ requestKey, data: { enabled: false } })
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
  const [preview, setPreview] = useState(null)
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview.url) }, [preview, session.generation])
  const active = useRef(true)
  useEffect(() => { active.current = true; return () => { active.current = false } }, [session.generation])
  async function download(inline = false) {
    const generation = session.generation
    setDownloading(true)
    setError(false)
    try {
      const response = await api.get(`/certificates/${encodeURIComponent(certificate.verification_code)}/download/${inline ? '?preview=1' : ''}`, { responseType: 'blob' })
      if (!active.current || getAuthSession().generation !== generation) return
      if (response.data.type && response.data.type.split(';')[0] !== 'application/pdf') throw new Error('Unexpected PDF response')
      const url = URL.createObjectURL(response.data)
      if (inline) {
        setPreview({ url, generation })
        return
      }
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
      {certificate.verification_available === true ? <Link to={`/certificates/verify/${encodeURIComponent(certificate.verification_code)}`}>{t('certificates.verify')}</Link> : <p>{t('certificates.verificationUnavailable')}</p>}
      {session.authenticated && !certificate.revoked && <>
        <button type="button" className="academic-button" onClick={() => download(true)} disabled={downloading}>{t('certificates.preview')}</button>
        <button type="button" className="academic-button" onClick={() => download()} disabled={downloading}>{t(downloading ? 'common.loading' : 'certificates.download')}</button>
      </>}
    </div>
    {error && <p role="alert">{t('certificates.downloadError')}</p>}
    {session.authenticated && preview?.generation === session.generation && <div className="certificate-preview">
      <button type="button" className="academic-button" onClick={() => setPreview(null)}>{t('certificates.closePreview')}</button>
      <iframe src={preview.url} title={t('certificates.preview')} referrerPolicy="no-referrer" />
    </div>}
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

export function CertificateNamePanel({ record, draft, onDraftChange, onSave, onConfirm, confirmation, onConfirmationChange, busy, error }) {
  const { t } = useTranslation()
  const changed = draft !== record.learner_name
  return <section id="certificate-name-title" className="certificate-section certificate-name-section" aria-labelledby="certificate-name-heading">
    <h2 id="certificate-name-heading">{t('certificates.nameTitle')}</h2>
    <p>{t('certificates.nameDescription')}</p>
    {record.confirmed && !changed && <p className="certificate-name-status" role="status">{t('certificates.nameConfirmed')}</p>}
    {!record.confirmed && record.learner_name && !changed && <p className="certificate-name-status" role="status">{t('certificates.nameNotConfirmed')}</p>}
    <form className="certificate-name-form" onSubmit={onSave}>
      <label htmlFor="certificate-display-name">{t('certificates.nameLabel')}</label>
      <input id="certificate-display-name" name="learner_name" type="text" autoComplete="name" maxLength={200}
        value={draft} onChange={onDraftChange} aria-describedby="certificate-name-help" />
      <p id="certificate-name-help">{t('certificates.nameReviewDescription')}</p>
      <button className="academic-button" type="submit" disabled={busy || !draft.trim() || !changed}>
        {t(busy ? 'common.loading' : 'certificates.nameSave')}
      </button>
    </form>
    {!record.confirmed && record.learner_name && !changed && <div className="certificate-name-confirmation">
      <p><strong>{t('certificates.nameReviewTitle')}</strong></p>
      <p className="certificate-name-preview">{record.learner_name}</p>
      <label className="certificate-name-confirm-label">
        <input type="checkbox" checked={confirmation} onChange={onConfirmationChange} disabled={busy} />
        <span>{t('certificates.nameConfirm')}</span>
      </label>
      <button className="academic-button" type="button" onClick={onConfirm} disabled={busy || !confirmation}>
        {t(busy ? 'common.loading' : 'certificates.nameConfirmButton')}
      </button>
    </div>}
    {error && <p role="alert">{t(error)}</p>}
  </section>
}

export function CertificateNameConfirmation() {
  const { t } = useTranslation()
  const session = useAuthSession()
  const [record, setRecord] = useState(null)
  const [draft, setDraft] = useState('')
  const [confirmation, setConfirmation] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    Promise.resolve().then(() => {
      if (!active) return
      setRecord(null)
      setDraft('')
      setConfirmation(false)
      setBusy(false)
      setError('')
    })
    if (session.authenticated) api.get('/my/certificate-name/').then(({ data }) => {
      if (active && getAuthSession().generation === session.generation) {
        setRecord(data)
        setDraft(data.learner_name || '')
      }
    }).catch(() => {
      if (active && getAuthSession().generation === session.generation) setError('certificates.nameLoadError')
    })
    return () => { active = false }
  }, [session.authenticated, session.generation])

  async function saveName(event) {
    event.preventDefault()
    const generation = session.generation
    setBusy(true)
    setError('')
    try {
      const { data } = await api.put('/my/certificate-name/', { learner_name: draft })
      if (getAuthSession().generation !== generation) return
      setRecord(data)
      setDraft(data.learner_name || '')
      setConfirmation(false)
    } catch {
      if (getAuthSession().generation === generation) setError('certificates.nameSaveError')
    } finally {
      if (getAuthSession().generation === generation) setBusy(false)
    }
  }

  async function confirmName() {
    if (!record?.learner_name || !confirmation) return
    const generation = session.generation
    setBusy(true)
    setError('')
    try {
      const { data } = await api.post('/my/certificate-name/', { learner_name: record.learner_name, confirmation: true })
      if (getAuthSession().generation !== generation) return
      setRecord(data)
      setDraft(data.learner_name || '')
      setConfirmation(false)
    } catch {
      if (getAuthSession().generation === generation) setError('certificates.nameConfirmError')
    } finally {
      if (getAuthSession().generation === generation) setBusy(false)
    }
  }

  if (!session.authenticated) return null
  if (error === 'certificates.nameLoadError' && !record) return <section id="certificate-name-title" className="certificate-section certificate-name-section" aria-labelledby="certificate-name-heading">
    <h2 id="certificate-name-heading">{t('certificates.nameTitle')}</h2><p role="alert">{t(error)}</p>
  </section>
  if (!record) return <section id="certificate-name-title" className="certificate-section certificate-name-section" aria-labelledby="certificate-name-heading">
    <h2 id="certificate-name-heading">{t('certificates.nameTitle')}</h2><p role="status">{t('common.loading')}</p>
  </section>

  return <CertificateNamePanel record={record} draft={draft} onDraftChange={event => setDraft(event.target.value)}
    onSave={saveName} onConfirm={confirmName} confirmation={confirmation}
    onConfirmationChange={event => setConfirmation(event.target.checked)} busy={busy} error={error} />
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

export function CertificateListContent({ result, error, refresh }) {
  const { t } = useTranslation()
  const items = Array.isArray(result) ? result : result?.results
  return <CertificateReadState error={error} refresh={refresh}>{result?.enabled === false
    ? <p role="status">{t('certificates.listUnavailable')}</p>
    : items ? items.length ? <div className="certificate-grid">{items.map(item => <CertificateCard key={item.verification_code} certificate={item} />)}</div> : <p>{t('certificates.empty')}</p> : <p role="status">{t('common.loading')}</p>}</CertificateReadState>
}

export default function MyCertificates() {
  const { t } = useTranslation()
  const state = useCertificateRead('/my/certificates/')
  return <section className="certificate-section" aria-labelledby="my-certificates-title">
    <h2 id="my-certificates-title">{t('certificates.myTitle')}</h2>
    <p>{t('certificates.completionDifference')}</p>
    <CertificateListContent {...state} />
  </section>
}
