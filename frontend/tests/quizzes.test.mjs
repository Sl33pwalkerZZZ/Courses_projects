import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createServer } from 'vite'
import { createQuizSubmission, loadLessonQuiz, loadQuizAttempt, loadQuizHistory, normalizeAttempt, normalizeQuiz, quizAnswers, quizErrorKey, selectQuizChoice } from '../src/utils/quizzes.js'

const quiz = {
  id: 3, lesson_id: 11, title: 'Authored quiz', instructions: 'Authored instructions', passing_percentage: 70,
  questions: [
    { id: 10, text: 'Authored single question', type: 'single', order: 1, choices: [{ id: 101, text: 'One', order: 1 }, { id: 102, text: 'Two', order: 2 }] },
    { id: 20, text: 'Authored multiple question', type: 'multiple', order: 2, choices: [{ id: 201, text: 'A', order: 1 }, { id: 202, text: 'B', order: 2 }, { id: 203, text: 'C', order: 3 }] },
  ],
}
const result = {
  id: 9, quiz_id: 3, score: 50, passed: false, correct_count: 1, question_count: 2, passing_percentage: 70,
  submitted_at: '2026-10-09T06:00:00Z', submission_id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  answers: quiz.questions.map((question, index) => ({ question_id: question.id, text: question.text, type: question.type,
    choices: question.choices, correct_choice_ids: index ? [201, 203] : [101], selected_choice_ids: index ? [201] : [101],
    is_correct: index === 0, explanation: `Authored explanation ${index + 1}` })),
}
const history = { count: 1, next: null, previous: null, latest: result, best: result, results: [result] }
let server, Question, Results, Confirmation, LoadState, HistoryPanel
const dictionaries = new Map()

before(async () => {
  server = await createServer({ server: { middlewareMode: true, hmr: false, ws: false }, optimizeDeps: { noDiscovery: true, include: [] }, appType: 'custom' })
  Question = (await server.ssrLoadModule('/src/components/QuizQuestion.jsx')).default
  Results = (await server.ssrLoadModule('/src/components/QuizResults.jsx')).default
  const lessonQuiz = await server.ssrLoadModule('/src/components/LessonQuiz.jsx')
  Confirmation = lessonQuiz.QuizConfirmation
  LoadState = lessonQuiz.QuizLoadState
  HistoryPanel = (await server.ssrLoadModule('/src/components/QuizAttemptHistory.jsx')).QuizHistoryPanel
  for (const language of ['en', 'ru', 'kk']) {
    const dictionary = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
    const instance = createInstance()
    await instance.init({ lng: language, resources: { [language]: { translation: dictionary } }, interpolation: { escapeValue: false } })
    dictionaries.set(language, instance)
  }
})
after(async () => { await server?.close() })

function render(Component, props, language = 'en') {
  return renderToStaticMarkup(createElement(I18nextProvider, { i18n: dictionaries.get(language) }, createElement(Component, props)))
}

test('an accessible lesson without a quiz returns null, not sample questions', async () => {
  const calls = []
  const loaded = await loadLessonQuiz({ get: async (path) => { calls.push(path); return { data: { quiz: null } } } }, 11)
  assert.equal(loaded, null)
  assert.deepEqual(calls, ['/lessons/11/quiz/'])
})

test('quiz loading preserves the authored question language and API ordering', async () => {
  assert.equal(await loadLessonQuiz({ get: async () => ({ data: { quiz } }) }, 11), quiz)
  assert.deepEqual(quiz.questions.map((question) => question.id), [10, 20])
  assert.equal(quiz.title, 'Authored quiz')
})

test('missing or malformed quiz responses are errors rather than no-quiz states', () => {
  for (const data of [null, {}, { quiz: {} }, { quiz: { ...quiz, lesson_id: 12 } },
    { quiz: { ...quiz, questions: [] } }, { quiz: { ...quiz, passing_percentage: 101 } },
    { quiz: { ...quiz, questions: [{ ...quiz.questions[0], type: 'essay' }] } },
    { quiz: { ...quiz, questions: [{ ...quiz.questions[0], choices: [quiz.questions[0].choices[0]] }] } },
  ]) assert.throws(() => normalizeQuiz(data, 11))
})

test('duplicate IDs and prematurely disclosed solution fields are rejected', () => {
  for (const questions of [[quiz.questions[0], quiz.questions[0]],
    [{ ...quiz.questions[0], explanation: 'Secret' }],
    [{ ...quiz.questions[0], choices: quiz.questions[0].choices.map((choice) => ({ ...choice, is_correct: true })) }],
    [{ ...quiz.questions[0], choices: [quiz.questions[0].choices[0], quiz.questions[0].choices[0]] }],
  ]) assert.throws(() => normalizeQuiz({ quiz: { ...quiz, questions } }, 11))
})

test('single-choice selection replaces the answer without mutating previous state', () => {
  const first = selectQuizChoice({}, quiz.questions[0], 101)
  const second = selectQuizChoice(first, quiz.questions[0], 102)
  assert.deepEqual(first, { 10: [101] })
  assert.deepEqual(second, { 10: [102] })
  assert.throws(() => selectQuizChoice(first, quiz.questions[0], 201))
})

test('multiple-select toggles individual choices and retains other questions', () => {
  const original = { 10: [101], 20: [201] }
  const selected = selectQuizChoice(original, quiz.questions[1], 203)
  assert.deepEqual(selected, { 10: [101], 20: [201, 203] })
  assert.deepEqual(selectQuizChoice(selected, quiz.questions[1], 201), { 10: [101], 20: [203] })
  assert.deepEqual(original, { 10: [101], 20: [201] })
})

test('submission answers contain only question IDs and selected choices, with no grading', () => {
  assert.deepEqual(quizAnswers(quiz, { 10: [102], 20: [203, 201] }), [
    { question_id: 10, choice_ids: [102] }, { question_id: 20, choice_ids: [201, 203] },
  ])
  assert.deepEqual(quizAnswers(quiz, {})[0].choice_ids, [])
})

test('simultaneous submission clicks share one request and never call lesson completion', async () => {
  let release
  const waiting = new Promise((resolve) => { release = resolve })
  const calls = []
  const submit = createQuizSubmission({ post: async (path, payload) => {
    calls.push({ path, payload }); await waiting; return { data: result }
  } }, 11, 3, () => result.submission_id)
  const first = submit(quizAnswers(quiz, { 10: [101], 20: [201] }))
  const second = submit(quizAnswers(quiz, { 10: [101], 20: [201] }))
  assert.equal(first, second)
  assert.equal(calls.length, 1)
  assert.equal(calls[0].path, '/lessons/11/quiz/attempts/')
  assert.equal(calls[0].payload.submission_id, result.submission_id)
  release()
  assert.equal(await first, result)
})

test('retry after a failed response reuses the same idempotency key', async () => {
  const keys = []
  let generated = 0
  const submit = createQuizSubmission({ post: async (_path, payload) => {
    keys.push(payload.submission_id)
    if (keys.length === 1) throw new Error('Response lost')
    return { data: result }
  } }, 11, 3, () => { generated++; return result.submission_id })
  const answers = quizAnswers(quiz, { 10: [101], 20: [201] })
  await assert.rejects(submit(answers))
  assert.equal(await submit(answers), result)
  assert.deepEqual(keys, [result.submission_id, result.submission_id])
  assert.equal(generated, 1)
})

test('an explicit new quiz attempt receives a fresh submission ID', async () => {
  const ids = []
  for (const id of [result.submission_id, 'bbee15d0-5c55-4f35-a486-b527e6cc9dc2']) {
    const submit = createQuizSubmission({ post: async (_path, payload) => {
      ids.push(payload.submission_id); return { data: { ...result, submission_id: payload.submission_id } }
    } }, 11, 3, () => id)
    await submit(quizAnswers(quiz, { 10: [101], 20: [201] }))
  }
  assert.equal(new Set(ids).size, 2)
})

test('failed or unconfirmed submissions cannot produce a results screen payload', async () => {
  for (const data of [{}, { ...result, quiz_id: 99 }, { ...result, submission_id: 'wrong' }, { ...result, answers: [] }]) {
    const submit = createQuizSubmission({ post: async () => ({ data }) }, 11, 3, () => result.submission_id)
    await assert.rejects(submit([]))
  }
})

test('result validation accepts backend scores and rejects invalid score or feedback shapes', () => {
  assert.equal(normalizeAttempt(result, 3, true), result)
  for (const data of [{ ...result, score: 101 }, { ...result, score: '50' }, { ...result, passed: 'yes' },
    { ...result, submitted_at: 'bad' }, { ...result, answers: null },
    { ...result, answers: result.answers.map((answer) => ({ ...answer, selected_choice_ids: [999] })) },
  ]) assert.throws(() => normalizeAttempt(data, 3, true))
})

test('history requests use only the current lesson and page and retain latest and best scores', async () => {
  let path
  const loaded = await loadQuizHistory({ get: async (value) => { path = value; return { data: history } } }, 11, 3, 2)
  assert.equal(path, '/lessons/11/quiz/attempts/?page=2')
  assert.equal(loaded.latest.score, 50)
  assert.equal(loaded.best.score, 50)
})

test('history errors can be retried without changing quiz answers', async () => {
  let calls = 0
  const client = { get: async () => { if (++calls === 1) throw new Error('Offline'); return { data: history } } }
  await assert.rejects(loadQuizHistory(client, 11, 3))
  assert.equal(await loadQuizHistory(client, 11, 3), history)
  const empty = { count: 0, next: null, previous: null, latest: null, best: null, results: [] }
  assert.equal(await loadQuizHistory({ get: async () => ({ data: empty }) }, 11, 3), empty)
  for (const data of [{}, { ...history, count: -1 }, { ...history, results: null }, { ...empty, best: result }]) {
    await assert.rejects(loadQuizHistory({ get: async () => ({ data }) }, 11, 3))
  }
})

test('previous attempt feedback is validated for the current quiz and selected attempt', async () => {
  let path
  assert.equal(await loadQuizAttempt({ get: async (value) => { path = value; return { data: result } } }, 9, 3), result)
  assert.equal(path, '/quiz-attempts/9/')
  await assert.rejects(loadQuizAttempt({ get: async () => ({ data: { ...result, id: 8 } }) }, 9, 3))
})

test('API authentication, access, unavailable and submission errors have localized keys', () => {
  for (const [status, key] of [[401, 'signIn'], [403, 'accessDenied'], [409, 'unavailable'], [400, 'invalidSubmission'], [500, 'submitError']]) {
    assert.equal(quizErrorKey({ response: { status } }, 'submit'), `quiz.${key}`)
  }
  assert.equal(quizErrorKey(new Error('Offline')), 'quiz.loadError')
})

test('single-choice questions render labelled radios sharing one question name', () => {
  const html = render(Question, { question: quiz.questions[0], selected: [102], number: 1, total: 2, onSelect: () => {} })
  assert.equal((html.match(/type="radio"/g) || []).length, 2)
  assert.equal((html.match(/checked=""/g) || []).length, 1)
  assert.equal((html.match(/name="quiz-question-10"/g) || []).length, 2)
  assert.match(html, /<fieldset/)
  assert.match(html, /<legend/)
  assert.match(html, /Question 1 of 2/)
  assert.match(html, /Choose one answer/)
  assert.doesNotMatch(html, /explanation|correct_choice_ids/)
})

test('multiple-select questions render checked boxes with exact-match instructions', () => {
  const html = render(Question, { question: quiz.questions[1], selected: [201, 203], number: 2, total: 2, onSelect: () => {} })
  assert.equal((html.match(/type="checkbox"/g) || []).length, 3)
  assert.equal((html.match(/checked=""/g) || []).length, 2)
  assert.match(html, /only for an exact match/)
})

test('authored question and feedback text is escaped instead of executed', () => {
  const html = render(Question, { question: { ...quiz.questions[0], text: '<script>alert(1)</script>' }, number: 1, total: 1, onSelect: () => {} })
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /<script/)
})

test('submit confirmation disables both actions while grading and shows independent completion', () => {
  const html = render(Confirmation, { total: 2, busy: true, onBack: () => {}, onSubmit: () => {} })
  assert.equal((html.match(/disabled=""/g) || []).length, 2)
  assert.match(html, /Grading answers/)
  assert.match(html, /completion is saved separately/)
  const failed = render(Confirmation, { total: 2, error: 'quiz.submitError', onBack: () => {}, onSubmit: () => {} })
  assert.match(failed, /role="alert"/)
  assert.doesNotMatch(failed, /quiz-results/)
})

test('loading and load errors offer retry without showing fake scores or questions', () => {
  const loading = render(LoadState, {})
  assert.match(loading, /role="status"/)
  const failed = render(LoadState, { error: 'quiz.loadError', onRetry: () => {} })
  assert.match(failed, /role="alert"/)
  assert.ok(failed.includes(dictionaries.get('en').t('common.retry')))
  assert.doesNotMatch(failed, /quiz-results|quiz-question/)
})

test('results show the server score, wrong and correct feedback, explanations and retry', () => {
  const html = render(Results, { result, onRetry: () => {} })
  assert.match(html, /50%/)
  assert.match(html, /Not passed yet/)
  assert.match(html, /Authored explanation 2/)
  assert.match(html, /Your answer/)
  assert.match(html, /Correct answer/)
  assert.match(html, /Try again/)
  assert.match(html, /role="status"/)
  const passed = render(Results, { result: { ...result, passed: true, score: 100 }, onRetry: () => {} })
  assert.match(passed, /is-passed/)
  assert.match(passed, /100%/)
})

test('history renders zero attempts, latest/best and read-only previous attempt actions', () => {
  const empty = render(HistoryPanel, { history: { count: 0 }, onRetry: () => {} })
  assert.match(empty, /No attempts yet/)
  assert.doesNotMatch(empty, /quiz-history-summary/)
  const loaded = render(HistoryPanel, { history, onView: () => {} })
  assert.match(loaded, /Latest score/)
  assert.match(loaded, /Best score/)
  assert.match(loaded, /Review attempt/)
  assert.match(loaded, /1 attempt/)
  const failed = render(HistoryPanel, { error: true, onRetry: () => {} })
  assert.match(failed, /role="alert"/)
})

for (const language of ['en', 'ru', 'kk']) {
  test(`question, confirmation, results, and history are localized in ${language}`, () => {
    const instance = dictionaries.get(language)
    const question = render(Question, { question: quiz.questions[1], number: 2, total: 2, onSelect: () => {} }, language)
    const confirmation = render(Confirmation, { total: 2, onSubmit: () => {}, onBack: () => {} }, language)
    const results = render(Results, { result, onRetry: () => {} }, language)
    const attempts = render(HistoryPanel, { history, onView: () => {} }, language)
    assert.ok(question.includes(instance.t('quiz.chooseMultiple')))
    assert.ok(confirmation.includes(instance.t('quiz.confirmTitle')))
    assert.ok(results.includes(instance.t('quiz.notPassed')))
    assert.ok(attempts.includes(instance.t('quiz.history')))
    assert.ok(question.includes('Authored multiple question'))
    assert.doesNotMatch(question + confirmation + results + attempts, /quiz\.[a-zA-Z]/)
  })
}

test('Russian attempt counts and confirmation questions use the proper plural forms', () => {
  const instance = dictionaries.get('ru')
  for (const [count, expected] of [[1, '1 попытка'], [2, '2 попытки'], [5, '5 попыток'], [21, '21 попытка']]) {
    assert.equal(instance.t('quiz.attemptCount', { count }), expected)
  }
  assert.match(instance.t('quiz.confirmDescription', { count: 2 }), /2 вопроса/)
})
