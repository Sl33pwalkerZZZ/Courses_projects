import { useId } from 'react'
import { useTranslation } from 'react-i18next'
import Button from '../ui/Button'

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
