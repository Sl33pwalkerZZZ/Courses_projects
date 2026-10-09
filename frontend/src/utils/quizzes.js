function validId(value) {
  return Number.isSafeInteger(value) && value > 0
}

function uniqueIds(values) {
  return Array.isArray(values) && values.every(validId) && new Set(values).size === values.length
}

export function normalizeQuiz(data, lessonId) {
  if (data?.quiz === null) return null
  const quiz = data?.quiz
  if (!quiz || !validId(quiz.id) || quiz.lesson_id !== Number(lessonId) || typeof quiz.title !== 'string'
    || typeof quiz.instructions !== 'string' || !Number.isInteger(quiz.passing_percentage)
    || quiz.passing_percentage < 0 || quiz.passing_percentage > 100 || !Array.isArray(quiz.questions) || !quiz.questions.length) {
    throw new Error('Invalid quiz response')
  }
  const questionIds = [], choiceIds = []
  for (const question of quiz.questions) {
    if (!validId(question.id) || typeof question.text !== 'string' || !question.text.trim()
      || !['single', 'multiple'].includes(question.type) || !Array.isArray(question.choices) || question.choices.length < 2
      || 'explanation' in question || 'correct_choice_ids' in question) throw new Error('Invalid quiz question')
    questionIds.push(question.id)
    for (const choice of question.choices) {
      if (!validId(choice.id) || typeof choice.text !== 'string' || !choice.text.trim() || 'is_correct' in choice) throw new Error('Invalid quiz choice')
      choiceIds.push(choice.id)
    }
  }
  if (!uniqueIds(questionIds) || !uniqueIds(choiceIds)) throw new Error('Duplicate quiz IDs')
  return quiz
}

export function normalizeAttempt(data, quizId, withAnswers = false) {
  if (!data || !validId(data.id) || data.quiz_id !== quizId || typeof data.score !== 'number'
    || !Number.isFinite(data.score) || data.score < 0 || data.score > 100 || typeof data.passed !== 'boolean'
    || !Number.isInteger(data.question_count) || data.question_count < 1 || !Number.isInteger(data.correct_count)
    || data.correct_count < 0 || data.correct_count > data.question_count || !Number.isInteger(data.passing_percentage)
    || data.passing_percentage < 0 || data.passing_percentage > 100
    || typeof data.submitted_at !== 'string' || !Number.isFinite(Date.parse(data.submitted_at))) {
    throw new Error('Invalid quiz result')
  }
  if (withAnswers) {
    if (!Array.isArray(data.answers) || data.answers.length !== data.question_count) throw new Error('Missing quiz feedback')
    for (const answer of data.answers) {
      if (!validId(answer.question_id) || typeof answer.text !== 'string' || !['single', 'multiple'].includes(answer.type)
        || typeof answer.is_correct !== 'boolean' || typeof answer.explanation !== 'string' || !Array.isArray(answer.choices)
        || !uniqueIds(answer.selected_choice_ids) || !uniqueIds(answer.correct_choice_ids)) throw new Error('Invalid quiz feedback')
      const ids = answer.choices.map((choice) => choice.id)
      if (!uniqueIds(ids) || answer.choices.some((choice) => typeof choice.text !== 'string')
        || [...answer.selected_choice_ids, ...answer.correct_choice_ids].some((id) => !ids.includes(id))) throw new Error('Invalid feedback choices')
    }
    if (!uniqueIds(data.answers.map((answer) => answer.question_id))) throw new Error('Duplicate feedback questions')
  }
  return data
}

export async function loadLessonQuiz(client, lessonId) {
  const { data } = await client.get(`/lessons/${encodeURIComponent(lessonId)}/quiz/`)
  return normalizeQuiz(data, lessonId)
}

export async function loadQuizHistory(client, lessonId, quizId, page = 1) {
  const { data } = await client.get(`/lessons/${encodeURIComponent(lessonId)}/quiz/attempts/?page=${page}`)
  if (!data || !Number.isSafeInteger(data.count) || data.count < 0 || !Array.isArray(data.results)
    || data.results.length > 10 || ![data.next, data.previous].every((value) => value === null || typeof value === 'string')) {
    throw new Error('Invalid attempt history')
  }
  data.results.forEach((attempt) => normalizeAttempt(attempt, quizId))
  if (data.count) {
    normalizeAttempt(data.latest, quizId)
    normalizeAttempt(data.best, quizId)
  } else if (data.latest !== null || data.best !== null || data.results.length) throw new Error('Invalid empty history')
  return data
}

export async function loadQuizAttempt(client, attemptId, quizId) {
  const { data } = await client.get(`/quiz-attempts/${encodeURIComponent(attemptId)}/`)
  if (data?.id !== attemptId) throw new Error('Incorrect attempt response')
  return normalizeAttempt(data, quizId, true)
}

export function selectQuizChoice(selections, question, choiceId) {
  if (!question.choices.some((choice) => choice.id === choiceId)) throw new Error('Unknown choice')
  const selected = selections[question.id] || []
  return { ...selections, [question.id]: question.type === 'single' ? [choiceId]
    : selected.includes(choiceId) ? selected.filter((id) => id !== choiceId) : [...selected, choiceId] }
}

export function quizAnswers(quiz, selections) {
  return quiz.questions.map((question) => ({ question_id: question.id, choice_ids: [...(selections[question.id] || [])].sort((a, b) => a - b) }))
}

export function createQuizSubmission(client, lessonId, quizId, makeId = () => crypto.randomUUID()) {
  let inFlight = null
  let pending = null
  return (answers) => {
    if (inFlight) return inFlight
    const fingerprint = JSON.stringify(answers)
    if (!pending || pending.fingerprint !== fingerprint) pending = { fingerprint, id: makeId() }
    const payload = { submission_id: pending.id, answers }
    // Keep the same ID after a network failure: the server may already have saved it.
    inFlight = client.post(`/lessons/${encodeURIComponent(lessonId)}/quiz/attempts/`, payload)
      .then(({ data }) => {
        if (data.submission_id !== payload.submission_id) throw new Error('Submission was not confirmed')
        return normalizeAttempt(data, quizId, true)
      }).finally(() => { inFlight = null })
    return inFlight
  }
}

export function quizErrorKey(error, action = 'load') {
  if (error.response?.status === 401) return 'quiz.signIn'
  if (error.response?.status === 403) return 'quiz.accessDenied'
  if (error.response?.status === 409) return 'quiz.unavailable'
  if (action === 'submit' && error.response?.status === 400) return 'quiz.invalidSubmission'
  return action === 'submit' ? 'quiz.submitError' : 'quiz.loadError'
}
