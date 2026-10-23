import { useState } from 'react'
import { Link, useOutletContext } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import { refreshInstructorPermissions } from '../../hooks/useInstructor'
import Button from '../../components/ui/Button'
import { Input, Notice, ResourceState } from '../../components/instructor/StudioShared'
import { useStudioAction, useStudioResource } from '../../components/instructor/useStudio'
import { studioList } from '../../utils/instructorStudio'

export default function Publication() {
  const { course } = useOutletContext()
  const resource = useStudioResource(`/studio/courses/${course.id}/publication/`)
  return <ResourceState resource={resource}>{data => <PublicationForm course={course} data={data} onSaved={resource.reload} />}</ResourceState>
}
function PublicationForm({ course, data, onSaved }) {
  const { t } = useTranslation(), action = useStudioAction()
  const [source, setSource] = useState(false), [assessment, setAssessment] = useState(false)
  const destinations = { title: 'edit', description: 'edit', curriculum: 'curriculum', lesson_content: 'curriculum', assessment: 'assessment', source_reviewed: 'curriculum', assessment_reviewed: 'assessment' }
  return <section className="instructor-panel"><h3>{t('instructorStudio.publication')}</h3><p>{t('instructorStudio.publicationHint')}</p><ul className="instructor-requirements">{(data.requirements || []).map(requirement => { const met = requirement.met || (requirement.key === 'source_reviewed' && source) || (requirement.key === 'assessment_reviewed' && assessment); return <li key={requirement.key}><span aria-hidden="true">{met ? '✓' : '○'}</span> <Link to={`/instructor/courses/${course.id}/${destinations[requirement.key] || 'edit'}`}>{t(`instructorStudio.requirements.${requirement.key}`, { defaultValue: requirement.label })}</Link> — {t(`instructorStudio.${met ? 'complete' : 'incomplete'}`)}</li> })}</ul><form className="instructor-form" onSubmit={event => { event.preventDefault(); if (window.confirm(t('instructorStudio.requestConfirm'))) action.run(signal => api.post(`/studio/courses/${course.id}/publication/`, { source_reviewed: source, assessment_reviewed: assessment }, { signal }), onSaved) }}><label className="instructor-check"><input type="checkbox" checked={source} onChange={event => setSource(event.target.checked)} />{t('instructorStudio.sourceReviewed')}</label><label className="instructor-check"><input type="checkbox" checked={assessment} onChange={event => setAssessment(event.target.checked)} />{t('instructorStudio.assessmentReviewed')}</label><Notice {...action} /><Button type="submit" disabled={action.busy || data.is_published || data.requests?.some(request => request.status === 'pending')}>{t('instructorStudio.requestPublication')}</Button></form><h4>{t('instructorStudio.history')}</h4>{!data.requests?.length && <p>{t('instructorStudio.noRequests')}</p>}{data.requests?.map(request => <article className="instructor-history" key={request.id}><strong>{t(`instructorStudio.statuses.${request.status}`, { defaultValue: request.status })}</strong><p><time dateTime={request.created_at}>{new Date(request.created_at).toLocaleString()}</time></p>{request.note && <p>{request.note}</p>}{request.reviewed_at && <p>{t('instructorStudio.reviewed')}: <time dateTime={request.reviewed_at}>{new Date(request.reviewed_at).toLocaleString()}</time></p>}</article>)}</section>
}
export function PublicationReviews() {
  const { identity } = useOutletContext(), { t } = useTranslation()
  const resource = useStudioResource(identity.is_moderator ? '/studio/reviews/' : null)
  if (!identity.is_moderator) return <p role="alert">{t('instructorStudio.forbidden')}</p>
  return <><h2>{t('instructorStudio.reviews')}</h2><ResourceState resource={resource}>{data => <>{!studioList(data).length && <p>{t('instructorStudio.noReviews')}</p>}{studioList(data).map(request => <ReviewCard request={request} key={request.id} onSaved={resource.reload} />)}</>}</ResourceState></>
}
function ReviewCard({ request, onSaved }) {
  const { t } = useTranslation(), action = useStudioAction(), [note, setNote] = useState('')
  const [checked, setChecked] = useState(false)
  const id = request.course?.id || request.course_id || request.course
  const decide = decision => {
    if (!window.confirm(t(decision === 'approve' ? 'instructorStudio.approveConfirm' : 'instructorStudio.rejectConfirm'))) return
    action.run(signal => api.post(`/studio/reviews/${request.id}/decision/`, { decision, note }, { signal }), onSaved)
  }
  return <article className="instructor-panel"><h3>{request.course?.title || request.course_title || `#${id}`}</h3><p>{t(`instructorStudio.statuses.${request.status}`, { defaultValue: request.status })}</p><div className="instructor-actions"><Button to={`/instructor/courses/${id}/publication`} variant="secondary">{t('instructorStudio.inspectRequirements')}</Button><Link to={`/instructor/courses/${id}/assessment`}>{t('instructorStudio.reviewAssessment')}</Link></div>{request.status === 'pending' && <><Input multiline label={t('instructorStudio.reviewNote')} value={note} onChange={event => setNote(event.target.value)} /><label className="instructor-check"><input type="checkbox" checked={checked} onChange={event => setChecked(event.target.checked)} />{t('instructorStudio.adminReviewed')}</label><Notice {...action} /><div className="instructor-actions"><Button disabled={action.busy || !checked} onClick={() => decide('approve')}>{t('instructorStudio.approvePublish')}</Button><Button variant="secondary" disabled={action.busy || !note.trim()} onClick={() => decide('reject')}>{t('instructorStudio.reject')}</Button></div></>}</article>
}
export { default as Submissions } from './Submissions'
export function InstructorManagement() {
  const { identity } = useOutletContext(), { t } = useTranslation()
  const resource = useStudioResource(identity.can_manage_instructors ? '/studio/instructors/' : null)
  if (!identity.can_manage_instructors) return <p role="alert">{t('instructorStudio.forbidden')}</p>
  return <><h2>{t('instructorStudio.instructors')}</h2><p>{t('instructorStudio.instructorsHint')}</p><ResourceState resource={resource}>{data => <div className="instructor-courses">{studioList(data).map(person => <InstructorCard key={person.id} person={person} onSaved={resource.reload} />)}</div>}</ResourceState></>
}
function InstructorCard({ person, onSaved }) {
  const { t } = useTranslation(), action = useStudioAction()
  const protectedAccount = person.is_staff || person.is_superuser || person.role === 'admin'
  return <article className="instructor-panel"><h3>{person.username}</h3><p>{t(`instructorStudio.roles.${person.role}`, { defaultValue: person.role })}</p><Notice {...action} />{!protectedAccount && <Button variant="secondary" disabled={action.busy} onClick={() => { if (window.confirm(t('instructorStudio.roleConfirm', { username: person.username }))) action.run(signal => api.post(`/studio/instructors/${person.id}/`, { role: person.role === 'author' ? 'student' : 'author' }, { signal }), () => { onSaved(); refreshInstructorPermissions() }) }}>{t(person.role === 'author' ? 'instructorStudio.revokeAuthor' : 'instructorStudio.grantAuthor')}</Button>}</article>
}
