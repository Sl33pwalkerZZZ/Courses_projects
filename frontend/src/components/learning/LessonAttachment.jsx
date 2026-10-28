import { useEffect, useId, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import { useAuthSession } from '../../hooks/useAuth'
import { downloadAttachment, loadLessonAttachment } from '../../utils/lessonAttachments'
import './lessonAttachments.css'

export default function LessonAttachment({ asset }) {
  const { generation } = useAuthSession()
  const { id: assetId, kind, filename } = asset
  const [result, setResult] = useState(null), [requested, setRequested] = useState({ count: 0, generation, id: assetId })
  const id = useId(), audio = kind === 'audio'
  const current = result?.id === asset.id && result.generation === generation ? result : null
  useEffect(() => {
    if (!audio && (requested.count === 0 || requested.generation !== generation || requested.id !== assetId)) return
    const request = loadLessonAttachment(api, { id: assetId, kind }, src => {
      setResult({ id: assetId, generation, src })
      if (!audio) downloadAttachment(src, filename)
    }, () => setResult({ id: assetId, generation, error: true }))
    return () => request.dispose()
  }, [assetId, kind, filename, audio, generation, requested.count, requested.generation, requested.id])
  const retry = () => { setResult(null); setRequested(value => ({ count: value.count + 1, generation, id: assetId })) }
  return <AttachmentContent asset={asset} id={id} src={current?.src} error={current?.error}
    busy={requested.count > 0 && requested.generation === generation && requested.id === assetId} onRetry={retry}
    onMediaError={() => setResult({ id: assetId, generation, error: true })} />
}

// Pure presentation is shared by the live player and focused accessibility tests.
export function AttachmentContent({ asset, id, src, error, busy, onRetry, onMediaError }) {
  const { t } = useTranslation(), audio = asset.kind === 'audio'
  return <figure className="lesson-attachment" aria-labelledby={`${id}-label`}>
    <h3 id={`${id}-label`}>{asset.label}</h3>
    {audio && src && <audio controls preload="metadata" src={src} aria-labelledby={`${id}-label`} aria-describedby={`${id}-transcript`} onError={onMediaError} />}
    {audio && !src && !error && <p role="status">{t('common.loading')}</p>}
    {!audio && !src && !error && <button className="lesson-text-button" type="button" onClick={onRetry} disabled={busy}>{t(busy ? 'common.loading' : 'learning.downloadSubtitles')}</button>}
    {!audio && src && <a href={src} download={asset.filename}>{t('learning.downloadSubtitles')}</a>}
    {error && <div role="alert"><p>{t('lessonWorkspace.loadError')}</p><button type="button" className="lesson-text-button" onClick={onRetry}>{t('common.retry')}</button></div>}
    {asset.caption && <figcaption>{asset.caption}</figcaption>}
    {audio && <section className="lesson-attachment-transcript" id={`${id}-transcript`}><h4>{t('learning.audioTranscript')}</h4><p>{asset.transcript}</p></section>}
  </figure>
}
