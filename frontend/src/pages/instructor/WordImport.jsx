import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import Button from '../../components/ui/Button'
import { CourseForm } from './CourseEditor'
import { Input, Notice } from '../../components/instructor/StudioShared'
import { useStudioAction } from '../../components/instructor/useStudio'

export default function WordImport() {
  const { t } = useTranslation(), navigate = useNavigate(), action = useStudioAction()
  const [file, setFile] = useState(null), [preview, setPreview] = useState(null), [lessons, setLessons] = useState([])
  const [confirmed, setConfirmed] = useState(false), [stage, setStage] = useState('upload')
  const [metadata, setMetadata] = useState(null)
  const upload = event => {
    event.preventDefault()
    if (!file) return
    const body = new FormData(); body.append('file', file)
    action.run(signal => api.post('/studio/imports/preview/', body, { signal }), data => {
      setPreview(data); setLessons(data.parsed.lessons.map(item => ({ title: item.title, text_content: item.text_content }))); setStage('mapping')
    }, '')
  }
  function confirm() {
    if (!confirmed || !metadata || !window.confirm(t('instructorStudio.importConfirm'))) return
    action.run(signal => api.post(`/studio/imports/${preview.id}/confirm/`, { ...metadata, lessons, preview_token: preview.preview_token }, { signal }), data => navigate(`/instructor/courses/${data.id || data.course?.id}/curriculum`))
  }
  return <><h2>{t('instructorStudio.import')}</h2><p>{t('instructorStudio.importHint')}</p><ol className="instructor-steps">{['uploadStep', 'mappingStep', 'confirmStep'].map((key, index) => <li key={key} aria-current={['upload', 'mapping', 'confirm'][index] === stage ? 'step' : undefined}>{t(`instructorStudio.${key}`)}</li>)}</ol>{stage === 'upload' && <form className="instructor-panel instructor-form" onSubmit={upload}><Input type="file" accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document" label={t('instructorStudio.wordFile')} required onChange={event => setFile(event.target.files[0] || null)} /><p>{t('instructorStudio.previewOnly')}</p><Notice {...action} /><Button type="submit" disabled={action.busy}>{t(action.busy ? 'instructorStudio.parsing' : 'instructorStudio.parse')}</Button></form>}{preview && <><section className="instructor-panel"><h3>{preview.parsed.source_name}</h3><p>{t('instructorStudio.importProvenance')}</p><ul>{[...(preview.warnings || []), ...(preview.parsed.warnings || [])].filter((value, index, array) => array.indexOf(value) === index).map((warning, index) => <li key={index}>{warning}</li>)}</ul><details><summary>{t('instructorStudio.sourcePreview')}</summary><div className="instructor-source">{preview.parsed.blocks?.map((block, index) => block.type === 'table' ? <div key={index} className="instructor-table-scroll" tabIndex={0} role="region" aria-label={t('instructorStudio.sourceTable')}><table><tbody>{block.rows?.map((row, rowIndex) => <tr key={rowIndex}>{row.map((cell, cellIndex) => <td key={cellIndex}>{typeof cell === 'string' ? cell : JSON.stringify(cell)}</td>)}</tr>)}</tbody></table></div> : <p key={index}>{block.text}</p>)}</div></details></section>{stage === 'mapping' && <><p>{t('instructorStudio.mappingHint')}</p>{lessons.map((lesson, index) => <section className="instructor-panel" key={index}><h3>{t('instructorStudio.lesson')} {index + 1}</h3><Input label={t('instructorStudio.lessonTitle')} value={lesson.title} required onChange={event => setLessons(items => items.map((item, i) => i === index ? { ...item, title: event.target.value } : item))} /><Input multiline rows={10} label={t('instructorStudio.lessonBody')} value={lesson.text_content} onChange={event => setLessons(items => items.map((item, i) => i === index ? { ...item, text_content: event.target.value } : item))} /></section>)}<ImportMetadata initial={metadata || { title: preview.parsed.title }} onContinue={data => { setMetadata(data); setStage('confirm') }} /></>}{stage === 'confirm' && <section className="instructor-panel"><h3>{metadata.title}</h3><p>{metadata.description}</p><ol>{lessons.map((lesson, index) => <li key={index}>{lesson.title}</li>)}</ol><p>{t('instructorStudio.finalDraftNotice')}</p><label className="instructor-check"><input type="checkbox" checked={confirmed} onChange={event => setConfirmed(event.target.checked)} />{t('instructorStudio.confirmMapping')}</label><Notice {...action} /><div className="instructor-actions"><Button variant="secondary" disabled={action.busy} onClick={() => { setStage('mapping'); setConfirmed(false) }}>{t('instructorStudio.backMapping')}</Button><Button disabled={!confirmed || action.busy} onClick={confirm}>{t('instructorStudio.createImportedDraft')}</Button></div></section>}</>}</>
}
function ImportMetadata({ initial, onContinue }) {
  // The shared form below is used in a non-writing mode for import metadata.
  return <CourseForm initial={initial} onPrepared={onContinue} />
}
