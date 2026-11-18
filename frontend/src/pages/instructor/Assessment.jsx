import { useId, useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../../api'
import Button from '../../components/ui/Button'
import { Input, Select, Notice, ResourceState } from '../../components/instructor/StudioShared'
import { useStudioAction, useStudioResource } from '../../components/instructor/useStudio'
import AssignmentInstructions, { AssignmentRubric } from '../../components/learning/AssignmentInstructions'
import { LessonPicker } from './Curriculum'
import { moveStudioItem, newStudioQuestion, quizProblems, studioList } from '../../utils/instructorStudio'

export default function Assessment() {
  const { course } = useOutletContext(), { t } = useTranslation()
  const [lesson, setLesson] = useState('')
  return <><h3>{t('instructorStudio.assessment')}</h3><LessonPicker course={course} value={lesson} onChange={setLesson} />{lesson && <LessonAssessments key={lesson} lesson={lesson} courseLocked={course.is_published} />}</>
}
export function LessonAssessments({ lesson, courseLocked }) {
  const { t } = useTranslation()
  const resource = useStudioResource(`/studio/lessons/${lesson}/quiz/`, { retainData: true })
  return <><ResourceState resource={resource}>{data => <QuizEditor courseLocked={courseLocked} key={data?.id || 'new'} lesson={lesson} initial={data?.quiz === null ? null : data?.quiz || data} onSaved={resource.reload} />}</ResourceState><AssignmentManager locked={courseLocked} lesson={lesson} /><p className="instructor-note">{t('instructorStudio.answerPrivacy')}</p></>
}
export function QuizEditor({ lesson, initial, onSaved, courseLocked }) {
  const { t } = useTranslation(), action = useStudioAction(), editorId = useId()
  const [quiz, setQuiz] = useState(() => ({ title: initial?.title || '', instructions: initial?.instructions || '', passing_percentage: initial?.passing_percentage ?? 70, questions: initial?.questions || [] }))
  const [localError, setLocalError] = useState(''), [preview, setPreview] = useState(false)
  const locked = Boolean(courseLocked || initial?.locked || initial?.is_published || initial?.has_attempts || initial?.attempt_count)
  const questionChange = (index, update) => setQuiz(current => ({ ...current, questions: current.questions.map((question, i) => i === index ? { ...question, ...update } : question) }))
  return <section className="instructor-panel"><h3>{t('instructorStudio.quiz')}</h3>{locked && <p role="note">{t('instructorStudio.quizLocked')}</p>}<p className="instructor-note">{t('instructorStudio.quizAuthoring.answerPolicy')}</p><form className="instructor-form" onSubmit={event => { event.preventDefault(); if (locked || action.busy) return; if (quizProblems(quiz).length) { setLocalError(t(quizProblems(quiz).includes('passing') ? 'instructorStudio.quizAuthoring.invalidPassing' : 'instructorStudio.quizInvalid')); return } setLocalError(''); action.run(signal => api.put(`/studio/lessons/${lesson}/quiz/`, { ...quiz, passing_percentage: Number(quiz.passing_percentage), questions: quiz.questions.map(q => ({ text: q.text, type: q.type, explanation: q.explanation || '', choices: q.choices.map(c => ({ text: c.text, is_correct: c.is_correct })) })) }, { signal }), onSaved) }}><fieldset disabled={locked || action.busy}><legend>{t('instructorStudio.quizSettings')}</legend><Input label={t('instructorStudio.quizTitle')} value={quiz.title} required onChange={event => setQuiz({ ...quiz, title: event.target.value })} /><Input multiline label={t('instructorStudio.instructions')} value={quiz.instructions} onChange={event => setQuiz({ ...quiz, instructions: event.target.value })} /><Input label={t('instructorStudio.passing')} type="number" min={0} max={100} step={1} required value={quiz.passing_percentage} onChange={event => setQuiz({ ...quiz, passing_percentage: event.target.value })} />{quiz.questions.map((question, index) => <fieldset key={index}><legend>{t('instructorStudio.question')} {index + 1}</legend><Input multiline label={t('instructorStudio.questionText')} required value={question.text} onChange={event => questionChange(index, { text: event.target.value })} /><Select label={t('instructorStudio.questionType')} value={question.type} options={['single', 'multiple'].map(value => ({ value, label: t(`instructorStudio.${value}`) }))} onChange={event => questionChange(index, { type: event.target.value, choices: question.choices.map(choice => ({ ...choice, is_correct: false })) })} /><p>{t(`instructorStudio.quizAuthoring.${question.type}`)}</p>{question.choices.map((choice, choiceIndex) => <div className="instructor-choice" key={choiceIndex}><Input label={`${t('instructorStudio.choice')} ${choiceIndex + 1}`} value={choice.text} required onChange={event => questionChange(index, { choices: question.choices.map((item, i) => i === choiceIndex ? { ...item, text: event.target.value } : item) })} /><label className="instructor-check"><input type={question.type === 'single' ? 'radio' : 'checkbox'} name={`${editorId}-correct-${index}`} checked={choice.is_correct} onChange={event => questionChange(index, { choices: question.choices.map((item, i) => ({ ...item, is_correct: i === choiceIndex ? event.target.checked : question.type === 'single' ? false : item.is_correct })) })} />{t('instructorStudio.correct')} {choiceIndex + 1}</label><Button variant="ghost" disabled={question.choices.length <= 2} aria-label={`${t('instructorStudio.removeChoice')} ${choiceIndex + 1}`} onClick={() => questionChange(index, { choices: question.choices.filter((_, i) => i !== choiceIndex) })}>×</Button></div>)}<Button variant="secondary" disabled={question.choices.length >= 20} onClick={() => questionChange(index, { choices: [...question.choices, { text: '', is_correct: false }] })}>{t('instructorStudio.addChoice')}</Button><Input multiline label={t('instructorStudio.explanation')} value={question.explanation || ''} onChange={event => questionChange(index, { explanation: event.target.value })} /><div className="instructor-actions"><Button variant="ghost" disabled={index === 0} aria-label={`${t('instructorStudio.up')}: ${t('instructorStudio.question')} ${index + 1}`} onClick={() => setQuiz({ ...quiz, questions: moveStudioItem(quiz.questions, index, -1) })}>↑</Button><Button variant="ghost" disabled={index === quiz.questions.length - 1} aria-label={`${t('instructorStudio.down')}: ${t('instructorStudio.question')} ${index + 1}`} onClick={() => setQuiz({ ...quiz, questions: moveStudioItem(quiz.questions, index, 1) })}>↓</Button><Button variant="ghost" onClick={() => { if (window.confirm(t('instructorStudio.removeQuestionConfirm'))) setQuiz({ ...quiz, questions: quiz.questions.filter((_, i) => i !== index) }) }}>{t('instructorStudio.removeQuestion')}</Button></div></fieldset>)}<Button variant="secondary" disabled={quiz.questions.length >= 100} onClick={() => setQuiz({ ...quiz, questions: [...quiz.questions, newStudioQuestion()] })}>{t('instructorStudio.addQuestion')}</Button></fieldset><Notice error={localError || action.error} message={action.message} /><div className="instructor-actions"><Button type="submit" disabled={locked || action.busy}>{t('instructorStudio.saveDraft')}</Button><Button variant="secondary" aria-expanded={preview} onClick={() => setPreview(!preview)}>{t('instructorStudio.previewQuestions')}</Button></div></form>{preview && <section aria-label={t('instructorStudio.previewQuestions')}>{quiz.questions.map((question, i) => <article key={i}><h4>{i + 1}. {question.text}</h4><ul>{question.choices.map((choice, j) => <li key={j}>{choice.text}{choice.is_correct && <strong> — {t('instructorStudio.correct')}</strong>}</li>)}</ul><p>{question.explanation}</p></article>)}</section>}</section>
}
export function AssignmentManager({ lesson, locked }) {
  const resource = useStudioResource(`/studio/lessons/${lesson}/assignments/`, { retainData: true }), { t } = useTranslation()
  return <section className="instructor-panel"><h3>{t('instructorStudio.assignments')}</h3><ResourceState resource={resource}>{data => <>{studioList(data).map(item => <AssignmentForm locked={locked} key={item.id} lesson={lesson} initial={item} onSaved={resource.reload} />)}<details><summary>{t('instructorStudio.addAssignment')}</summary><AssignmentForm locked={locked} lesson={lesson} onSaved={resource.reload} /></details></>}</ResourceState></section>
}
export function AssignmentForm({ lesson, initial, onSaved, locked }) {
  const { t } = useTranslation(), action = useStudioAction(), id = useId()
  const empty = () => ({ type: 'text', description: '', learning_activity: '' })
  const [form, setForm] = useState(() => initial ? { type: initial.type, description: initial.description, learning_activity: initial.learning_activity || '' } : empty())
  const [preview, setPreview] = useState(false), [invalid, setInvalid] = useState(false)
  const specialized = form.learning_activity === 'ai_selection_map'
  const finalProject = form.learning_activity === 'final_media_project'
  return <div className="instructor-assignment-editor"><form className="instructor-form" onSubmit={event => {
    event.preventDefault()
    if (locked || action.busy) return
    if (!form.description.trim()) { setInvalid(true); return }
    setInvalid(false)
    const submitted = form
    action.run(signal => initial ? api.patch(`/studio/assignments/${initial.id}/`, submitted, { signal }) : api.post(`/studio/lessons/${lesson}/assignments/`, submitted, { signal }), response => {
      setForm(current => JSON.stringify(current) === JSON.stringify(submitted) ? (initial ? { type: response.type, description: response.description, learning_activity: response.learning_activity || '' } : empty()) : current)
      onSaved(response)
    })
  }}><fieldset disabled={locked || action.busy}>
    <legend>{t('instructorStudio.assignment')}</legend>
    <p id={`${id}-hint`}>{t('instructorStudio.assignmentAuthoring.descriptionHint')}</p>
    <Input multiline label={t('instructorStudio.assignmentAuthoring.titleInstructions')} required value={form.description} aria-describedby={`${id}-hint${invalid ? ` ${id}-error` : ''}`} aria-invalid={invalid || undefined} onChange={event => { setInvalid(false); setForm({ ...form, description: event.target.value }) }} />
    {invalid && <p id={`${id}-error`} className="instructor-error" role="alert">{t('instructorStudio.assignmentAuthoring.required')}</p>}
    <Select label={t('instructorStudio.assignmentAuthoring.activityLabel')} value={form.learning_activity} onChange={event => setForm({ ...form, type: event.target.value === 'ai_selection_map' || (event.target.value === 'final_media_project' && form.type === 'quiz') ? 'text' : form.type, learning_activity: event.target.value })} options={[
      { value: '', label: t('instructorStudio.standardActivity') },
      { value: 'ai_selection_map', label: t('instructorStudio.selectionMap') },
      { value: 'final_media_project', label: t('instructorStudio.assignmentAuthoring.finalProject') },
    ]} />
    <Select label={t('instructorStudio.assignmentAuthoring.submissionOptions')} value={form.type} disabled={specialized} onChange={event => setForm({ ...form, type: event.target.value })} options={['text', 'file', ...(form.type === 'quiz' ? ['quiz'] : [])].map(value => ({ value, label: t(`instructorStudio.assignmentAuthoring.${value}`) }))} />
    <p>{t(specialized ? 'instructorStudio.assignmentAuthoring.structured' : form.type === 'file' ? 'instructorStudio.assignmentAuthoring.fileHint' : form.type === 'quiz' ? 'instructorStudio.assignmentAuthoring.quizHint' : 'instructorStudio.assignmentAuthoring.textHint')}</p>
    {!specialized && form.type !== 'quiz' && <p className="instructor-note">{t('assignmentSubmission.fileRules')}</p>}
    {finalProject && <section className="instructor-assignment-rubric"><AssignmentRubric /><p>{t('instructorStudio.assignmentAuthoring.fixedRubric')}</p></section>}
    <Notice {...action} />
    <div className="instructor-actions"><Button type="submit" variant="secondary" disabled={locked || action.busy}>{t('instructorStudio.save')}</Button><Button variant="ghost" aria-expanded={preview} aria-controls={`${id}-preview`} onClick={() => setPreview(!preview)}>{t('instructorStudio.assignmentAuthoring.preview')}</Button></div>
  </fieldset></form>
    {preview && <section id={`${id}-preview`} aria-label={t('instructorStudio.assignmentAuthoring.preview')}><AssignmentInstructions assignment={form} /></section>}
  </div>
}
