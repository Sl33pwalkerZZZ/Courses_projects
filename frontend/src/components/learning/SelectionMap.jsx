import { useCallback, useEffect, useId, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import { comparisonCriteria, emptySelectionMap, selectionFields, selectionMapProblems, updateComparedService, normalizeSelectionMap, serializeSelectionMap } from '../../utils/selectionMap'
import './learning.css'

export default function SelectionMap({ assignment, preview = false }) {
  const { t } = useTranslation()
  const id = useId()
  const active = useRef(false)
  const busyRef = useRef(false)
  const [record, setRecord] = useState(null)
  const [payload, setPayload] = useState(emptySelectionMap)
  const [busy, setBusy] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [problems, setProblems] = useState([])
  const [confirm, setConfirm] = useState(false)
  const endpoint = `/assignments/${assignment.id}/selection-map/`
  const load = useCallback(async () => {
    try {
      const { data } = await api.get(endpoint)
      if (active.current) {
        setError('')
        setRecord(data)
        setPayload(normalizeSelectionMap(data.payload))
        setProblems([])
        setConfirm(false)
      }
    } catch { if (active.current) setError('loadError') }
    finally { if (active.current) setBusy(false) }
  }, [endpoint])
  function reload() { setBusy(true); setError(''); load() }
  useEffect(() => { active.current = true; Promise.resolve().then(() => { if (active.current) load() }); return () => { active.current = false } }, [load]) // Assignment/session parent is keyed.
  const locked = preview || ['pending', 'approved'].includes(record?.status)
  function change(key, value) {
    setPayload(current => ({ ...current, [key]: value }))
    setNotice('unsaved')
    setConfirm(false)
  }
  async function persist(submit) {
    if (busyRef.current || locked) return
    const invalid = submit ? selectionMapProblems(payload) : []
    setProblems(invalid)
    if (invalid.length) { setError('validation'); setConfirm(false); return }
    busyRef.current = true
    setBusy(true)
    setError('')
    try {
      const { data } = await api[submit ? 'post' : 'put'](submit ? `${endpoint}submit/` : endpoint, { revision: record.revision, payload: serializeSelectionMap(payload) })
      if (active.current) { setRecord(data); setPayload(normalizeSelectionMap(data.payload)); setNotice(submit ? 'submitted' : 'saved'); setConfirm(false) }
    } catch (failure) {
      if (active.current) setError(failure.response?.status === 409 ? 'conflict' : failure.response?.status === 400 ? 'validation' : 'saveError')
    } finally { busyRef.current = false; if (active.current) setBusy(false) }
  }
  const field = (key, value, onChange, label = t(`selectionMap.fields.${key}`)) => <label className="selection-field" key={key}>
    <span>{label}</span><textarea value={value || ''} onChange={event => onChange(event.target.value)} rows={3} maxLength={comparisonCriteria.includes(key) ? 2000 : 4000}
      aria-invalid={problems.includes(key.startsWith('testing-') ? 'testing_results' : comparisonCriteria.includes(key) ? 'comparison_criteria' : key) || undefined} aria-describedby={problems.length ? `${id}-errors` : undefined} />
  </label>
  return <section className="selection-map" aria-labelledby={`${id}-title`} aria-busy={busy}>
    <h3 id={`${id}-title`}>{t('selectionMap.title')}</h3>
    <p>{t('selectionMap.safety')}</p>
    <p className="learning-source-note">{t('selectionMap.noExternalCalls')}</p>
    {!record ? <><p role="status">{busy ? t('common.loading') : t('selectionMap.loadError')}</p><button type="button" disabled={busy} onClick={reload}>{t('common.retry')}</button></> : <>
      <p className="selection-status" role="status">{t('selectionMap.statusLabel')}: {t(`selectionMap.status.${record.status}`)}</p>
      {preview && <p>{t('selectionMap.preview')}</p>}
      {record.reviewer_comment && <div className="selection-feedback"><h4>{t('selectionMap.feedback')}</h4><p>{record.reviewer_comment}</p></div>}
      {record.review_history?.length > 0 && <details><summary>{t('selectionMap.history')}</summary><ul>{record.review_history.map((item, index) => <li key={index}>{t(`selectionMap.status.${item.status || 'rejected'}`)}: {item.reviewer_comment || item.comment || ''}</li>)}</ul></details>}
      <form onSubmit={event => { event.preventDefault(); setConfirm(true) }}>
        <fieldset disabled={locked || busy}><legend>{t('selectionMap.taskHeading')}</legend>
          {selectionFields.slice(0, 4).map(key => field(key, payload[key], value => change(key, value)))}
          <label className="selection-field"><span>{t('selectionMap.fields.data_classification')}</span><select aria-invalid={problems.includes('data_classification') || undefined} aria-describedby={problems.length ? `${id}-errors` : undefined} value={payload.data_classification} onChange={event => change('data_classification', event.target.value)}>
            {['public', 'internal', 'confidential'].map(key => <option key={key} value={key}>{t(`selectionMap.classification.${key}`)}</option>)}
          </select></label>
          <p>{t('selectionMap.anonymize')}</p>
          <fieldset><legend>{t('selectionMap.fields.services')}</legend>
            {payload.services.map((service, index) => <label className="selection-field" key={index}><span>{t('selectionMap.serviceNumber', { number: index + 1 })}</span>
              <input aria-invalid={problems.includes('services') || undefined} aria-describedby={problems.length ? `${id}-errors` : undefined} maxLength={120} value={service} onChange={event => { setPayload(current => updateComparedService(current, index, event.target.value)); setNotice('unsaved'); setConfirm(false) }} /></label>)}
            {payload.services.length < 3 ? <button type="button" onClick={() => change('services', [...payload.services, ''])}>{t('selectionMap.addService')}</button>
              : <button type="button" onClick={() => { change('services', payload.services.slice(0, 2)); change('testing_results', payload.testing_results.filter(row => row.service !== payload.services[2])); if (payload.selected_service === payload.services[2]) change('selected_service', '') }}>{t('selectionMap.removeService')}</button>}
          </fieldset>
          <fieldset><legend>{t('selectionMap.fields.comparison_criteria')}</legend>
            {comparisonCriteria.map(key => field(key, payload.comparison_criteria[key], value => change('comparison_criteria', { ...payload.comparison_criteria, [key]: value }), t(`selectionMap.criteria.${key}`)))}
          </fieldset>
          <fieldset><legend>{t('selectionMap.fields.testing_results')}</legend>
            {payload.services.map((service, index) => field(`testing-${index}`, payload.testing_results.find(row => row.service === service)?.result || '', value => {
              const rows = payload.services.map(name => ({ service: name, result: name === service ? value : payload.testing_results.find(row => row.service === name)?.result || '' }))
              change('testing_results', rows)
            }, t('selectionMap.resultFor', { service: service || t('selectionMap.serviceNumber', { number: index + 1 }) })))}
          </fieldset>
          <label className="selection-field"><span>{t('selectionMap.fields.selected_service')}</span><select aria-invalid={problems.includes('selected_service') || undefined} aria-describedby={problems.length ? `${id}-errors` : undefined} value={payload.selected_service} onChange={event => change('selected_service', event.target.value)}>
            <option value="">{t('selectionMap.choose')}</option>{payload.services.filter(Boolean).map((service, index) => <option key={index} value={service}>{service}</option>)}
          </select></label>
          {field('final_justification', payload.final_justification, value => change('final_justification', value))}
        </fieldset>
        {!locked && <div className="selection-actions"><button type="button" disabled={busy} onClick={() => persist(false)}>{t('selectionMap.saveDraft')}</button><button className="academic-button" type="submit" disabled={busy}>{t('selectionMap.submit')}</button></div>}
        {confirm && !locked && <div className="selection-confirm" role="group" aria-label={t('selectionMap.confirmTitle')}><p>{t('selectionMap.confirmText')}</p><button type="button" disabled={busy} onClick={() => persist(true)}>{t('selectionMap.confirmSubmit')}</button><button type="button" onClick={() => setConfirm(false)}>{t('common.cancel')}</button></div>}
      </form>
    </>}
    {notice && <p role="status">{t(`selectionMap.${notice}`)}</p>}
    {error && <div id={`${id}-errors`} role="alert"><p>{t(`selectionMap.${error}`)}</p>{problems.length > 0 && <ul>{problems.map(key => <li key={key}>{t(`selectionMap.fields.${key}`)}</li>)}</ul>}
      {error === 'conflict' && <button type="button" disabled={busy} onClick={reload}>{t('selectionMap.reload')}</button>}</div>}
  </section>
}
