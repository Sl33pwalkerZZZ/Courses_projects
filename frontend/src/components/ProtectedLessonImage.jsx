import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../api'
import { lessonImageDescription, loadLessonImage } from '../utils/lessonImages'

export default function ProtectedLessonImage({ image, enlarge = false }) {
  const { t, i18n } = useTranslation()
  const dialog = useRef(null)
  const [result, setResult] = useState(null)
  const [retry, setRetry] = useState(0)

  useEffect(() => {
    const request = loadLessonImage(api, image.id,
      (src) => setResult({ imageId: image.id, src }),
      () => setResult({ imageId: image.id, error: true }),
    )
    return () => request.dispose()
  }, [image.id, retry])

  if (result?.imageId === image.id && result.src) {
    const description = lessonImageDescription(image, i18n.resolvedLanguage || i18n.language)
    const illustration = <img src={result.src} alt={description.alt} lang={description.lang} loading="lazy" onError={() => setResult({ imageId: image.id, error: true })} />
    if (!enlarge) return illustration
    return <>
      <button type="button" className="lesson-image-enlarge" aria-label={`${t('learning.enlargeImage')}: ${description.alt}`} onClick={() => dialog.current?.showModal()}>{illustration}</button>
      <dialog ref={dialog} className="lesson-image-dialog" aria-label={`${t('learning.enlargeImage')}: ${description.alt}`} onClick={event => { if (event.target === dialog.current) dialog.current.close() }}>
        <button type="button" className="lesson-image-close" autoFocus onClick={() => dialog.current.close()}>{t('learning.closeImage')}</button>
        <img src={result.src} alt={description.alt} lang={description.lang} />
      </dialog>
    </>
  }
  if (result?.imageId === image.id && result.error) {
    return <div role="alert">
      <p>{t('lessonWorkspace.loadError')}</p>
      <button className="lesson-text-button" type="button" onClick={() => {
        setResult(null)
        setRetry((value) => value + 1)
      }}>{t('common.retry')}</button>
    </div>
  }
  return <p role="status">{t('common.loading')}</p>
}
