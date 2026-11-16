import { mediaLessonSections } from './mediaLessonPresentation.js'
import { attachmentLayout } from './lessonAttachments.js'

export function savedSectionHeadings(lesson) {
  return mediaLessonSections(lesson)?.map(section => section.heading) || []
}

export function attachmentPlacement(lesson, asset) {
  const headings = savedSectionHeadings(lesson)
  const layout = attachmentLayout(lesson, headings.map(heading => ({ heading })))
  const rendered = [...layout.bySection.values()].flat().concat(layout.fallback)
  const subtitleId = rendered.find(item => item.id === asset.id)?.subtitle_attachment_id
  const subtitle = (lesson.attachments || []).find(item => item.id === subtitleId)
  const siblings = (lesson.attachments || []).filter(item => item.after_section === asset.after_section)
  const ambiguous = asset.kind === 'video' && !!asset.after_section && (siblings.filter(a => a.kind === 'video').length !== 1 || siblings.filter(a => a.kind === 'vtt').length > 1)
  return { headings, subtitle, ambiguous, unresolved: !!asset.after_section && !headings.includes(asset.after_section), eligible: ['audio', 'srt', 'video'].includes(asset.kind) && !ambiguous && headings.length > 0 }
}

export function placementPayload(lesson, asset, target) {
  const info = attachmentPlacement(lesson, asset)
  return { after_section: target, expected_after_section: asset.after_section || '', expected_sections: [...(lesson.learning_content?.source_sections || [])], expected_subtitle_id: info.subtitle?.id || null }
}

export function sectionMovesBlocked(form, lesson) {
  return !!form.section_renames?.length || JSON.stringify(form.learning_content?.source_sections || []) !== JSON.stringify(lesson.learning_content?.source_sections || [])
    || form.section_inputs?.some((title, index) => title.trim() !== form.learning_content.source_sections[index])
}
