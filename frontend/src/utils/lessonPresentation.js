import { lessonParagraphs } from './lessons.js'
import { lesson91Source } from './lesson91Source.js'

// Omit only the verified Word cover/course introduction from this lesson view.
// Unknown teacher edits fall back to the complete text rather than losing prose.
export function lesson91Reading(lesson, paragraphs) {
  const source = lesson91Source
  const matchesLesson = Number(lesson.id) === source.lessonId && lesson.course_slug === source.courseSlug
  const matchesPrefix = source.titlePage.every((text, index) => paragraphs[index] === text)
  return matchesLesson && matchesPrefix && paragraphs[source.titlePage.length] === source.sectionHeading
    ? paragraphs.slice(source.titlePage.length) : paragraphs
}

export function lessonReadingBlocks(paragraphs) {
  const source = lesson91Source
  const blocks = []
  for (let index = 0; index < paragraphs.length; index++) {
    const matchesExamples = paragraphs[index] === source.exampleHeading
      && source.examples.every((text, offset) => paragraphs[index + 1 + offset] === text)
      && paragraphs[index + 1 + source.examples.length] === source.relationHeading
    if (matchesExamples) {
      blocks.push({ type: 'examples', heading: source.exampleHeading, items: [...source.examples] })
      index += source.examples.length
    } else blocks.push({ type: 'paragraph', text: paragraphs[index] })
  }
  return blocks
}

// Presentation-only changes: never change the API objects or stored source text.
export function isSelectionMapTemplate(interaction) {
  return interaction.type === 'model_service'
    && JSON.stringify(interaction.headers) === JSON.stringify(['Параметр', 'Ответ участника'])
    && interaction.rows?.length > 0
    && interaction.rows.every(row => Array.isArray(row) && row.length === 2 && typeof row[1] === 'string' && !row[1].trim())
}

export function studentInteraction(interaction) {
  return interaction.title === 'Сервисы из раздела 1.5 — сведения требуют проверки перед публикацией'
    ? { ...interaction, title: 'Обзор популярных ИИ-сервисов' } : interaction
}

export function studentAssignmentDescription(description = '') {
  const provenance = 'Поля сравнения и сохранение черновика — авторское цифровое развитие исходной карты.'
  return description.endsWith(provenance) ? description.slice(0, -provenance.length).trim() : description
}

export function lessonPresentation(lesson) {
  const structuredPractice = lesson.assignments?.some(item => item.learning_activity === 'ai_selection_map')
  const source = lesson.learning_content
  const templates = structuredPractice ? (source?.interactions || []).filter(isSelectionMapTemplate) : []
  const interactions = (source?.interactions || []).filter(item => !templates.includes(item)).map(studentInteraction)
  const sections = { reading: [], conclusions: [], resources: [] }
  let current = 'reading'
  for (const paragraph of lesson91Reading(lesson, lessonParagraphs(lesson))) {
    if (structuredPractice && paragraph.trim() === '1.8. Выводы по первой главе') current = 'conclusions'
    if (structuredPractice && paragraph.trim() === 'Материалы для дополнительного изучения') current = 'resources'
    sections[current].push(paragraph)
  }
  return { ...sections, templates, content: source ? { ...source, objectives: [], interactions } : null }
}

// The source task/function table explains this specific imported selection step.
// Keep unrelated tables in their original position rather than guessing associations.
export function selectionStepUsesSourceTable(interaction, selected) {
  const step = interaction.steps?.[selected]
  return interaction.type === 'selection_steps' && selected === 1
    && step?.title === 'Шаг 2. Определить необходимые возможности'
    && !(step.text || step.description || step.body)
    && interaction.headers?.[0] === 'Задача'
    && interaction.headers?.[1] === 'Нужные функции'
    && interaction.rows?.length > 0
}
