import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { BookOpenCheck, Check } from 'lucide-react'
import api from '../api'
import { createQuizSubmission, loadLessonQuiz, quizAnswers, quizErrorKey, selectQuizChoice } from '../utils/quizzes'
import QuizQuestion from './QuizQuestion'
import QuizResults from './QuizResults'
import QuizAttemptHistory from './QuizAttemptHistory'
import './LessonQuiz.css'

export function QuizLoadState({ error, onRetry }) {
  const { t } = useTranslation()
  return <section className="lesson-quiz quiz-load-state" aria-label={t('quiz.knowledgeCheck')} aria-busy={!error}>
    {error ? <div className="quiz-error" role="alert"><p>{t(error)}</p>
      <button className="lesson-text-button" type="button" onClick={onRetry}>{t('common.retry')}</button></div>
      : <p role="status">{t('quiz.loading')}</p>}
  </section>
}

export function QuizConfirmation({ total, busy, error, onBack, onSubmit, headingRef }) {
  const { t } = useTranslation()
  return <form className="quiz-confirmation" onSubmit={onSubmit} aria-busy={busy}>
    <h3 tabIndex={-1} ref={headingRef}>{t('quiz.confirmTitle')}</h3>
    <p>{t('quiz.confirmDescription', { count: total })}</p>
    <p>{t('quiz.independentCompletion')}</p>
    {error && <p className="quiz-error" role="alert">{t(error)}</p>}
    <div className="quiz-actions">
      <button className="lesson-text-button" type="button" disabled={busy} onClick={onBack}>{t('quiz.backToAnswers')}</button>
      <button className="academic-button" type="submit" disabled={busy}>{t(busy ? 'quiz.submitting' : 'quiz.submit')}</button>
    </div>
  </form>
}

function QuizSession({ quiz, lessonId }) {
  const { t, i18n } = useTranslation()
  const [selections, setSelections] = useState({})
  const [index, setIndex] = useState(0)
  const [phase, setPhase] = useState('answering')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [historyVersion, setHistoryVersion] = useState(0)
  const submissionRef = useRef(null)
  const busyRef = useRef(false)
  const activeRef = useRef(true)
  const headingRef = useRef(null)
  const focusRequested = useRef(false)
  const question = quiz.questions[index]
  const answered = quiz.questions.filter((item) => selections[item.id]?.length).length
  const percent = new Intl.NumberFormat(i18n.resolvedLanguage, { style: 'percent', maximumFractionDigits: 0 })

  useEffect(() => { activeRef.current = true; return () => { activeRef.current = false } }, [])
  useEffect(() => {
    if (focusRequested.current) { headingRef.current?.focus(); focusRequested.current = false }
  }, [index, phase, result])

  function navigate(next) {
    focusRequested.current = true
    setIndex(next)
  }

  function reviewAnswers() {
    if (answered !== quiz.questions.length) {
      setError('quiz.answerAll')
      navigate(quiz.questions.findIndex((item) => !selections[item.id]?.length))
      return
    }
    setError('')
    focusRequested.current = true
    setPhase('confirming')
  }

  async function submit(event) {
    event.preventDefault()
    if (busyRef.current) return
    busyRef.current = true
    setBusy(true)
    setError('')
    if (!submissionRef.current) submissionRef.current = createQuizSubmission(api, lessonId, quiz.id)
    try {
      const saved = await submissionRef.current(quizAnswers(quiz, selections))
      if (!activeRef.current) return
      setResult(saved)
      focusRequested.current = true
      setPhase('results')
      setHistoryVersion((value) => value + 1)
    } catch (failure) {
      if (activeRef.current) setError(quizErrorKey(failure, 'submit'))
    } finally {
      busyRef.current = false
      if (activeRef.current) setBusy(false)
    }
  }

  function tryAgain() {
    submissionRef.current = null
    setSelections({})
    setIndex(0)
    setResult(null)
    setError('')
    focusRequested.current = true
    setPhase('answering')
  }

  return <section className="lesson-quiz" aria-labelledby="lesson-quiz-title">
    <header className="quiz-header"><div><p className="eyebrow">{t('quiz.knowledgeCheck')}</p>
      <h2 id="lesson-quiz-title">{quiz.title}</h2></div><BookOpenCheck size={25} strokeWidth={1.4} aria-hidden="true" /></header>
    {quiz.instructions && <p className="quiz-instructions">{quiz.instructions}</p>}
    <p className="quiz-independent-note">{t('quiz.independentCompletion')}</p>
    {phase === 'results' ? <QuizResults result={result} onRetry={tryAgain} headingRef={headingRef} />
      : phase === 'confirming' ? <QuizConfirmation total={quiz.questions.length} busy={busy} error={error} headingRef={headingRef}
        onBack={() => { focusRequested.current = true; setPhase('answering'); setError('') }} onSubmit={submit} /> : <>
        <div className="quiz-progress"><div><span>{t('quiz.answeredProgress', { answered, total: quiz.questions.length })}</span>
          <span>{t('quiz.passingScore', { score: percent.format(quiz.passing_percentage / 100) })}</span></div>
          <progress max={quiz.questions.length} value={answered} aria-label={t('quiz.progressLabel')} /></div>
        <nav className="quiz-question-navigation" aria-label={t('quiz.questionNavigation')}>
          {quiz.questions.map((item, position) => <button key={item.id} type="button" onClick={() => navigate(position)}
            aria-current={position === index ? 'step' : undefined} aria-label={t('quiz.questionNavLabel', {
              number: position + 1, status: t(selections[item.id]?.length ? 'quiz.answered' : 'quiz.unanswered'),
            })}>{position + 1}{selections[item.id]?.length > 0 && <Check size={12} aria-hidden="true" />}</button>)}
        </nav>
        <QuizQuestion question={question} selected={selections[question.id]} number={index + 1} total={quiz.questions.length} legendRef={headingRef}
          onSelect={(choiceId) => { setSelections((current) => selectQuizChoice(current, question, choiceId)); setError('') }} />
        {error && <p className="quiz-error" role="alert">{t(error)}</p>}
        <div className="quiz-actions"><div className="quiz-step-actions">
          <button className="lesson-text-button" type="button" disabled={index === 0} onClick={() => navigate(index - 1)}>{t('quiz.previous')}</button>
          <button className="lesson-text-button" type="button" disabled={index === quiz.questions.length - 1} onClick={() => navigate(index + 1)}>{t('quiz.next')}</button>
        </div><button className="academic-button" type="button" onClick={reviewAnswers}>{t('quiz.reviewAnswers')}</button></div>
      </>}
    <QuizAttemptHistory key={historyVersion} lessonId={lessonId} quizId={quiz.id} disabled={busy}
      onView={(saved) => {
        // A history request started earlier must not replace a pending submission.
        if (busyRef.current) return
        setResult(saved)
        focusRequested.current = true
        setPhase('results')
        setError('')
      }} />
  </section>
}

export default function LessonQuiz({ lessonId }) {
  const [quiz, setQuiz] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [retry, setRetry] = useState(0)

  useEffect(() => {
    let active = true
    loadLessonQuiz(api, lessonId).then((data) => { if (active) setQuiz(data) })
      .catch((failure) => { if (active) setError(quizErrorKey(failure)) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [lessonId, retry])

  if (loading || error) return <QuizLoadState error={error} onRetry={() => { setLoading(true); setError(''); setRetry((value) => value + 1) }} />
  return quiz ? <QuizSession key={quiz.id} quiz={quiz} lessonId={lessonId} /> : null
}
