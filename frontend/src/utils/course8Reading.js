import source from './course8Source.json' with { type: 'json' }
import { sourceFingerprint } from './sourceFingerprint.js'

const heading = text => text.replace(/^1\.[1-8]\.\s+/, '')

// Public metadata contains fingerprints only. A teacher edit must restore the
// ordinary complete renderer, never silently discard new prose or interactions.
export function getCourse8Reading(lesson) {
  const expected = source[String(lesson?.id)]
  if (!expected || ![93, 94, 95].includes(expected.id) || lesson.course_slug !== expected.course_slug
    || sourceFingerprint(lesson.text_content || '') !== expected.text
    || sourceFingerprint(JSON.stringify(lesson.learning_content?.interactions) || '') !== expected.interactions) return null
  const saved = { ...lesson, interactions: lesson.learning_content.interactions }
  const paragraphs = saved.text_content.split('\n\n')
  if (saved.id === 93) {
    const [definition, example] = paragraphs[1].split(' Например, ')
    return { id: 93, heading: heading(paragraphs[0]), definition,
      example: `Например, ${example}`, comparison: saved.interactions[0], conclusion: paragraphs[3] }
  }
  if (saved.id === 94) return {
    id: 94, heading: heading(paragraphs[0]), categories: saved.interactions[0], caveat: paragraphs[2],
    servicesHeading: heading(paragraphs[3]), services: saved.interactions[1].items.map(item => ({
      ...item, text: item.text.slice(0, -` Адрес: ${item.url}`.length),
    })), conclusion: paragraphs.at(-1),
  }
  return { id: 95, heading: heading(paragraphs[0]), process: saved.interactions[0] }
}
