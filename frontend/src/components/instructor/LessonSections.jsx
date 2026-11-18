import { useId, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Button from '../ui/Button'
import { Input } from './StudioShared'
import { appendSection, hasPendingSection, renameSection, sectionInventory } from '../../utils/studioSections'

export default function LessonSections({ form, lesson, setForm, disabled = false }) {
  const { t } = useTranslation()
  const [error, setError] = useState('')
  const [addError, setAddError] = useState('')
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
      <Input label={`${t('instructorStudio.sectionHeading')} ${index + 1}`} value={form.section_inputs?.[index] ?? section.heading} maxLength={255} disabled={disabled || !section.valid} aria-invalid={!!form.section_inputs && form.section_inputs[index].trim() !== section.heading} aria-describedby={showError ? errorId : undefined} onChange={event => {
        const raw = event.target.value
        const section_inputs = [...(form.section_inputs || form.learning_content.source_sections)]
        section_inputs[index] = raw
        try { const next = renameSection(form, lesson, section.heading, raw); setForm({ ...next, section_inputs }); setError('') }
        catch { setForm({ ...form, section_inputs }); setError('ambiguousSectionRename') }
      }} />
      {!section.valid && <p role="status">{t('instructorStudio.ambiguousSectionRename')}</p>}
      {section.assets.length ? <ul>{section.assets.map(asset => <li key={`${asset.kind}-${asset.id}`}>{assetLabel(asset)}</li>)}</ul> : <p>{t('instructorStudio.noSectionMedia')}</p>}
    </li>)}</ol>
    <fieldset disabled={disabled}>
      <legend>{t('instructorStudio.sectionCreation.title')}</legend>
      <p>{t('instructorStudio.sectionCreation.hint')}</p>
      {!sections.length && form.text_content && <p>{t('instructorStudio.sectionCreation.existingText')}</p>}
      <Input label={t('instructorStudio.sectionCreation.heading')} value={form.section_new?.title || ''} maxLength={255} aria-invalid={addError === 'heading' || undefined} aria-describedby={addError ? `${errorId}-add` : undefined} onChange={event => { setAddError(''); setForm({ ...form, section_new: { ...form.section_new, title: event.target.value } }) }} />
      <Input multiline label={t('instructorStudio.sectionCreation.text')} value={form.section_new?.text || ''} aria-invalid={addError === 'text' || undefined} aria-describedby={addError ? `${errorId}-add` : undefined} onChange={event => { setAddError(''); setForm({ ...form, section_new: { ...form.section_new, text: event.target.value } }) }} />
      {addError && <p id={`${errorId}-add`} role="alert">{t(`instructorStudio.sectionCreation.errors.${addError}`)}</p>}
      <Button variant="secondary" onClick={() => {
        try { setForm(current => appendSection(current, lesson)); setAddError('') }
        catch (error) { setAddError(error.message) }
      }}>{t('instructorStudio.sectionCreation.add')}</Button>
      {hasPendingSection(form) && <p role="status">{t('instructorStudio.sectionCreation.pending')}</p>}
    </fieldset>
    {!!unresolved.length && <div role="status"><h5>{t('instructorStudio.unresolvedPlacements')}</h5><ul>{unresolved.map((asset, index) => <li key={index}>{assetLabel(asset)} — {asset.after_section || t('instructorStudio.noPlacement')}</li>)}</ul></div>}
  </section>
}
