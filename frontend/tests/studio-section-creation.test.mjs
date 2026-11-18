import assert from 'node:assert/strict'
import {before,after,test} from 'node:test'
import {createElement} from 'react'
import {renderToStaticMarkup} from 'react-dom/server'
import {MemoryRouter} from 'react-router-dom'
import {readFile} from 'node:fs/promises'
import {createInstance} from 'i18next'
import {I18nextProvider} from 'react-i18next'
import {appendSection,renameSection,hasPendingSection} from '../src/utils/studioSections.js'
import {lessonDraft,draftPayload,draftEqual,savedDraft} from '../src/utils/studioDraft.js'
import {mediaLessonSections} from '../src/utils/mediaLessonPresentation.js'
import {attachmentLayout} from '../src/utils/lessonAttachments.js'
import {studioError} from '../src/utils/instructorStudio.js'
import {createTestServer} from './helpers/vite.mjs'
const plain={title:'New lesson',text_content:'  Existing exact text.\n\nAnother paragraph.  '}
const prepare=(form,title,text)=>({...form,section_new:{title,text}})
const add=(form,title,text,lesson=plain)=>appendSection(prepare(form,title,text),lesson)
test('first section explicitly wraps exact original text; second appends in order and resolves media',()=>{
 const first=add(lessonDraft(plain),'First','Additional text.')
 assert.ok(first.text_content.startsWith('First\n\n'+plain.text_content))
 const second=add(first,'Second','Second section text.')
 assert.deepEqual(second.learning_content.source_sections,['First','Second'])
 const payload=draftPayload(second)
 assert.ok(!('section_new' in payload))
 const persisted={...plain,...payload,attachments:[{id:1,kind:'srt',after_section:'Second'}]}
 const sections=mediaLessonSections(persisted)
 assert.deepEqual(sections.map(s=>s.heading),['First','Second'])
 assert.equal(attachmentLayout(persisted,sections).bySection.get('Second')[0].id,1)
 assert.equal(draftEqual(savedDraft(second,second,persisted).form,lessonDraft(persisted)),true)
})
test('pending title/text participates in dirty guard and cannot be silently saved',()=>{
 const baseline=lessonDraft(plain),pending=prepare(baseline,'Draft','Text')
 assert.ok(hasPendingSection(pending));assert.ok(!draftEqual(baseline,pending))
 assert.throws(()=>draftPayload(pending))
 assert.equal(draftPayload(baseline).text_content,plain.text_content)
 const response={...plain,...draftPayload(baseline)}
 const result=savedDraft(pending,baseline,response)
 assert.equal(result.form.section_new.title,'Draft');assert.ok(!draftEqual(result.form,result.baseline))
})
test('blank/duplicate/paragraph/orphan headings and ambiguous body reject without mutating input',()=>{
 const base=lessonDraft(plain)
 for(const heading of ['', ' ', 'line\nbreak','x'.repeat(256),'Another paragraph.'])assert.throws(()=>add(base,heading,'Text'))
 assert.throws(()=>add(base,'New','New'))
 const first=add(base,'First','Text')
 assert.throws(()=>add(first,'First','Other'))
 assert.throws(()=>add(first,'Second','First'))
 assert.throws(()=>add(first,'Second',''))
 assert.throws(()=>add(base,'Orphan','Body',{...plain,attachments:[{id:1,kind:'srt',after_section:'Orphan'}]}))
 assert.equal(base.text_content,plain.text_content)
 assert.deepEqual(base.learning_content.source_sections,[])
})
test('unsaved appended section can be renamed and a pending save rebases its new anchor',()=>{
 const base=lessonDraft({title:'New',text_content:''})
 const sent=add(base,'First','Body',{title:'New',text_content:''})
 const renamed={...renameSection(sent,{title:'New',text_content:''},'First','Renamed'),section_inputs:['Renamed']}
 assert.deepEqual(renamed.section_renames,[])
 const accepted=savedDraft(renamed,sent,{...plain,...draftPayload(sent)},'ru',{title:'New',text_content:''})
 assert.deepEqual(accepted.form.section_renames,[{from_title:'First',to_title:'Renamed'}])
 assert.ok(!draftEqual(accepted.form,accepted.baseline))
 const next=renameSection(accepted.form,{title:'New',text_content:''},'Renamed','Latest')
 assert.deepEqual(next.section_renames,[{from_title:'First',to_title:'Latest'}])
})
test('append can accompany a saved-section rename; legacy teaching blocks stay plain',()=>{
 const lesson={title:'Existing',text_content:'First\n\nOld text',learning_content:{source_sections:['First'],interactions:[]}}
 const renamed=renameSection(lessonDraft(lesson),lesson,'First','Renamed')
 const appended=add({...renamed,section_inputs:['Renamed']},'Second','New text',lesson)
 assert.deepEqual(draftPayload(appended).section_renames,[{from_title:'First',to_title:'Renamed'}])
 const legacy=lessonDraft({...plain,learning_content:{source_sections:[],interactions:[{type:'categories',items:[]}]}})
 assert.throws(()=>add(legacy,'New','Body'))
 assert.equal(draftPayload(legacy).text_content,plain.text_content)
})
let server,Sections,Notice
before(async()=>{server=await createTestServer();Sections=(await server.ssrLoadModule('/src/components/instructor/LessonSections.jsx')).default;Notice=(await server.ssrLoadModule('/src/components/instructor/QuizPreviewNotice.jsx')).default})
after(async()=>server?.close())
test('RU/KK/EN creation guidance, errors, Studio link and real quiz requirement are localized',async()=>{
 for(const language of ['ru','kk','en']){
  const words=JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`,import.meta.url),'utf8'))
  const i18n=createInstance();await i18n.init({lng:language,resources:{[language]:{translation:words}}})
  const render=(Component,props)=>renderToStaticMarkup(createElement(I18nextProvider,{i18n},createElement(MemoryRouter,null,createElement(Component,props))))
  const html=render(Sections,{form:lessonDraft(plain),lesson:plain,setForm(){}})
  for(const key of ['heading','text','add','existingText'])assert.ok(html.includes(i18n.t(`instructorStudio.sectionCreation.${key}`)))
  assert.ok(render(Notice,{courseId:55}).includes('/instructor/courses/55/assessment'))
  assert.doesNotMatch(render(Notice,{courseId:55}),/Django Admin/)
  for(const value of Object.values(words.instructorStudio.sectionCreation.errors))assert.ok(value.trim())
  assert.equal(studioError({response:{data:{section_additions:'error'}}},'Fallback',i18n.t.bind(i18n)),words.instructorStudio.sectionCreation.errors.server)
  assert.ok(words.instructorStudio.requirements.assessment.trim())
 }
})
