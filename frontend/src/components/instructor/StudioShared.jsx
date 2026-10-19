import { useEffect, useId, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import Button from '../ui/Button'
import { studioError } from '../../utils/instructorStudio'

export function useStudioResource(path) {
  const [state, setState] = useState({ loading: true, data: null, error: '' })
  const [revision, setRevision] = useState(0)
  const { t } = useTranslation()
  useEffect(() => {
    const controller = new AbortController()
    if (!path) return () => controller.abort()
    setState({ loading: true, data: null, error: '' })
    api.get(path, { signal: controller.signal }).then(({ data }) => {
      if (!controller.signal.aborted) setState({ loading: false, data, error: '' })
    }).catch(error => {
      if (!controller.signal.aborted) setState({ loading: false, data: null, error: studioError(error, t('instructorStudio.loadError')) })
    })
    return () => controller.abort()
  }, [path, revision, t])
  return { ...state, reload: () => setRevision(value => value + 1) }
}
export function ResourceState({ resource, children }) {
  const { t } = useTranslation()
  if (resource.loading) return <p role="status">{t('common.loading')}</p>
  if (resource.error) return <div role="alert"><p>{resource.error}</p><Button variant="secondary" onClick={resource.reload}>{t('common.retry')}</Button></div>
  return children(resource.data)
}
export function Field({ label, children, hint }) {
  const id = useId()
  return <div className="instructor-field"><label htmlFor={id}>{label}</label>{typeof children === 'function' ? children(id) : children}{hint && <small>{hint}</small>}</div>
}
export function Input({ label, multiline = false, ...props }) {
  return <Field label={label}>{id => multiline ? <textarea id={id} rows={5} {...props} /> : <input id={id} {...props} />}</Field>
}
export function Select({ label, options, ...props }) {
  return <Field label={label}>{id => <select id={id} {...props}>{options.map(item => <option key={item.value} value={item.value}>{item.label}</option>)}</select>}</Field>
}
export function Notice({ error, message }) {
  return <>{error && <p className="instructor-error" role="alert">{error}</p>}{message && <p role="status" className="instructor-success">{message}</p>}</>
}
// Every mutation is aborted on unmount; the existing API client additionally
// rejects obsolete responses/retries when the authentication generation changes.
export function useStudioAction() {
  const { t } = useTranslation()
  const controller = useRef(null)
  const active = useRef(false)
  const running = useRef(false)
  const [state, setState] = useState({ busy: false, error: '', message: '' })
  useEffect(() => { active.current = true; return () => { active.current = false; controller.current?.abort() } }, [])
  async function run(work, onSuccess, successKey = 'instructorStudio.saved') {
    if (!active.current || running.current) return
    const request = new AbortController()
    controller.current = request
    running.current = true
    setState({ busy: true, error: '', message: '' })
    try {
      const result = await work(request.signal)
      if (request.signal.aborted || !active.current) return
      setState({ busy: false, error: '', message: successKey ? t(successKey) : '' })
      onSuccess?.(result.data)
    } catch (error) {
      if (!request.signal.aborted && active.current) setState({ busy: false, error: studioError(error, t('instructorStudio.saveError')), message: '' })
    } finally { running.current = false }
  }
  return { ...state, run }
}
