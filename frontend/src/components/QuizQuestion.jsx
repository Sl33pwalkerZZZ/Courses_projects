import { useTranslation } from 'react-i18next'

export default function QuizQuestion({ question, selected = [], number, total, onSelect, legendRef }) {
  const { t } = useTranslation()
  const hintId = `quiz-question-hint-${question.id}`
  return <fieldset className="quiz-question" aria-describedby={hintId}>
    <legend tabIndex={-1} ref={legendRef}>
      <span className="quiz-question-position">{t('quiz.questionPosition', { number, total })}</span>
      <span className="quiz-question-text">{question.text}</span>
    </legend>
    <p className="quiz-choice-hint" id={hintId}>{t(question.type === 'single' ? 'quiz.chooseOne' : 'quiz.chooseMultiple')}</p>
    <div className="quiz-choices">
      {question.choices.map((choice) => <label className={`quiz-choice${selected.includes(choice.id) ? ' is-selected' : ''}`} key={choice.id}>
        <input type={question.type === 'single' ? 'radio' : 'checkbox'} name={`quiz-question-${question.id}`}
          value={choice.id} checked={selected.includes(choice.id)} onChange={() => onSelect(choice.id)} />
        <span>{choice.text}</span>
      </label>)}
    </div>
  </fieldset>
}
