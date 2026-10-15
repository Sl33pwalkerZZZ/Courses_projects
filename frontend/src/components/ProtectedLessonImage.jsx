import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../api'
import { lessonImageDescription, loadLessonImage } from '../utils/lessonImages'

export default function ProtectedLessonImage({ image }) {
  const { t, i18n } = useTranslation()
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
    return <img src={result.src} alt={description.alt} lang={description.lang} loading="lazy" onError={() => setResult({ imageId: image.id, error: true })} />
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
