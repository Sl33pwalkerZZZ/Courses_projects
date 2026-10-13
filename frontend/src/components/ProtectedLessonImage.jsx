import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../api'
import { loadLessonImage } from '../utils/lessonImages'

export default function ProtectedLessonImage({ image }) {
  const { t } = useTranslation()
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
    return <img src={result.src} alt="" loading="lazy" onError={() => setResult({ imageId: image.id, error: true })} />
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
