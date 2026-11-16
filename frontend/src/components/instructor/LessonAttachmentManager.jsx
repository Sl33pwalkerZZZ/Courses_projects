import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import Button from '../ui/Button'
import { Input, Notice, Select } from './StudioShared'
import { useStudioAction } from './useStudio'
import { attachmentPlacement, placementPayload } from '../../utils/studioAttachmentPlacement'

export default function LessonAttachmentManager({ lesson, locked, onSaved, movesBlocked = false, onMoved, onMoving = () => {} }) {
  const { t } = useTranslation(), action = useStudioAction(), moveAction = useStudioAction()
  const [file, setFile] = useState(null)
  const [fields, setFields] = useState({ label: '', caption: '', transcript: '', provenance: '', after_section: '' })
  const update = (key, value) => setFields(current => ({ ...current, [key]: value }))
  const move = (asset, target) => {
    if (locked || movesBlocked || moveAction.busy) return
    onMoving(true)
    moveAction.run(signal => api.patch(`/studio/lessons/${lesson.id}/attachments/${asset.id}/placement/`, placementPayload(lesson, asset, target), { signal }), data => onMoved?.(data))
      .finally(() => onMoving(false))
  }
  return <section className="instructor-attachment-manager"><h4>{t('learning.attachments')}</h4>
    {movesBlocked && <p role="status">{t('instructorStudio.placement.renamePending')}</p>}
    <ul>{(lesson.attachments || []).map(asset => <AttachmentPlacement key={asset.id} lesson={lesson} asset={asset} disabled={locked || movesBlocked || moveAction.busy} onMove={target => move(asset, target)} />)}</ul>
    <Notice {...moveAction} />
    <form className="instructor-form" onSubmit={event => {
      event.preventDefault()
      if (!file) return
      const body = new FormData()
      body.append('file', file)
      Object.entries(fields).forEach(([key, value]) => body.append(key, value))
      action.run(signal => api.post(`/studio/lessons/${lesson.id}/attachments/`, body, { signal }), onSaved)
    }}><fieldset disabled={locked || action.busy}><legend>{t('learning.addAttachment')}</legend>
      <Input type="file" label={t('learning.attachmentFile')} accept=".mp3,.wav,.srt,.mp4,.vtt" required onChange={event => setFile(event.target.files[0] || null)} />
      <Input label={t('learning.attachmentLabel')} value={fields.label} required maxLength={255} onChange={e => update('label', e.target.value)} />
      <Input multiline label={t('learning.attachmentCaption')} value={fields.caption} maxLength={2000} onChange={e => update('caption', e.target.value)} />
      <Input multiline label={t(file && /\.mp4$/i.test(file.name) ? 'learning.videoTranscript' : 'learning.audioTranscript')} value={fields.transcript} required={Boolean(file && !(/\.(srt|vtt)$/i.test(file.name)))} maxLength={20000} onChange={e => update('transcript', e.target.value)} />
      <Input multiline label={t('learning.attachmentProvenance')} value={fields.provenance} required maxLength={4000} onChange={e => update('provenance', e.target.value)} />
      <Select label={t('learning.attachmentSection')} value={fields.after_section} onChange={e => update('after_section', e.target.value)} options={[{ value: '', label: t('learning.attachmentFallback') }, ...(lesson.learning_content?.source_sections || []).map(value => ({ value, label: value }))]} />
    </fieldset><Notice {...action} /><Button type="submit" variant="secondary" disabled={locked || action.busy}>{t('instructorStudio.upload')}</Button></form>
  </section>
}


function AttachmentPlacement({ lesson, asset, disabled, onMove }) {
  const { t } = useTranslation()
  const [target, setTarget] = useState('')
  const info = attachmentPlacement(lesson, asset)
  return <li className="instructor-attachment-placement">
    <p><strong>{asset.label}</strong> ({asset.filename})</p>
    <p>{t('instructorStudio.placement.current')}: {asset.after_section || t('learning.attachmentFallback')}
      {info.unresolved && <span> · {t('instructorStudio.unresolvedPlacements')}</span>}</p>
    {asset.kind === 'video' && <p>{t('instructorStudio.placement.captions')}: {info.subtitle ? `${info.subtitle.label} (${info.subtitle.filename})` : t(info.ambiguous ? 'instructorStudio.placement.ambiguous' : 'instructorStudio.placement.noTrack')}</p>}
    {asset.kind === 'vtt' && <p>{t('instructorStudio.placement.track')}</p>}
    {info.eligible && <form className="instructor-inline-form" onSubmit={event => { event.preventDefault(); if (target && target !== asset.after_section && !disabled) onMove(target) }}>
      <Select label={`${t('instructorStudio.placement.destination')}: ${asset.label}`} value={target} disabled={disabled} required onChange={event => setTarget(event.target.value)} options={[{ value: '', label: t('instructorStudio.choose') }, ...info.headings.map(heading => ({ value: heading, label: heading }))]} />
      <Button type="submit" variant="secondary" disabled={disabled || !target || target === asset.after_section}>{t('instructorStudio.placement.move')}</Button>
    </form>}
  </li>
}
