import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import Button from '../ui/Button'
import { Input, Notice, Select } from './StudioShared'
import { useStudioAction } from './useStudio'

export default function LessonAttachmentManager({ lesson, locked, onSaved }) {
  const { t } = useTranslation(), action = useStudioAction()
  const [file, setFile] = useState(null)
  const [fields, setFields] = useState({ label: '', caption: '', transcript: '', provenance: '', after_section: '' })
  const update = (key, value) => setFields(current => ({ ...current, [key]: value }))
  return <section><h4>{t('learning.attachments')}</h4>
    <ul>{(lesson.attachments || []).map(asset => <li key={asset.id}>{asset.label} ({asset.filename})</li>)}</ul>
    <form className="instructor-form" onSubmit={event => {
      event.preventDefault()
      if (!file) return
      const body = new FormData()
      body.append('file', file)
      Object.entries(fields).forEach(([key, value]) => body.append(key, value))
      action.run(signal => api.post(`/studio/lessons/${lesson.id}/attachments/`, body, { signal }), onSaved)
    }}><fieldset disabled={locked || action.busy}><legend>{t('learning.addAttachment')}</legend>
      <Input type="file" label={t('learning.attachmentFile')} accept=".mp3,.wav,.srt" required onChange={event => setFile(event.target.files[0] || null)} />
      <Input label={t('learning.attachmentLabel')} value={fields.label} required maxLength={255} onChange={e => update('label', e.target.value)} />
      <Input multiline label={t('learning.attachmentCaption')} value={fields.caption} maxLength={2000} onChange={e => update('caption', e.target.value)} />
      <Input multiline label={t('learning.audioTranscript')} value={fields.transcript} required={Boolean(file && !file.name.toLowerCase().endsWith('.srt'))} maxLength={20000} onChange={e => update('transcript', e.target.value)} />
      <Input multiline label={t('learning.attachmentProvenance')} value={fields.provenance} required maxLength={4000} onChange={e => update('provenance', e.target.value)} />
      <Select label={t('learning.attachmentSection')} value={fields.after_section} onChange={e => update('after_section', e.target.value)} options={[{ value: '', label: t('learning.attachmentFallback') }, ...(lesson.learning_content?.source_sections || []).map(value => ({ value, label: value }))]} />
    </fieldset><Notice {...action} /><Button type="submit" variant="secondary" disabled={locked || action.busy}>{t('instructorStudio.upload')}</Button></form>
  </section>
}
