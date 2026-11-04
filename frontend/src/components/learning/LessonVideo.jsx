import { useEffect, useId, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import { useAuthSession } from '../../hooks/useAuth'
import { loadLessonImage } from '../../utils/lessonImages'
import { requestVideoPlayback } from '../../utils/lessonVideo'

export default function LessonVideo({ asset }) {
  const { generation } = useAuthSession(), id = useId(), video = useRef(null)
  const [attempt, setAttempt] = useState(0), [result, setResult] = useState(null)
  const current = result?.generation === generation && result.id === asset.id ? result : null
  useEffect(() => {
    const request = requestVideoPlayback(api, asset.id,
      playback => setResult({ ...playback, id: asset.id, generation }),
      error => setResult({ id: asset.id, generation, error: [401, 403].includes(error.response?.status) ? 'unauthorized' : 'failed' }), asset.subtitle_attachment_id)
    const element = video.current
    return () => {
      request.dispose()
      if (element) { element.pause(); element.removeAttribute('src'); element.load() }
    }
  }, [asset.id, asset.subtitle_attachment_id, generation, attempt])
  const [poster, setPoster] = useState(null)
  useEffect(() => {
    if (!Number.isSafeInteger(asset.poster_image_id) || asset.poster_image_id <= 0) return
    const request = loadLessonImage(api, asset.poster_image_id,
      src => setPoster({ src, id: asset.poster_image_id, generation }), () => {})
    return () => request.dispose()
  }, [asset.poster_image_id, generation])
  const retry = () => { setResult(null); setAttempt(value => value + 1) }
  return <VideoContent asset={asset} id={id} playback={current} poster={poster?.id === asset.poster_image_id && poster.generation === generation ? poster.src : undefined} videoRef={video} onRetry={retry}
    onError={() => setResult({ id: asset.id, generation, error: 'failed' })} />
}

export function VideoContent({ asset, id, playback, poster, videoRef, onRetry, onError }) {
  const { t } = useTranslation()
  return <figure className="lesson-attachment lesson-video" aria-labelledby={`${id}-label`}>
    <h3 id={`${id}-label`}>{asset.label}</h3>
    <video ref={videoRef} controls playsInline preload="metadata" src={playback?.url || undefined}
      poster={poster} aria-labelledby={`${id}-label`} aria-describedby={`${id}-transcript`} onError={onError}>
      {playback?.subtitles && <track kind="subtitles" src={playback.subtitles} srcLang={asset.subtitle_language || 'ru'} label={t('learning.videoSubtitles')} />}
    </video>
    {!playback && <p role="status">{t('common.loading')}</p>}
    {playback?.error && <div role="alert"><p>{t(playback.error === 'unauthorized' ? 'learning.videoUnauthorized' : 'learning.videoError')}</p>
      <button type="button" className="lesson-text-button" onClick={onRetry}>{t('common.retry')}</button></div>}
    {asset.caption && <figcaption>{asset.caption}</figcaption>}
    <section className="lesson-attachment-transcript" id={`${id}-transcript`}><h4>{t('learning.videoTranscript')}</h4><p>{asset.transcript}</p></section>
  </figure>
}
