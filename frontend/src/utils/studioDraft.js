import { prepareLearningContent } from './instructorStudio.js'

export function lessonDraft(lesson, language = 'ru') {
  return { title: lesson.title, text_content: lesson.text_content || '', learning_content: {
    content_language: language, source_sections: [], objectives: [], interactions: [], ...lesson.learning_content,
  } }
}
export function draftPayload(form) {
  return { ...form, learning_content: prepareLearningContent(form.learning_content) }
}
export function draftEqual(a, b) {
  return JSON.stringify(a) === JSON.stringify(b)
}
export function savedDraft(current, submitted, response, language) {
  const baseline = lessonDraft(response, language)
  return { baseline, form: draftEqual(current, submitted) ? baseline : current }
}

export { guardStudioNavigation } from './studioNavigation.js'
