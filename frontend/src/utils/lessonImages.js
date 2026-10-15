// Empty/missing alternatives mean decorative. Never invent text from file names.
export function lessonImageDescription(image, language) {
  const alternatives = image.alt_text
  if (!alternatives || typeof alternatives !== 'object' || Array.isArray(alternatives)) return { alt: '' }
  const preferred = language?.split('-')[0]
  for (const locale of new Set([preferred, 'en', 'ru', 'kk'])) {
    if (!['en', 'ru', 'kk'].includes(locale)) continue
    const text = alternatives[locale]
    if (typeof text === 'string' && text.trim()) return { alt: text.trim(), lang: locale }
  }
  return { alt: '' }
}

// Fetch private images through the JWT client, never through a supplied storage URL.
export function loadLessonImage(client, imageId, onLoad, onError, urlApi = URL) {
  const controller = new AbortController()
  let active = true
  let objectUrl = null

  const promise = (async () => {
    try {
      if (!Number.isSafeInteger(imageId) || imageId <= 0) throw new Error('Invalid lesson image ID')
      const { data } = await client.get(`/lesson-images/${imageId}/`, {
        responseType: 'blob', signal: controller.signal,
      })
      // Cancellation may race with a completed request, so check before creating a URL.
      if (!active) return
      if (!(data instanceof Blob) || !data.size || !data.type.startsWith('image/')) {
        throw new Error('Lesson image was not returned')
      }
      objectUrl = urlApi.createObjectURL(data)
      onLoad(objectUrl)
    } catch (error) {
      if (active) onError(error)
    }
  })()

  return {
    promise,
    dispose() {
      active = false
      controller.abort()
      if (objectUrl) {
        urlApi.revokeObjectURL(objectUrl)
        objectUrl = null
      }
    },
  }
}
