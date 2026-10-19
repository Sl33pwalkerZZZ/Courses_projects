import { Link, NavLink, Outlet, useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import Button from '../../components/ui/Button'
import { Input, Select, Notice, ResourceState, useStudioAction, useStudioResource } from '../../components/instructor/StudioShared'
import { studioList } from '../../utils/instructorStudio'

export function Dashboard() {
  const { t } = useTranslation()
  const resource = useStudioResource('/studio/dashboard/')
  return <><h2>{t('instructorStudio.dashboard')}</h2><ResourceState resource={resource}>{data => <div className="instructor-stats">{Object.entries(data?.counts || data || {}).filter(([, value]) => typeof value === 'number').map(([key, value]) => <div className="instructor-panel" key={key}><strong>{value}</strong><span>{t(`instructorStudio.metrics.${key}`, { defaultValue: key.replaceAll('_', ' ') })}</span></div>)}</div>}</ResourceState><div className="instructor-actions"><Button to="/instructor/courses/new">{t('instructorStudio.newCourse')}</Button><Button to="/instructor/courses" variant="secondary">{t('instructorStudio.courses')}</Button></div></>
}
export function CourseList() {
  const { t } = useTranslation()
  const resource = useStudioResource('/studio/courses/')
  return <><div className="instructor-section-heading"><h2>{t('instructorStudio.courses')}</h2><Button to="/instructor/courses/new">{t('instructorStudio.newCourse')}</Button></div><ResourceState resource={resource}>{data => <div className="instructor-courses">{!studioList(data).length && <p>{t('instructorStudio.noCourses')}</p>}{studioList(data).map(course => <article className="instructor-panel" key={course.id}><span className="instructor-badge">{t(`instructorStudio.${course.is_published ? 'published' : 'draft'}`)}</span><h3><Link to={`/instructor/courses/${course.id}/edit`}>{course.title}</Link></h3><p>{course.description}</p><Button to={`/instructor/courses/${course.id}/edit`} variant="secondary">{t('instructorStudio.edit')}</Button></article>)}</div>}</ResourceState></>
}
export function CourseWorkspace() {
  const { id } = useParams()
  const { identity } = useOutletContext()
  const { t } = useTranslation()
  const resource = useStudioResource(`/studio/courses/${id}/`)
  return <ResourceState resource={resource}>{course => <><div className="instructor-section-heading"><div><span className="instructor-badge">{t(`instructorStudio.${course.is_published ? 'published' : 'draft'}`)}</span><h2>{course.title}</h2></div><Button to={`/instructor/courses/${course.slug}/preview`} variant="secondary">{t('instructorStudio.preview')}</Button></div><nav className="instructor-tabs" aria-label={t('instructorStudio.courseNavigation')}>{['edit', 'curriculum', 'assessment', 'submissions', 'publication'].map(tab => <NavLink key={tab} to={`/instructor/courses/${id}/${tab}`}>{t(`instructorStudio.${tab}`)}</NavLink>)}</nav><Outlet context={{ course, reload: resource.reload, identity }} /></>}</ResourceState>
}
export function CourseForm({ initial, onSaved, onPrepared }) {
  const { t } = useTranslation()
  const metadata = useStudioResource('/studio/meta/')
  const [form, setForm] = useState(() => ({ title: initial?.title || '', description: initial?.description || '', direction: initial?.direction?.id || '', level: initial?.level || 'beginner', enrollment_mode: initial?.enrollment_mode || 'approval', language: initial?.language || initial?.content_language || 'ru' }))
  const action = useStudioAction()
  const change = key => event => setForm(value => ({ ...value, [key]: event.target.value }))
  const options = (list, prefix) => (list || []).map(item => typeof item === 'string' ? { value: item, label: t(`instructorStudio.${prefix}.${item}`, { defaultValue: item }) } : Array.isArray(item) ? { value: item[0], label: t(`instructorStudio.${prefix}.${item[0]}`, { defaultValue: item[1] }) } : { value: item.value || item.id, label: prefix === 'directions' ? item.name : t(`instructorStudio.${prefix}.${item.value}`, { defaultValue: item.label || item.name }) })
  return <ResourceState resource={metadata}>{meta => <form className="instructor-form instructor-panel" onSubmit={event => { event.preventDefault(); if (onPrepared) { onPrepared(form); return } action.run(signal => initial?.id ? api.patch(`/studio/courses/${initial.id}/`, form, { signal }) : api.post('/studio/courses/', form, { signal }), onSaved) }}><p>{t('instructorStudio.draftNotice')}</p><Input label={t('instructorStudio.courseTitle')} value={form.title} onChange={change('title')} maxLength={255} required /><Input multiline label={t('instructorStudio.description')} value={form.description} onChange={change('description')} required /><div className="instructor-grid"><Select label={t('instructorStudio.direction')} value={form.direction} onChange={change('direction')} required options={[{ value: '', label: t('instructorStudio.choose') }, ...options(meta.directions, 'directions')]} /><Select label={t('instructorStudio.level')} value={form.level} onChange={change('level')} options={options(meta.levels || ['beginner', 'intermediate', 'advanced'], 'levels')} /><Select label={t('instructorStudio.enrollment')} value={form.enrollment_mode} onChange={change('enrollment_mode')} options={options(meta.enrollment_modes || ['approval', 'open'], 'enrollments')} /><Select label={t('instructorStudio.language')} value={form.language} onChange={change('language')} options={options(meta.languages || ['ru', 'kk', 'en'], 'languages')} /></div><Notice {...action} /><Button type="submit" disabled={action.busy}>{t(action.busy ? 'instructorStudio.saving' : onPrepared ? 'instructorStudio.continueReview' : 'instructorStudio.save')}</Button></form>}</ResourceState>
}
export function NewCourse() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  return <><h2>{t('instructorStudio.newCourse')}</h2><CourseForm onSaved={course => navigate(`/instructor/courses/${course.id}/curriculum`)} /></>
}
export function CourseSettings() {
  const { course, reload } = useOutletContext()
  return <CourseForm key={course.id} initial={course} onSaved={reload} />
}
