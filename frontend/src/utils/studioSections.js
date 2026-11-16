// Title anchors are the persisted identifiers. Never infer an anchor from an ID or filename.
export function sectionInventory(form, lesson) {
  const headings = form.learning_content?.source_sections || []
  const renames = new Map((form.section_renames || []).map(item => [item.from_title, item.to_title]))
  const aliases = new Map((form.section_aliases || []).map(item => [item.id, item]))
  const resolve = asset => {
    const alias = aliases.get(asset.id)
    const anchor = alias?.from_title === asset.after_section ? alias.to_title : asset.after_section
    return renames.get(anchor) || anchor
  }
  const assets = [
    ...(lesson.attachments || []).map(asset => ({ ...asset, after_section: resolve(asset) })),
    ...(form.learning_content?.interactions || []).filter(item => item.type === 'image_placement').map(item => ({ ...item, id: item.image_id, kind: 'image', label: item.caption })),
  ]
  const paragraphs = form.text_content.split(/\n\s*\n/u).map(p => p.trim()).filter(Boolean)
  const valid = heading => headings.filter(h => h === heading).length === 1 && paragraphs.filter(p => p === heading).length === 1
  return {
    sections: headings.map(heading => ({ heading, valid: valid(heading), assets: valid(heading) ? assets.filter(asset => asset.after_section === heading) : [] })),
    unresolved: assets.filter(asset => !headings.includes(asset.after_section) || !valid(asset.after_section)),
  }
}

export function renameSection(form, lesson, from, rawTitle) {
  const to = rawTitle.trim()
  if (to === from) return form
  const inventory = sectionInventory(form, lesson)
  if (!to || to.length > 255 || /[\r\n]/u.test(to) || !inventory.sections.find(s => s.heading === from)?.valid
    || (form.section_renames || []).some(item => item.from_title === to && item.to_title !== from)
    || inventory.sections.some(s => s.heading === to) || inventory.unresolved.some(asset => asset.after_section === to)
    || form.text_content.split(/\n\s*\n/u).some(p => p.trim() === to)) throw new Error('ambiguousSectionRename')
  const existing = form.section_renames || []
  const original = existing.find(item => item.to_title === from)?.from_title || from
  const renames = existing.filter(item => item.from_title !== original)
  if (original !== to) renames.push({ from_title: original, to_title: to })
  return { ...form, section_renames: renames,
    text_content: form.text_content.split(/(\n\s*\n)/u).map(p => p.trim() === from ? p.replace(from, to) : p).join(''),
    learning_content: { ...form.learning_content,
      source_sections: form.learning_content.source_sections.map(h => h === from ? to : h),
      interactions: form.learning_content.interactions.map(item => item.type === 'image_placement' && item.after_section === from ? { ...item, after_section: to } : item),
    },
  }
}

// A save may finish after further typing/renaming. Rebase only acknowledged intents.
export function remainingRenames(current, submitted) {
  const acknowledged = new Map((submitted.section_renames || []).map(item => [item.from_title, item.to_title]))
  const result = []
  for (const item of current.section_renames || []) {
    const from = acknowledged.get(item.from_title) || item.from_title
    if (from !== item.to_title) result.push({ from_title: from, to_title: item.to_title })
    acknowledged.delete(item.from_title)
  }
  for (const [original, saved] of acknowledged) result.push({ from_title: saved, to_title: original })
  return result
}
