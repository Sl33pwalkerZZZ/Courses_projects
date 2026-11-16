import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { createTestServer } from './helpers/vite.mjs'
import { attachmentPlacement, placementPayload, savedSectionHeadings, sectionMovesBlocked } from '../src/utils/studioAttachmentPlacement.js'
import { attachmentLayout } from '../src/utils/lessonAttachments.js'
import { mediaLessonSections } from '../src/utils/mediaLessonPresentation.js'
import { lessonDraft } from '../src/utils/studioDraft.js'
import { renameSection } from '../src/utils/studioSections.js'
import { studioError } from '../src/utils/instructorStudio.js'

const lesson = { id: 501, text_content: 'First\n\nExplanation\n\nSecond\n\nEnd', learning_content: { source_sections: ['First', 'Second'], interactions: [] }, attachments: [ { id: 1, kind: 'video', label: 'Video example', filename: 'video.mp4', after_section: 'First' }, { id: 2, kind: 'vtt', label: 'Caption example', filename: 'captions.vtt', after_section: 'First' }, { id: 3, kind: 'srt', label: 'Legacy SRT', filename: 'legacy.srt', after_section: 'Missing' } ] }
let server, Manager
before(async () => { server = await createTestServer(); Manager = (await server.ssrLoadModule('/src/components/instructor/LessonAttachmentManager.jsx')).default })
after(async () => { await server?.close() })

test('saved sections retain ordering; exact student pairing is reused including fallback', () => {
 assert.deepEqual(savedSectionHeadings(lesson), ['First', 'Second'])
 const info = attachmentPlacement(lesson, lesson.attachments[0])
 assert.equal(info.subtitle.id, 2)
 assert.equal(info.eligible, true)
 assert.equal(attachmentPlacement(lesson, lesson.attachments[2]).unresolved, true)
 assert.equal(attachmentPlacement(lesson, lesson.attachments[1]).eligible, false)
 const orphan = { ...lesson, attachments: lesson.attachments.map(a => a.kind === 'srt' ? a : { ...a, after_section: 'Missing' }) }
 assert.equal(attachmentPlacement(orphan, orphan.attachments[0]).subtitle.id, 2)
 assert.equal(attachmentPlacement(orphan, orphan.attachments[0]).unresolved, true)
})
test('move snapshot and reload preserve video identity, subtitle pairing and standalone SRT', () => {
 const payload = placementPayload(lesson, lesson.attachments[0], 'Second')
 assert.deepEqual(payload, { after_section: 'Second', expected_after_section: 'First', expected_sections: ['First', 'Second'], expected_subtitle_id: 2 })
 const reloaded = { ...lesson, attachments: lesson.attachments.map(a => [1, 2].includes(a.id) ? { ...a, after_section: 'Second' } : a) }
 const layout = attachmentLayout(reloaded, mediaLessonSections(reloaded))
 assert.equal(layout.bySection.has('First'), false)
 assert.equal(layout.bySection.get('Second')[0].subtitle_attachment_id, 2)
 assert.equal(layout.bySection.get('Second')[0].id, 1)
 assert.equal(layout.fallback[0].id, 3)
})
test('ambiguous source is ineligible and empty anchor does not imply captions', () => {
 const ambiguous = { ...lesson, attachments: [...lesson.attachments, { id: 4, kind: 'vtt', after_section: 'First' }] }
 const info = attachmentPlacement(ambiguous, ambiguous.attachments[0])
 assert.equal(info.ambiguous, true)
 assert.equal(info.eligible, false)
 assert.equal(info.subtitle, undefined)
 const empty = { ...lesson, attachments: lesson.attachments.map(a => ({ ...a, after_section: '' })) }
 assert.equal(attachmentPlacement(empty, empty.attachments[0]).subtitle, undefined)
 assert.equal(attachmentPlacement(empty, empty.attachments[0]).unresolved, false)
})
test('pending section renames/raw invalid title block moves while unsaved text does not', () => {
 const draft = lessonDraft(lesson)
 draft.text_content += '\n\nUnsaved explanation'
 assert.equal(!!sectionMovesBlocked(draft, lesson), false)
 const renamed = renameSection(draft, lesson, 'First', 'Pending')
 assert.equal(sectionMovesBlocked(renamed, lesson), true)
 assert.equal(sectionMovesBlocked({ ...draft, section_inputs: ['', 'Second'] }, lesson), true)
 assert.equal(draft.text_content.endsWith('Unsaved explanation'), true)
})
test('legacy, missing or ambiguous headings have no move targets', () => {
 assert.deepEqual(savedSectionHeadings({}), [])
 assert.deepEqual(savedSectionHeadings({ ...lesson, text_content: 'Intro\n\n' + lesson.text_content }), [])
 assert.deepEqual(savedSectionHeadings({ ...lesson, learning_content: { ...lesson.learning_content, interactions: [{ type: 'llm_steps' }] } }), [])
 assert.deepEqual(savedSectionHeadings({ ...lesson, text_content: lesson.text_content + '\n\nFirst' }), [])
 assert.deepEqual(savedSectionHeadings({ ...lesson, learning_content: { source_sections: ['Second', 'First'] } }), [])
})
test('RU/KK/EN inventory, linked captions, rename guard and server error localization', async () => {
 for (const language of ['ru', 'kk', 'en']) {
  const translations = JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`, import.meta.url), 'utf8'))
  const i18n = createInstance(); await i18n.init({ lng: language, resources: { [language]: { translation: translations } }, interpolation: { escapeValue: false } })
  const render = props => renderToStaticMarkup(createElement(I18nextProvider, { i18n }, createElement(Manager, { lesson, onSaved() {}, ...props })))
  const html = render({ movesBlocked: false })
  assert.match(html, /Caption example \(captions.vtt\)/)
  assert.ok(html.includes(translations.instructorStudio.placement.current))
  assert.ok(html.includes(translations.instructorStudio.unresolvedPlacements))
  assert.ok(html.indexOf('<option value="First"') < html.indexOf('<option value="Second"'))
  const blocked = render({ movesBlocked: true })
  assert.ok(blocked.includes(translations.instructorStudio.placement.renamePending))
  assert.match(blocked, /disabled=""/)
  for (const code of ['stale', 'ambiguous', 'invalid', 'track', 'locked']) assert.equal(studioError({ response: { data: { placement_error: code } } }, 'fallback', i18n.t.bind(i18n)), translations.instructorStudio.placement[code])
 }
})
