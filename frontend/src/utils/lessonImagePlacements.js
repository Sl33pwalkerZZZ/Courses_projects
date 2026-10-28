// Only declared IDs already present in this authorized lesson response can render.
export function lessonImagePlacements(lesson, sections) {
  const bySection = new Map(), placed = new Set()
  const anchors = new Set((sections || []).map(section => section.heading))
  const images = new Map((lesson.images || []).map(image => [image.id, image]))
  for (const item of lesson.learning_content?.interactions || []) {
    if (item.type !== 'image_placement' || !Number.isSafeInteger(item.image_id)
      || !anchors.has(item.after_section) || !images.has(item.image_id) || placed.has(item.image_id)
      || typeof item.caption !== 'string' || !item.caption.trim()) continue
    const group = bySection.get(item.after_section) || []
    group.push({ image: images.get(item.image_id), caption: item.caption })
    bySection.set(item.after_section, group)
    placed.add(item.image_id)
  }
  return { bySection, gallery: (lesson.images || []).filter(image => !placed.has(image.id)) }
}
