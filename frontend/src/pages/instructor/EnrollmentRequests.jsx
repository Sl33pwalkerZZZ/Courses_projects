import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useOutletContext } from 'react-router-dom'
import api from '../../api'
import Button from '../../components/ui/Button'
import { Input, Notice, ResourceState, Select } from '../../components/instructor/StudioShared'
import { useStudioAction, useStudioResource } from '../../components/instructor/useStudio'
import { studioList } from '../../utils/instructorStudio'

const key = 'instructorStudio.enrollmentRequests.'
export default function EnrollmentRequests() {
  const { t } = useTranslation()
  const { identity } = useOutletContext()
  const [status, setStatus] = useState('pending')
  const [decisionResult, setDecisionResult] = useState(null)
  const action = useStudioAction()
  const resource = useStudioResource(identity.is_moderator ? `/studio/enrollment-requests/?status=${status}` : null)
  if (!identity.is_moderator) return <p role="alert">{t('instructorStudio.forbidden')}</p>
  let message = ''
  if (decisionResult) {
    message = decisionResult.changed
      ? t(`${key}${decisionResult.status === 'approved' ? 'approveSuccess' : 'rejectSuccess'}`)
      : t(`${key}alreadyReviewed`, { status: t(`${key}${decisionResult.status}`) })
  }
  const decide = (request, decision, note) => {
    if (!window.confirm(t(`${key}${decision}Confirm`, { username: request.student.username, course: request.course.title }))) return
    setDecisionResult(null)
    action.run(signal => api.post(`/studio/enrollment-requests/${request.id}/decision/`, { decision, note }, { signal }), result => {
      setDecisionResult(result)
      resource.reload()
    }, '')
  }
  return <>
    <h2>{t(`${key}title`)}</h2><p>{t(`${key}intro`)}</p>
    <Select label={t(`${key}filter`)} value={status} onChange={event => setStatus(event.target.value)} options={['pending', 'approved', 'rejected', 'all'].map(value => ({ value, label: t(`${key}${value}`) }))} />
    <Notice {...action} message={message} />
    <ResourceState resource={resource}>{data => <>{!studioList(data).length && <p role="status">{t(`${key}empty`)}</p>}{studioList(data).map(request => <EnrollmentRequestCard request={request} key={request.id} busy={action.busy} onDecision={decide} />)}</>}</ResourceState>
  </>
}

export function EnrollmentRequestCard({ request, busy = false, onDecision }) {
  const { t, i18n } = useTranslation()
  const [note, setNote] = useState(request.admin_note || '')
  const date = value => new Date(value).toLocaleString(i18n.resolvedLanguage || i18n.language)
  return <article className="instructor-panel" aria-labelledby={`enrollment-request-${request.id}`}>
    <h3 id={`enrollment-request-${request.id}`}>{request.course.title}</h3>
    <p><strong>{t(`${key}student`)}:</strong> {request.student.username}</p>
    <p><strong>{t(`${key}submitted`)}:</strong> <time dateTime={request.created_at}>{date(request.created_at)}</time></p>
    <p><strong>{t(`${key}status`)}:</strong> {t(`${key}${request.status}`)}</p>
    {request.message && <p>{request.message}</p>}
    {request.status === 'pending' ? <>
      <Input multiline label={t(`${key}note`)} value={note} maxLength={5000} disabled={busy} onChange={event => setNote(event.target.value)} />
      <div className="instructor-actions"><Button disabled={busy} onClick={() => onDecision(request, 'approve', note)}>{t(`${key}approve`)}</Button><Button variant="secondary" disabled={busy} onClick={() => onDecision(request, 'reject', note)}>{t(`${key}reject`)}</Button></div>
    </> : <>{request.admin_note && <p>{t(`${key}reviewNote`)}: {request.admin_note}</p>}{request.reviewed_at && <p>{t('instructorStudio.reviewed')}: <time dateTime={request.reviewed_at}>{date(request.reviewed_at)}</time></p>}</>}
  </article>
}
