import { remainingRenames } from './studioSections.js'
import { prepareLearningContent } from './instructorStudio.js'

export function lessonDraft(lesson, language = 'ru') {
  return { section_inputs: [...(lesson.learning_content?.source_sections || [])], section_renames: [], title: lesson.title, text_content: lesson.text_content || '', learning_content: {
    content_language: language, source_sections: [], objectives: [], interactions: [], ...lesson.learning_content,
  } }
}
export function draftPayload(form) {
  const { section_inputs, section_aliases: _aliases, ...payload } = form
  if (section_inputs?.some((title, i) => !title.trim() || title.trim() !== form.learning_content.source_sections[i])) throw new Error('Invalid section heading')
  return { ...payload, learning_content: prepareLearningContent(form.learning_content) }
}
export function draftEqual(a, b) {
  const comparable = ({ section_aliases: _aliases, ...draft }) => draft
  return JSON.stringify(comparable(a)) === JSON.stringify(comparable(b))
}
export function savedDraft(current, submitted, response, language, lesson = {}) {
  const baseline = lessonDraft(response, language)
  // Workspace refresh can fail after a successful save. Keep display-only aliases
  // so old media props still resolve, without making the acknowledged draft dirty.
  const aliases = []
  for (const asset of lesson.attachments || []) {
    const saved = response.attachments?.find(item => item.id === asset.id)
    if (saved && saved.after_section !== asset.after_section) aliases.push({ id: asset.id, from_title: asset.after_section, to_title: saved.after_section })
  }
  const next = draftEqual(current, submitted) ? baseline : { ...current, section_renames: remainingRenames(current, submitted) }
  return { baseline, form: { ...next, section_aliases: aliases } }
}

export { guardStudioNavigation } from './studioNavigation.js'
