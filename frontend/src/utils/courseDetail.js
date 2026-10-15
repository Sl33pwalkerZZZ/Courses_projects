import axios from 'axios'

export function courseErrorKind(error) {
  // Session changes and request cleanup are intentional cancellations.
  if (axios.isCancel(error)) return null
  return error.response?.status === 404 ? 'notFound' : 'loadError'
}

export function loadCourse(client, slug, onLoaded, onError) {
  const controller = new AbortController()
  let active = true
  const promise = (async () => {
    try {
      const { data } = await client.get(`/courses/${encodeURIComponent(slug)}/`, { signal: controller.signal })
      if (active) onLoaded(data)
    } catch (error) {
      const kind = courseErrorKind(error)
      if (active && kind) onError(kind)
    }
  })()
  return {
    promise,
    dispose() {
      active = false
      controller.abort()
    },
  }
}
