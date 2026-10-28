import { useTranslation } from 'react-i18next'
import Button from '../ui/Button'
import { Input } from './StudioShared'
import { moveStudioItem, teachingEntryChange } from '../../utils/instructorStudio'

// Preserve the original declarative shape: editing a description must not add a
// competing text property that hides source content in the student renderer.
export default function EducationalSections({ value, onChange }) {
  const { t } = useTranslation()
  const update = (index, patch) => onChange(value.map((item, i) => i === index ? { ...item, ...patch } : item))
  return <>{value.map((item, index) => {
    if (item.type === 'image_placement') return null // Preserve placement metadata; it is not an interactive teaching card.
    const listKey = ['items', 'steps', 'cards', 'services'].find(key => Array.isArray(item[key]))
    const entries = listKey ? item[listKey] : []
    const updateEntry = (entryIndex, replacement) => update(index, { [listKey]: entries.map((entry, i) => i === entryIndex ? replacement : entry) })
    return <fieldset key={index}><legend>{t('instructorStudio.section')} {index + 1}</legend>
      <Input label={t('instructorStudio.heading')} value={item.title || ''} onChange={event => update(index, { title: event.target.value })} />
      <Input multiline label={t('instructorStudio.explanation')} value={item.description || ''} onChange={event => update(index, { description: event.target.value })} />
      {Array.isArray(item.rows) && <>
        <Input label={t('instructorStudio.tableHeaders')} value={(item.headers || []).join(' | ')} onChange={event => update(index, { headers: event.target.value.split('|').map(text => text.trim()) })} />
        <Input multiline label={t('instructorStudio.tableRows')} value={item.rows.map(row => row.join(' | ')).join('\n')} onChange={event => update(index, { rows: event.target.value.split('\n').map(row => row.split('|').map(text => text.trim())) })} />
      </>}
      {entries.map((entry, entryIndex) => <fieldset key={entryIndex}><legend>{t('instructorStudio.example')} {entryIndex + 1}</legend>
        {typeof entry !== 'string' && <Input label={t('instructorStudio.itemTitle')} value={entry.title || entry.name || entry.label || ''} onChange={event => { const key = ['title', 'name', 'label'].find(key => Object.hasOwn(entry, key)) || 'title'; updateEntry(entryIndex, { ...entry, [key]: event.target.value }) }} />}
        <Input multiline label={t('instructorStudio.explanation')} value={typeof entry === 'string' ? entry : entry.text || entry.description || entry.body || ''} onChange={event => updateEntry(entryIndex, teachingEntryChange(entry, event.target.value))} />
        {typeof entry !== 'string' && Object.hasOwn(entry, 'details') && <Input multiline label={t('instructorStudio.details')} value={entry.details} onChange={event => updateEntry(entryIndex, { ...entry, details: event.target.value })} />}
        {typeof entry !== 'string' && Object.hasOwn(entry, 'examples') && <Input multiline label={t('instructorStudio.examples')} value={entry.examples.join('\n')} onChange={event => updateEntry(entryIndex, { ...entry, examples: event.target.value.split('\n') })} />}
        {typeof entry !== 'string' && Object.hasOwn(entry, 'url') && <Input type="url" label={t('instructorStudio.referenceUrl')} value={entry.url} onChange={event => updateEntry(entryIndex, { ...entry, url: event.target.value })} />}
        <Button variant="ghost" onClick={() => update(index, { [listKey]: entries.filter((_, i) => i !== entryIndex) })}>{t('instructorStudio.removeItem')} {entryIndex + 1}</Button>
      </fieldset>)}
      {listKey && <Button variant="secondary" onClick={() => update(index, { [listKey]: [...entries, { title: '', text: '' }] })}>{t('instructorStudio.addItem')}</Button>}
      {Array.isArray(item.criteria) && <Input multiline label={t('instructorStudio.criteria')} value={item.criteria.join('\n')} onChange={event => update(index, { criteria: event.target.value.split('\n') })} />}
      {['note', 'warning'].filter(key => Object.hasOwn(item, key)).map(key => <Input key={key} multiline label={t(`instructorStudio.${key}`)} value={item[key]} onChange={event => update(index, { [key]: event.target.value })} />)}
      <div className="instructor-actions"><Button variant="ghost" disabled={index === 0} aria-label={`${t('instructorStudio.up')}: ${t('instructorStudio.section')} ${index + 1}`} onClick={() => onChange(moveStudioItem(value, index, -1))}>↑</Button><Button variant="ghost" disabled={index === value.length - 1} aria-label={`${t('instructorStudio.down')}: ${t('instructorStudio.section')} ${index + 1}`} onClick={() => onChange(moveStudioItem(value, index, 1))}>↓</Button><Button variant="ghost" onClick={() => { if (window.confirm(t('instructorStudio.removeSectionConfirm'))) onChange(value.filter((_, i) => i !== index)) }}>{t('instructorStudio.removeSection')}</Button></div>
    </fieldset>
  })}<div className="instructor-actions">{[['model_service', 'addTable', { headers: ['', ''], rows: [['', '']] }], ['categories', 'addExample', { items: [{ title: '', text: '' }] }], ['concept_hierarchy', 'addIllustration', { items: [{ title: 'AI', text: '' }] }]].map(([type, label, extra]) => <Button key={type} variant="secondary" onClick={() => onChange([...value, { type, title: '', description: '', ...extra }])}>{t(`instructorStudio.${label}`)}</Button>)}</div></>
}
