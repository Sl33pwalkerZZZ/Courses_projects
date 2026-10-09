import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../api'
import { loadQuizAttempt, loadQuizHistory } from '../utils/quizzes'

export function QuizHistoryPanel({ history, loading, error, viewing, viewError, onRetry, onView, onPage }) {
  const { t, i18n } = useTranslation()
  const percent = new Intl.NumberFormat(i18n.resolvedLanguage, { style: 'percent', maximumFractionDigits: 2 })
  const date = new Intl.DateTimeFormat(i18n.resolvedLanguage, { dateStyle: 'medium', timeStyle: 'short' })
  return <section className="quiz-history" aria-labelledby="quiz-history-title" aria-busy={loading}>
    <h3 id="quiz-history-title">{t('quiz.history')}</h3>
    {error ? <div className="quiz-error" role="alert"><p>{t('quiz.historyError')}</p>
      <button className="lesson-text-button" type="button" onClick={onRetry}>{t('common.retry')}</button></div>
      : loading || !history ? <p role="status">{t('common.loading')}</p>
        : !history.count ? <p>{t('quiz.noAttempts')}</p> : <>
          <dl className="quiz-history-summary">
            <div><dt>{t('quiz.latestScore')}</dt><dd>{percent.format(history.latest.score / 100)}</dd></div>
            <div><dt>{t('quiz.bestScore')}</dt><dd>{percent.format(history.best.score / 100)}</dd></div>
          </dl>
          <p>{t('quiz.attemptCount', { count: history.count })}</p>
          <ol className="quiz-attempt-list">
            {history.results.map((attempt) => <li key={attempt.id}>
              <div><time dateTime={attempt.submitted_at}>{date.format(new Date(attempt.submitted_at))}</time>
                <span>{percent.format(attempt.score / 100)} · {t(attempt.passed ? 'quiz.passed' : 'quiz.notPassed')}</span></div>
              <button className="lesson-text-button" type="button" onClick={() => onView(attempt.id)} disabled={viewing !== null && viewing !== undefined}>
                {t(viewing === attempt.id ? 'common.loading' : 'quiz.viewAttempt')}
              </button>
            </li>)}
          </ol>
          {(history.previous || history.next) && <nav className="quiz-history-pagination" aria-label={t('quiz.historyPagination')}>
            <button className="lesson-text-button" type="button" disabled={!history.previous} onClick={() => onPage(-1)}>{t('quiz.previous')}</button>
            <button className="lesson-text-button" type="button" disabled={!history.next} onClick={() => onPage(1)}>{t('quiz.next')}</button>
          </nav>}
        </>}
    {viewError && <p className="quiz-error" role="alert">{t('quiz.historyError')}</p>}
  </section>
}

export default function QuizAttemptHistory({ lessonId, quizId, onView, disabled }) {
  const [history, setHistory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [viewError, setViewError] = useState(false)
  const [viewing, setViewing] = useState(null)
  const [page, setPage] = useState(1)
  const [retry, setRetry] = useState(0)
  const activeRef = useRef(true)
  const viewingRef = useRef(false)

  useEffect(() => { activeRef.current = true; return () => { activeRef.current = false } }, [])
  useEffect(() => {
    let active = true
    loadQuizHistory(api, lessonId, quizId, page).then((data) => { if (active) setHistory(data) })
      .catch(() => { if (active) setError(true) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [lessonId, quizId, page, retry])

  async function viewAttempt(id) {
    if (disabled || viewingRef.current) return
    viewingRef.current = true
    setViewing(id)
    setViewError(false)
    try {
      const result = await loadQuizAttempt(api, id, quizId)
      if (activeRef.current) onView(result)
    } catch {
      if (activeRef.current) setViewError(true)
    } finally {
      viewingRef.current = false
      if (activeRef.current) setViewing(null)
    }
  }

  function refresh(direction) {
    setError(false)
    setLoading(true)
    if (direction) setPage((current) => current + direction)
    else setRetry((current) => current + 1)
  }

  return <QuizHistoryPanel history={history} loading={loading} error={error} viewing={disabled ? -1 : viewing}
    viewError={viewError} onRetry={() => refresh()} onPage={refresh} onView={viewAttempt} />
}
