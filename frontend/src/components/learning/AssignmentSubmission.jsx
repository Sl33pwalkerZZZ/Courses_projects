import { useCallback, useEffect, useId, useRef, useState, useSyncExternalStore } from 'react'
import { useTranslation } from 'react-i18next'
import api, { getAuthSession, subscribeAuth } from '../../api'
import { formatSubmissionTimestamps } from '../../utils/assignmentSubmissionDates'

const ACCEPTED = '.pdf,.docx,.pptx,.xlsx,.csv,.txt,.png,.jpg,.jpeg,.webp,.mp4'
const PER_FILE = 10 * 1024 * 1024
const VIDEO_FILE = 50 * 1024 * 1024
const TOTAL = 100 * 1024 * 1024

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export default function AssignmentSubmission(props) {
  const session = useSyncExternalStore(subscribeAuth, getAuthSession, getAuthSession)
  return <AssignmentSubmissionForm key={`${props.assignment.id}:${session.generation}:${Boolean(props.preview)}`} {...props} />
}

function AssignmentSubmissionForm({ assignment, preview = false }) {
  const { t, i18n } = useTranslation()
  const id = useId()
  const active = useRef(false)
  const [data, setData] = useState(null)
  const [content, setContent] = useState('')
  const [files, setFiles] = useState([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const endpoint = `/assignments/${assignment.id}/submissions/`

  const load = useCallback(async () => {
    try {
      const response = await api.get(endpoint)
      if (active.current) { setData(response.data); setError('') }
    } catch (failure) {
      if (active.current && failure.code !== 'ERR_CANCELED') { setData(null); setError(failure.response?.status === 403 ? 'access' : 'load') }
    }
  }, [endpoint])
  useEffect(() => {
    active.current = true
    if (!preview) Promise.resolve().then(load)
    return () => { active.current = false }
  }, [load, preview])

  const history = data?.submissions || []
  const latest = history.at(-1)
  const canSubmit = !preview && (!latest || latest.status === 'rejected' || latest.status === 'draft')
  function selectFiles(fileList) {
    const selected = [...fileList]
    setError('')
    if (files.length + selected.length > 5) { setError('tooMany'); return }
    const all = [...files, ...selected]
    const total = all.reduce((sum, file) => sum + file.size, 0)
    if (total > TOTAL) { setError('totalSize'); return }
    for (const file of selected) {
      const extension = `.${file.name.split('.').pop().toLowerCase()}`
      if (!ACCEPTED.split(',').includes(extension)) { setError('fileType'); return }
      if (file.size > (extension === '.mp4' ? VIDEO_FILE : PER_FILE)) { setError('fileSize'); return }
    }
    setFiles(all)
  }
  async function submit(event) {
    event.preventDefault()
    if (busy || !canSubmit) return
    if (!content.trim() && !files.length) { setError('empty'); return }
    if (assignment.type === 'file' && !files.length) { setError('fileRequired'); return }
    setBusy(true); setError(''); setNotice('')
    const body = new FormData()
    if (content.trim()) body.append('content', content)
    files.forEach(file => body.append('files', file))
    try {
      await api.post(endpoint, body)
      if (active.current) { setContent(''); setFiles([]); setNotice('submitted'); await load() }
    } catch (failure) {
      if (!active.current) return
      const statusCode = failure.response?.status
      setError(statusCode === 409 ? 'conflict' : statusCode === 400 ? 'invalid' : statusCode === 403 ? 'access' : 'submit')
    } finally { if (active.current) setBusy(false) }
  }
  async function download(submission, attachment) {
    try {
      const { data: blob } = await api.get(`${endpoint}${submission.id}/files/${attachment.id}/`, { responseType: 'blob' })
      if (active.current) downloadBlob(blob, attachment.filename)
    } catch { if (active.current) setError('download') }
  }
  async function downloadLegacy(submission) {
    try {
      const { data: blob } = await api.get(`${endpoint}${submission.id}/legacy-file/`, { responseType: 'blob' })
      if (active.current) downloadBlob(blob, t('assignmentSubmission.legacyFile'))
    } catch { if (active.current) setError('download') }
  }

  return <section className="assignment-submission" aria-labelledby={`${id}-title`} aria-busy={busy}>
    <h3 id={`${id}-title`}>{t('assignmentSubmission.title')}</h3>
    <p>{assignment.description}</p>
    {preview ? <p role="note">{t('assignmentSubmission.preview')}</p> : <>
      {!data && !error && <p role="status">{t('common.loading')}</p>}
      {error === 'load' && <p role="alert">{t('assignmentSubmission.loadError')} <button type="button" onClick={load}>{t('common.retry')}</button></p>}
      {error === 'access' && <p role="alert">{t('assignmentSubmission.accessError')}</p>}
      {history.length > 0 && <ol className="assignment-submission-history" aria-label={t('assignmentSubmission.history')}>
        {history.map((item, index) => {
          const dates = formatSubmissionTimestamps(item, i18n.resolvedLanguage)
          return <li key={item.id}>
            <div className="assignment-submission-history-heading"><strong>{t('assignmentSubmission.revision', { number: index + 1 })}</strong>
              <span>{t(`assignmentSubmission.status.${item.status}`)}</span></div>
            {(dates.submittedAt || dates.reviewedAt) && <dl className="assignment-submission-dates">
              {dates.submittedAt && <div><dt>{t('assignmentSubmission.submittedAt')}</dt><dd><time dateTime={dates.submittedAt.dateTime}>{dates.submittedAt.label}</time></dd></div>}
              {dates.reviewedAt && <div><dt>{t('assignmentSubmission.reviewedAt')}</dt><dd><time dateTime={dates.reviewedAt.dateTime}>{dates.reviewedAt.label}</time></dd></div>}
            </dl>}
          {item.content && <p className="assignment-submission-answer">{item.content}</p>}
          {item.feedback && <div className="assignment-submission-feedback"><strong>{t('assignmentSubmission.feedback')}</strong><p>{item.feedback}</p></div>}
          {item.rubric_scores && <p className="assignment-submission-rubric">{t('assignmentSubmission.rubricTotal', { total: Object.values(item.rubric_scores).reduce((sum, value) => sum + value, 0) })}</p>}
          {item.attachments?.map(file => <button className="lesson-text-button" type="button" key={file.id} onClick={() => download(item, file)}>{t('assignmentSubmission.download', { filename: file.filename })}</button>)}
          {item.legacy_file_available && <button className="lesson-text-button" type="button" onClick={() => downloadLegacy(item)}>{t('assignmentSubmission.legacyFile')}</button>}
          {item.review_history?.filter(event => event.action === 'reopened').map((event, eventIndex) => <p role="note" key={eventIndex}>{t('assignmentSubmission.reopened')}</p>)}
          </li>
        })}
      </ol>}
      {canSubmit && data && <form className="assignment-submission-form" onSubmit={submit}>
        <label htmlFor={`${id}-content`}>{t('assignmentSubmission.textLabel')}</label>
        <textarea id={`${id}-content`} value={content} onChange={event => setContent(event.target.value)} maxLength={100000} rows={7} />
        <label htmlFor={`${id}-files`}>{t('assignmentSubmission.filesLabel')}</label>
        <input id={`${id}-files`} type="file" accept={ACCEPTED} multiple onChange={event => { selectFiles(event.target.files); event.target.value = '' }} />
        <p>{t('assignmentSubmission.fileRules')}</p>
        {files.length > 0 && <ul>{files.map((file, index) => <li key={`${file.name}-${file.size}-${index}`}>
          {file.name} ({Math.ceil(file.size / (1024 * 1024))} MB) <button type="button" onClick={() => setFiles(current => current.filter((_, position) => position !== index))}>{t('assignmentSubmission.removeFile')}</button>
        </li>)}</ul>}
        <button className="academic-button" type="submit" disabled={busy}>{t(busy ? 'assignmentSubmission.sending' : 'assignmentSubmission.submit')}</button>
      </form>}
      {latest?.status === 'approved' && <p role="status">{t('assignmentSubmission.locked')}</p>}
      {notice && <p role="status">{t(`assignmentSubmission.${notice}`)}</p>}
      {error && !['load', 'access'].includes(error) && <p role="alert">{t(`assignmentSubmission.error.${error}`)}</p>}
    </>}
  </section>
}
