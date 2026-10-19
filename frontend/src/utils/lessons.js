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
  if (preview) {
    const { data } = await client.get(`/instructor/courses/${encodeURIComponent(slug)}/preview/`)
    return { course: { ...data, modules: orderCurriculum(data.modules) }, enrollment: null }
  }
  const [response, enrollment] = await Promise.all([
    client.get(`/courses/${encodeURIComponent(slug)}/`), loadEnrollmentProgress(client, slug),
  ])
  return { course: { ...response.data, modules: orderCurriculum(response.data.modules) }, enrollment }
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
