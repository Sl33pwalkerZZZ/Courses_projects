export function reviewLoadErrorKey(error) {
  const status = error.response?.status
  return status === 404 ? 'reviews.unavailable' : status === 401 ? 'reviews.sessionExpired' : 'reviews.loadError'
}
