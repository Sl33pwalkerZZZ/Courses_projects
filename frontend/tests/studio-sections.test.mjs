import assert from 'node:assert/strict'
import { test } from 'node:test'
import { lessonDraft, draftPayload, savedDraft, draftEqual } from '../src/utils/studioDraft.js'
import { sectionInventory, renameSection } from '../src/utils/studioSections.js'
import { mediaLessonSections } from '../src/utils/mediaLessonPresentation.js'
import { attachmentLayout } from '../src/utils/lessonAttachments.js'

const lesson = { id: 701, title: 'Fixture', text_content: 'First\n\nExplanation\n\nSecond\n\nEnd', learning_content: { source_sections: ['First', 'Second'], objectives: ['Goal'], interactions: [{ type: 'image_placement', image_id: 4, after_section: 'First', caption: 'Diagram' }] }, attachments: [ { id: 1, kind: 'video', after_section: 'First' }, { id: 2, kind: 'vtt', after_section: 'First' }, { id: 3, kind: 'audio', after_section: 'Missing' } ] }
function renamed(form, from, to) {
 const next = renameSection(form, lesson, from, to)
 return { ...next, section_inputs: next.learning_content.source_sections }
}
test('ordered sections show video, VTT, image and unresolved placements', () => {
 const inventory = sectionInventory(lessonDraft(lesson), lesson)
 assert.deepEqual(inventory.sections.map(s => s.heading), ['First', 'Second'])
 assert.deepEqual(inventory.sections[0].assets.map(a => a.kind), ['video', 'vtt', 'image'])
 assert.deepEqual(inventory.unresolved.map(a => a.id), [3])
})
test('rename save reload student presentation preserves video/VTT pairing and image anchor', () => {
 const form = renamed(lessonDraft(lesson), 'First', 'New first')
 const payload = draftPayload(form)
 assert.deepEqual(payload.section_renames, [{ from_title: 'First', to_title: 'New first' }])
 const persisted = { ...lesson, ...payload, attachments: lesson.attachments.map(a => a.after_section === 'First' ? { ...a, after_section: 'New first' } : a) }
 const sections = mediaLessonSections(persisted)
 assert.equal(sections[0].heading, 'New first')
 assert.equal(attachmentLayout(persisted, sections).bySection.get('New first')[0].subtitle_attachment_id, 2)
 assert.equal(persisted.learning_content.interactions[0].after_section, 'New first')
 assert.equal(draftEqual(savedDraft(form, form, persisted).form, lessonDraft(persisted)), true)
})
test('ambiguous headings, body collisions and orphan collisions reject without mutation', () => {
 const original = lessonDraft(lesson)
 for (const to of ['', 'Second', 'Explanation', 'Missing']) assert.throws(() => renameSection(original, lesson, 'First', to))
 assert.throws(() => renameSection({ ...original, text_content: original.text_content + '\n\nFirst' }, lesson, 'First', 'New'))
 assert.equal(original.text_content, lesson.text_content)
 const invalid = { ...original, section_inputs: ['', 'Second'] }
 assert.throws(() => draftPayload(invalid))
 assert.equal(draftEqual(invalid, original), false)
})
test('failed save and background media refresh retain dirty draft; later save rebases newer rename', () => {
 const submitted = renamed(lessonDraft(lesson), 'First', 'Sent')
 const newer = renamed(submitted, 'Sent', 'Newer')
 const refreshed = { ...lesson, attachments: [...lesson.attachments, { id: 9, kind: 'srt', after_section: 'First' }] }
 assert.equal(sectionInventory(newer, refreshed).sections[0].assets.length, 4)
 assert.equal(newer.text_content.startsWith('Newer'), true) // rejection leaves current state intact
 const response = { ...lesson, ...draftPayload(submitted), attachments: lesson.attachments.map(a => a.after_section === 'First' ? { ...a, after_section: 'Sent' } : a) }
 const accepted = savedDraft(newer, submitted, response, 'ru', lesson)
 assert.equal(accepted.form.text_content.startsWith('Newer'), true)
 assert.deepEqual(accepted.form.section_renames, [{ from_title: 'Sent', to_title: 'Newer' }])
 assert.equal(draftEqual(accepted.form, accepted.baseline), false)
 // Even before the workspace receives new attachment props, the media stays linked.
 assert.equal(sectionInventory(accepted.form, lesson).sections[0].assets.length, 3)
})
test('plain lessons and non-heading identifiers keep text editor fallback', () => {
 const plain = lessonDraft({ title: 'Plain', text_content: 'Body' })
 assert.deepEqual(sectionInventory(plain, {}).sections, [])
 assert.equal(draftPayload(plain).text_content, 'Body')
 const legacy = lessonDraft({ ...lesson, learning_content: { ...lesson.learning_content, source_sections: ['stable-id'] } })
 assert.equal(sectionInventory(legacy, lesson).sections[0].valid, false)
})

test('display aliases are scoped to attachment identity when another section reuses a freed heading', () => {
 const form = { ...lessonDraft(lesson), learning_content: { ...lesson.learning_content, interactions: [], source_sections: ['Renamed', 'First'] }, text_content: 'Renamed\n\nExplanation\n\nFirst\n\nEnd', section_aliases: [{ id: 1, from_title: 'First', to_title: 'Renamed' }] }
 const props = { ...lesson, attachments: [{ id: 1, kind: 'video', after_section: 'First' }, { id: 88, kind: 'srt', after_section: 'First' }] }
 const inventory = sectionInventory(form, props)
 assert.deepEqual(inventory.sections[0].assets.map(a => a.id), [1])
 assert.deepEqual(inventory.sections[1].assets.map(a => a.id), [88])
})

test('a conflicting batch cannot reuse another pending rename source', () => {
 const form = renamed(lessonDraft(lesson), 'First', 'Freed')
 assert.throws(() => renameSection(form, lesson, 'Second', 'First'))
 // Undoing the same pending rename is still supported.
 const undone = renamed(form, 'Freed', 'First')
 assert.deepEqual(undone.section_renames, [])
})
