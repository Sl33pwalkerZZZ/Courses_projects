import { useTranslation } from 'react-i18next'
import { CircleCheck, CircleX } from 'lucide-react'

export default function QuizResults({ result, onRetry, headingRef }) {
  const { t, i18n } = useTranslation()
  const percent = new Intl.NumberFormat(i18n.resolvedLanguage, { style: 'percent', maximumFractionDigits: 2 })
  return <div className="quiz-results">
    <div className={`quiz-score-card${result.passed ? ' is-passed' : ''}`} role="status">
      <div><h3 tabIndex={-1} ref={headingRef}>{t('quiz.results')}</h3>
        <p>{t(result.passed ? 'quiz.passed' : 'quiz.notPassed')}</p>
        <p>{t('quiz.correctSummary', { correct: result.correct_count, total: result.question_count })}</p>
        <p>{t('quiz.passingScore', { score: percent.format(result.passing_percentage / 100) })}</p></div>
      <strong className="quiz-score">{percent.format(result.score / 100)}</strong>
    </div>
    <ol className="quiz-feedback">
      {result.answers.map((answer) => <li className="quiz-feedback-question" key={answer.question_id}>
        <div className="quiz-feedback-heading">
          {answer.is_correct ? <CircleCheck size={19} aria-hidden="true" /> : <CircleX size={19} aria-hidden="true" />}
          <h4>{answer.text}</h4><span>{t(answer.is_correct ? 'quiz.correct' : 'quiz.incorrect')}</span>
        </div>
        <ul className="quiz-feedback-choices">
          {answer.choices.map((choice) => {
            const correct = answer.correct_choice_ids.includes(choice.id)
            const selected = answer.selected_choice_ids.includes(choice.id)
            return <li key={choice.id} className={`${correct ? 'is-correct' : ''}${selected ? ' is-selected' : ''}`}>
              <span>{choice.text}</span><span className="quiz-feedback-labels">
                {selected && <span>{t('quiz.yourAnswer')}</span>}{correct && <span>{t('quiz.correctAnswer')}</span>}
              </span>
            </li>
          })}
        </ul>
        {answer.explanation && <p className="quiz-explanation"><strong>{t('quiz.explanation')}</strong> {answer.explanation}</p>}
      </li>)}
    </ol>
    <button className="academic-button" type="button" onClick={onRetry}>{t('quiz.tryAgain')}</button>
  </div>
}
