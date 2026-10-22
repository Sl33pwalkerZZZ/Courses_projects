import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../api'
import '../components/certificates/certificates.css'

export function VerificationDetails({ certificate }) {
  const { t, i18n } = useTranslation()
  const valid = certificate.status === 'valid'
  return <>
    <p role="status"><strong>{t(valid ? 'certificates.valid' : 'certificates.revoked')}</strong></p>
    <dl>
      <div><dt>{t('certificates.learner')}</dt><dd>{certificate.learner_initials}</dd></div>
      <div><dt>{t('certificates.course')}</dt><dd>{certificate.course_title}</dd></div>
      <div><dt>{t('certificates.issuer')}</dt><dd>{certificate.issuer_name}</dd></div>
      <div><dt>{t('certificates.date')}</dt><dd>{new Intl.DateTimeFormat(i18n.resolvedLanguage, { dateStyle: 'long' }).format(new Date(certificate.issued_at))}</dd></div>
    </dl>
    <p>{t('certificates.privacy')}</p>
  </>
}

export default function CertificateVerification() {
  const { verificationId } = useParams()
  const { t } = useTranslation()
  const [response, setResponse] = useState(null)
  const [retry, setRetry] = useState(0)
  const requestKey = `${verificationId}:${retry}`
  const current = response?.requestKey === requestKey ? response : null
  const certificate = current?.data
  const error = current?.error
  useEffect(() => {
    let active = true
    api.get(`/certificates/verify/${encodeURIComponent(verificationId)}/`).then(({ data }) => {
      if (active) setResponse({ requestKey, data })
    }).catch(failure => { if (active) setResponse({ requestKey, error: failure.response?.status === 404 ? 'certificates.unknown' : 'certificates.loadError' }) })
    return () => { active = false }
  }, [verificationId, requestKey])
  return <section className="certificate-verification" aria-labelledby="verification-title">
    <h1 id="verification-title">{t('certificates.verificationTitle')}</h1>
    {error ? <div role="alert"><p>{t(error)}</p><button type="button" className="academic-button" onClick={() => setRetry(value => value + 1)}>{t('common.retry')}</button></div>
      : certificate ? <VerificationDetails certificate={certificate} /> : <p role="status">{t('common.loading')}</p>}
  </section>
}
