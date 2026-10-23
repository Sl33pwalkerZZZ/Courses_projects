import { useEffect, useRef, useState } from 'react'
import { Link, useOutletContext, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import Button from '../../components/ui/Button'
import { Input, Select, Notice, ResourceState } from '../../components/instructor/StudioShared'
import { useStudioAction, useStudioResource } from '../../components/instructor/useStudio'
import { studioList } from '../../utils/instructorStudio'

export default function Submissions() {
  const { course, identity } = useOutletContext(), { t } = useTranslation()
  const [params, setParams] = useSearchParams()
  const target = params.get('submission')
  const [status, setStatus] = useState(target ? 'all' : 'pending')
  const [notice, setNotice] = useState(null)
  const noticeRef = useRef(null)
  useEffect(() => { if (notice) noticeRef.current?.focus() }, [notice])
  const resource = useStudioResource(course ? `/studio/courses/${course.id}/submissions/` : '/studio/submissions/')
  const reviewed = decision => {
    setNotice({ id: decision.id, status: decision.status })
    resource.reload()
  }
  return <><h2>{t('instructorStudio.submissions')}</h2><p>{t('instructorStudio.assignmentReview.intro')}</p><p>{t('instructorStudio.submissionPrivacy')}</p>
    <Select label={t('instructorStudio.assignmentReview.filter')} value={status} onChange={event => { setStatus(event.target.value); if (target) { const next = new URLSearchParams(params); next.delete('submission'); setParams(next) } }} options={['pending', 'approved', 'rejected', 'all'].map(value => ({ value, label: t(value === 'all' ? 'instructorStudio.assignmentReview.all' : `instructorStudio.statuses.${value}`) }))} />
    <p ref={noticeRef} tabIndex={-1} role="status">{notice && <>{t('instructorStudio.assignmentReview.saved')} — {t(`instructorStudio.statuses.${notice.status}`)}</>}</p>
    <ResourceState resource={resource}>{data => {
      const submissions = studioList(data).filter(item => (!target || String(item.id) === target) && (status === 'all' || item.status === status))
      return <>{!submissions.length && <p role="status">{t('instructorStudio.noSubmissions')}</p>}{submissions.map(submission => <SubmissionCard key={`${submission.id}:${submission.revision}`} submission={submission} viewerId={identity?.id} onSaved={reviewed} />)}</>
    }}</ResourceState></>
}
export function ReadAnswer({ value, field }) {
  const { t } = useTranslation()
  const label = key => t(`selectionMap.fields.${key}`, {
    defaultValue: t(`selectionMap.criteria.${key}`, {
      defaultValue: t(`instructorStudio.assignmentReview.answerLabels.${key}`, { defaultValue: key.replaceAll('_', ' ') }),
    }),
  })
  if (Array.isArray(value)) return <ol>{value.map((item, index) => <li key={index}><ReadAnswer value={item} /></li>)}</ol>
  if (value && typeof value === 'object') return <dl>{Object.entries(value).map(([key, item]) => <div key={key}><dt>{label(key)}</dt><dd><ReadAnswer value={item} field={key} /></dd></div>)}</dl>
  if (field === 'data_classification') return <span>{t(`selectionMap.classification.${value}`, { defaultValue: String(value ?? '') })}</span>
  return <span>{String(value ?? '')}</span>
}
export function SubmissionCard({ submission, viewerId, onSaved }) {
  const { t, i18n } = useTranslation(), action = useStudioAction()
  const [note, setNote] = useState(submission.reviewer_comment || '')
  const self = viewerId != null && String(viewerId) === String(submission.student?.id || submission.student)
  const reviewable = submission.status === 'pending' && !self && submission.can_review !== false
  const review = status => {
    if (!reviewable || !window.confirm(t('instructorStudio.reviewConfirm'))) return
    action.run(signal => api.post(`/studio/submissions/${submission.id}/review/`, { revision: submission.revision, status, reviewer_comment: note }, { signal }), onSaved, 'instructorStudio.assignmentReview.saved')
  }
  return <article className="instructor-panel">
    <h3>{submission.student?.username || submission.student_username} — {submission.lesson_title}</h3>
    {submission.course_id && <p><Link to={`/instructor/courses/${submission.course_id}/submissions`}>{submission.course_title}</Link></p>}
    <p className="instructor-badge">{t(`instructorStudio.statuses.${submission.status}`, { defaultValue: submission.status })}</p>
    {submission.submitted_at && <p>{t('instructorStudio.assignmentReview.submitted')}: <time dateTime={submission.submitted_at}>{new Date(submission.submitted_at).toLocaleString(i18n.resolvedLanguage)}</time></p>}
    <details><summary>{t('instructorStudio.assignmentReview.instructions')}</summary><p className="instructor-answer">{submission.assignment_description}</p></details>
    <details><summary>{t('instructorStudio.assignmentReview.open')}</summary><div className="instructor-answer">{submission.content && <p>{submission.content}</p>}{submission.payload && <ReadAnswer value={submission.payload} />}</div>{submission.file_available && <SubmissionAttachment id={submission.id} />}</details>
    {reviewable ? <><Input multiline label={t('instructorStudio.feedback')} value={note} onChange={event => setNote(event.target.value)} /><p>{t('instructorStudio.assignmentReview.evidence')}</p><Notice {...action} /><div className="instructor-actions"><Button disabled={action.busy} onClick={() => review('approved')}>{t('instructorStudio.approve')}</Button><Button variant="secondary" disabled={action.busy || !note.trim()} onClick={() => review('rejected')}>{t('instructorStudio.reject')}</Button></div></> : <>{self && submission.status === 'pending' && <p role="note">{t('instructorStudio.assignmentReview.selfReview')}</p>}{submission.reviewer_comment && <section><h4>{t('instructorStudio.feedback')}</h4><p className="instructor-answer">{submission.reviewer_comment}</p></section>}{submission.reviewed_at && <p>{t('instructorStudio.reviewed')}: <time dateTime={submission.reviewed_at}>{new Date(submission.reviewed_at).toLocaleString(i18n.resolvedLanguage)}</time>{submission.reviewer_username && ` · ${submission.reviewer_username}`}</p>}{submission.status === 'approved' && <p>{t(submission.review_is_verifiable ? 'instructorStudio.assignmentReview.verified' : 'instructorStudio.assignmentReview.legacy')}</p>}</>}
  </article>
}
function SubmissionAttachment({ id }) {
  const { t } = useTranslation(), action = useStudioAction()
  const download = () => action.run(signal => api.get(`/studio/submissions/${id}/file/`, { signal, responseType: 'blob' }), blob => {
    const url = URL.createObjectURL(blob), link = document.createElement('a')
    link.href = url; link.download = `submission-${id}`
    document.body.appendChild(link); link.click(); link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }, '')
  return <div><p>{t('instructorStudio.privateFileNotice')}</p><Button variant="secondary" disabled={action.busy} onClick={download}>{t('instructorStudio.download')}</Button><Notice {...action} /></div>
}
