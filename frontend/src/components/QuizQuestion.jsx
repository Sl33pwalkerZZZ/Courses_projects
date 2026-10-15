import { useTranslation } from 'react-i18next'
import { motion, useReducedMotion } from 'motion/react'

export default function QuizQuestion({ question, selected = [], number, total, onSelect, legendRef }) {
  const { t } = useTranslation()
  const reduced = useReducedMotion()
  const hintId = `quiz-question-hint-${question.id}`
  // Keep the legend mounted: the quiz controller moves keyboard focus here.
  // Animate only its text so changing questions cannot detach that focus target.
  return <fieldset className="quiz-question" aria-describedby={hintId}>
    <legend tabIndex={-1} ref={legendRef}>
      <span className="quiz-question-position">{t('quiz.questionPosition', { number, total })}</span>
      <motion.span key={question.id} className="quiz-question-text"
        initial={reduced ? false : { x: 8 }} animate={{ x: 0 }}
        transition={{ duration: reduced ? 0 : .18 }}>{question.text}</motion.span>
    </legend>
    <p className="quiz-choice-hint" id={hintId}>{t(question.type === 'single' ? 'quiz.chooseOne' : 'quiz.chooseMultiple')}</p>
    <div className="quiz-choices">
      {question.choices.map((choice) => <motion.label tabIndex={-1} whileTap={reduced ? undefined : { scale: 0.99 }} className={`quiz-choice${selected.includes(choice.id) ? ' is-selected' : ''}`} key={choice.id}>
        <input type={question.type === 'single' ? 'radio' : 'checkbox'} name={`quiz-question-${question.id}`}
          value={choice.id} checked={selected.includes(choice.id)} onChange={() => onSelect(choice.id)} />
        <span>{choice.text}</span>
      </motion.label>)}
    </div>
  </fieldset>
}
