// Shared, framework-independent validation and ordering helpers for Studio.
export function studioList(value) { return Array.isArray(value) ? value : value?.results || [] }
export function moveStudioItem(items, index, direction) {
  const next = [...items], destination = index + direction
  if (index < 0 || destination < 0 || destination >= next.length) return next
  ;[next[index], next[destination]] = [next[destination], next[index]]
  return next
}
export function studioError(error, fallback, translate) {
  if (!error?.response?.data) return fallback
  const missing = publicationProblems(error.response.data)
  if (missing.length && translate) return missing.map(item => translate(`instructorStudio.requirements.${item.key}`, { defaultValue: item.label || item.key })).join(' · ')
  const values = []
  function visit(value, path = '') {
    if (typeof value === 'string') values.push(path ? `${path}: ${value}` : value)
    else if (Array.isArray(value)) value.forEach((item, i) => visit(item, typeof item === 'object' ? `${path} ${i + 1}` : path))
    else if (value && typeof value === 'object') Object.entries(value).forEach(([key, item]) => visit(item, key === 'detail' ? path : `${path} ${key}`.trim()))
  }
  visit(error.response.data)
  return values.join(' · ') || fallback
}
export function newStudioQuestion() {
  return { text: '', type: 'single', explanation: '', choices: [{ text: '', is_correct: false }, { text: '', is_correct: false }] }
}
export function quizProblems(quiz) {
  const problems = []
  if (!quiz.title?.trim()) problems.push('title')
  if (!Number.isFinite(Number(quiz.passing_percentage)) || Number(quiz.passing_percentage) < 0 || Number(quiz.passing_percentage) > 100) problems.push('passing')
  if (!quiz.questions?.length) problems.push('questions')
  quiz.questions?.forEach((q, i) => {
    if (!q.text?.trim() || !['single', 'multiple'].includes(q.type) || q.choices.length < 2 || q.choices.some(c => !c.text?.trim())) problems.push(`question ${i + 1}`)
    const correct = q.choices.filter(c => c.is_correct).length
    if (q.type === 'single' ? correct !== 1 : correct < 1) problems.push(`answers ${i + 1}`)
  })
  return problems
}

// Render structured publication validation as meaningful localized checklist text.
// DRF wraps error leaf values as strings, including the requirement's key.
export function publicationProblems(data) {
  return Array.isArray(data?.requirements) ? data.requirements.filter(item => item && typeof item === 'object' && item.key && item.met !== true && item.met !== 'True') : []
}
export function teachingEntryChange(entry, text) {
  if (typeof entry === 'string') return text
  const field = ['text', 'description', 'body'].find(key => Object.hasOwn(entry, key)) || 'text'
  return { ...entry, [field]: text }
}
export function prepareLearningContent(content) {
  return { ...content, objectives: (content.objectives || []).map(text => text.trim()).filter(Boolean) }
}
