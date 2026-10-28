// IDs come only from the authorized lesson response, never arbitrary media URLs.
export function attachmentLayout(lesson, sections) {
  const anchors = new Set((sections || []).map(section => section.heading))
  const bySection = new Map(), fallback = [], seen = new Set()
  for (const asset of lesson.attachments || []) {
    if (!Number.isSafeInteger(asset.id) || asset.id <= 0 || !['audio', 'srt'].includes(asset.kind) || seen.has(asset.id)) continue
    seen.add(asset.id)
    if (!anchors.has(asset.after_section)) { fallback.push(asset); continue }
    const group = bySection.get(asset.after_section) || []
    group.push(asset)
    bySection.set(asset.after_section, group)
  }
  return { bySection, fallback }
}

export function loadLessonAttachment(client, asset, onLoad, onError, urlApi = URL) {
  const controller = new AbortController()
  let active = true, objectUrl = null
  const promise = (async () => {
    try {
      if (!Number.isSafeInteger(asset.id) || asset.id <= 0 || !['audio', 'srt'].includes(asset.kind)) throw new Error('Invalid attachment')
      const { data } = await client.get(`/lesson-attachments/${asset.id}/`, { responseType: 'blob', signal: controller.signal })
      if (!active) return
      const allowed = asset.kind === 'audio' ? ['audio/wav','audio/mpeg'] : ['application/x-subrip']
      const limit = asset.kind === 'audio' ? 20 * 1024 * 1024 : 1024 * 1024
      if (!(data instanceof Blob) || !data.size || data.size > limit || !allowed.includes(data.type.split(';')[0])) throw new Error('Unsupported attachment response')
      objectUrl = urlApi.createObjectURL(data)
      onLoad(objectUrl)
    } catch (error) { if (active) onError(error) }
  })()
  return { promise, dispose() {
    active = false
    controller.abort()
    if (objectUrl) { urlApi.revokeObjectURL(objectUrl); objectUrl = null }
  } }
}

export function downloadAttachment(src, filename, documentApi = document) {
  const link = documentApi.createElement('a')
  link.href = src
  link.download = filename
  documentApi.body.appendChild(link)
  link.click()
  link.remove()
}
