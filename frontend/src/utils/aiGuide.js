export const AI_GUIDE_QUESTION_LIMIT = 1000

export function guideErrorKey(error) {
  const status = error?.response?.status
  if (status === 401 || status === 403 || status === 404) return 'aiGuide.accessError'
  if (status === 429) return 'aiGuide.rateLimit'
  if (status === 503) return 'aiGuide.unavailable'
  return 'aiGuide.error'
}

// A lesson/session owns each request. Never allow a delayed answer into another session.
export function createGuideRequest(client, { lessonId, question, language, getGeneration }) {
  const controller = new AbortController()
  const generation = getGeneration()
  const text = question.trim()
  if (!text || text.length > AI_GUIDE_QUESTION_LIMIT) throw new Error('Invalid question')
  const result = client.post('/ai-guide/', {
    lesson_id: lessonId, question: text, language: ['ru', 'kk', 'en'].includes(language) ? language : 'ru',
  }, { signal: controller.signal }).then(({ data }) => {
    if (controller.signal.aborted || generation !== getGeneration()) {
      const error = new Error('Discarded stale answer')
      error.name = 'AbortError'
      throw error
    }
    if (typeof data?.answer !== 'string' || !data.answer.trim()) throw new Error('Empty answer')
    return data.answer
  })
  return { result, cancel: () => controller.abort() }
}
