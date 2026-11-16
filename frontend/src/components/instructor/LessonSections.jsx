import { useId, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Input } from './StudioShared'
import { renameSection, sectionInventory } from '../../utils/studioSections'

export default function LessonSections({ form, lesson, setForm }) {
  const { t } = useTranslation()
  const [error, setError] = useState('')
  const errorId = useId()
  const showError = error || form.section_inputs?.some((title, i) => !title.trim() || title.trim() !== form.learning_content.source_sections[i])
  const { sections, unresolved } = sectionInventory(form, lesson)
  const assetLabel = asset => `${asset.kind.toUpperCase()} · ${asset.label || asset.filename || `#${asset.id}`}`
  return <section className="instructor-lesson-sections" aria-label={t('instructorStudio.lessonSections')}>
    <h4>{t('instructorStudio.lessonSections')}</h4>
    <p>{t('instructorStudio.sectionRenameHint')}</p>
    {!sections.length && <p>{t('instructorStudio.noStructuredSections')}</p>}
    {showError && <p id={errorId} role="alert">{t('instructorStudio.ambiguousSectionRename')}</p>}
    <ol>{sections.map((section, index) => <li key={index}>
      <Input label={`${t('instructorStudio.sectionHeading')} ${index + 1}`} value={form.section_inputs?.[index] ?? section.heading} maxLength={255} disabled={!section.valid} aria-invalid={!!form.section_inputs && form.section_inputs[index].trim() !== section.heading} aria-describedby={showError ? errorId : undefined} onChange={event => {
        const raw = event.target.value
        const section_inputs = [...(form.section_inputs || form.learning_content.source_sections)]
        section_inputs[index] = raw
        try { const next = renameSection(form, lesson, section.heading, raw); setForm({ ...next, section_inputs }); setError('') }
        catch { setForm({ ...form, section_inputs }); setError('ambiguousSectionRename') }
      }} />
      {!section.valid && <p role="status">{t('instructorStudio.ambiguousSectionRename')}</p>}
      {section.assets.length ? <ul>{section.assets.map(asset => <li key={`${asset.kind}-${asset.id}`}>{assetLabel(asset)}</li>)}</ul> : <p>{t('instructorStudio.noSectionMedia')}</p>}
    </li>)}</ol>
    {!!unresolved.length && <div role="status"><h5>{t('instructorStudio.unresolvedPlacements')}</h5><ul>{unresolved.map((asset, index) => <li key={index}>{assetLabel(asset)} — {asset.after_section || t('instructorStudio.noPlacement')}</li>)}</ul></div>}
  </section>
}
