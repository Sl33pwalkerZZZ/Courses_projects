// Only same-origin API paths returned by the grant endpoint reach native media.
export function safePlaybackPath(value) {
  return typeof value === 'string' && /^\/api\/lesson-attachments\/[1-9]\d*\/playback\/(?:poster\/|subtitles\/)?$/.test(value) ? value : null
}

export function revokeVideoGrant(id, token) {
  if (!Number.isSafeInteger(id) || typeof token !== 'string' || !token) return
  return fetch(`/api/lesson-attachments/${id}/playback-grant/`, {
    method: 'DELETE', credentials: 'same-origin', keepalive: true,
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ revoke_token: token }),
  }).catch(() => {})
}

export function requestVideoPlayback(client, id, onLoad, onError, subtitleId) {
  let active = true
  const grants = []
  const promise = (async () => {
    try {
      if (!Number.isSafeInteger(id) || id <= 0) throw new Error('Invalid video attachment')
      const { data } = await client.post(`/lesson-attachments/${id}/playback-grant/`, {}, { baseURL: '/api' })
      grants.push([id, data.revoke_token])
      if (!active) { revokeVideoGrant(id, data.revoke_token); return }
      const url = safePlaybackPath(data.url)
      if (!url) throw new Error('Invalid playback path')
      let subtitles = null
      if (Number.isSafeInteger(subtitleId) && subtitleId > 0) {
        const response = await client.post(`/lesson-attachments/${subtitleId}/playback-grant/`, {}, { baseURL: '/api' })
        grants.push([subtitleId, response.data.revoke_token])
        if (!active) { revokeVideoGrant(subtitleId, response.data.revoke_token); return }
        subtitles = safePlaybackPath(response.data.url)
        if (!subtitles) throw new Error('Invalid subtitle playback path')
      }
      if (active) onLoad({ url, subtitles, expiresAt: data.expires_at })
    } catch (error) { if (active) onError(error) }
  })()
  return { promise, dispose() { active = false; grants.forEach(([grantId, token]) => revokeVideoGrant(grantId, token)) } }
}
