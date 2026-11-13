// Match the progress API's order, including a stable ID tie-breaker.
export function orderCurriculum(modules = []) {
  const compare = (a, b) => a.order - b.order || a.id - b.id
  return [...modules].sort(compare).map((module) => ({
    ...module, lessons: [...(module.lessons || [])].sort(compare),
  }))
}

export function lessonNavigation(modules, lessonId) {
  const lessons = orderCurriculum(modules).flatMap((module, moduleIndex) =>
    module.lessons.map((lesson, lessonIndex) => ({ lesson, module, moduleIndex, lessonIndex })),
  )
  const index = lessons.findIndex((entry) => entry.lesson.id === Number(lessonId))
  if (index < 0) return null
  return { ...lessons[index], previous: lessons[index - 1]?.lesson || null, next: lessons[index + 1]?.lesson || null }
}

export function lessonErrorKey(error) {
  const status = error.response?.status
  if (status === 401) return 'lessonWorkspace.signIn'
  if (status === 403) return 'lessonWorkspace.accessDenied'
  if (status === 404) return 'lessonWorkspace.notFound'
  return 'lessonWorkspace.loadError'
}

export async function loadEnrollmentProgress(client, slug) {
  const { data } = await client.get('/my/enrollments/')
  return data.find((enrollment) => enrollment.course.slug === slug) || null
}

export async function loadCourseOutline(client, slug, preview = false) {
  const path = preview ? `/instructor/courses/${encodeURIComponent(slug)}/preview/` : `/courses/${encodeURIComponent(slug)}/`
  const { data } = await client.get(path)
  return { course: { ...data, modules: orderCurriculum(data.modules) }, enrollment: null }
}

export function lessonCourseErrorKey(error, resource) {
  if (error?.response?.status === 401) return 'lessonWorkspace.signIn'
  if (error?.response?.status === 403) return 'lessonWorkspace.accessDenied'
  return resource === 'outline' ? 'lessonWorkspace.outlineError' : 'lessonWorkspace.progressError'
}

// Each resource publishes as soon as it settles. Retries retain confirmed data
// and only request that resource; disposal also guards React StrictMode/unmount.
export function loadLessonCourse(client, slug, preview, { onOutline, onProgress }) {
  let active = true
  const states = { outline: { data: null }, progress: { data: null } }
  const flights = {}
  function load(resource, read, publish) {
    if (!active) return Promise.resolve()
    if (flights[resource]) return flights[resource]
    states[resource] = { ...states[resource], loading: true, error: null }
    publish(states[resource])
    flights[resource] = Promise.resolve().then(() => active ? read() : undefined).then(data => {
      if (!active) return
      states[resource] = { data, loading: false, error: null }
      publish(states[resource])
    }).catch(error => {
      // The API client cancels responses from obsolete sessions. Never turn
      // those cancellations into empty course/progress data or visible errors.
      if (!active || error?.code === 'ERR_CANCELED') return
      const denied = [401, 403].includes(error?.response?.status)
      states[resource] = { ...states[resource], data: denied ? null : states[resource].data, loading: false, error }
      publish(states[resource])
    }).finally(() => { flights[resource] = null })
    return flights[resource]
  }
  const retryOutline = () => load('outline', async () => (await loadCourseOutline(client, slug, preview)).course, onOutline)
  const refreshProgress = () => preview ? Promise.resolve()
    : load('progress', () => loadEnrollmentProgress(client, slug), onProgress)
  const ready = Promise.allSettled([retryOutline(), refreshProgress()])
  return { ready, retryOutline, refreshProgress, dispose() { active = false } }
}

export async function saveLessonCompletion(client, lessonId) {
  const { data } = await client.post(`/lessons/${encodeURIComponent(lessonId)}/complete/`)
  // A successful HTTP response alone is not confirmation of this lesson's completion.
  if (Number(data.lesson_id) !== Number(lessonId) || typeof data.completed_at !== 'string' || !Number.isFinite(Date.parse(data.completed_at))) {
    throw new Error('Lesson completion was not confirmed')
  }
  return data.completed_at
}

// Hide only exact fallback table paragraphs when every cell is rendered natively.
export function lessonParagraphs(lesson) {
  const normalized = text => text.replace(/\s+/g, ' ').trim()
  const tables = new Set((lesson.learning_content?.interactions || []).filter(item => item.rows?.length).map(item =>
    normalized([...(item.headers?.length ? [item.headers] : []), ...item.rows].map(row => row.join(' | ')).join('\n')),
  ))
  return (lesson.text_content || '').split(/\n\s*\n/).filter(paragraph => !tables.has(normalized(paragraph)))
}
