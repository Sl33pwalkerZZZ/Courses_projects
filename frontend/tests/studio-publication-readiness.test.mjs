import assert from 'node:assert/strict'
import {before,after,test} from 'node:test'
import {readFile} from 'node:fs/promises'
import {createElement} from 'react'
import {renderToStaticMarkup} from 'react-dom/server'
import {MemoryRouter} from 'react-router-dom'
import {createInstance} from 'i18next'
import {I18nextProvider} from 'react-i18next'
import {createTestServer} from './helpers/vite.mjs'
let server,Form
const locales=new Map()
before(async()=>{
 server=await createTestServer();Form=(await server.ssrLoadModule('/src/pages/instructor/Publication.jsx')).PublicationForm
 for(const lang of ['en','ru','kk']){const words=JSON.parse(await readFile(new URL(`../src/i18n/locales/${lang}.json`,import.meta.url),'utf8'));const i18n=createInstance();await i18n.init({lng:lang,resources:{[lang]:{translation:words}}});locales.set(lang,i18n)}
})
after(async()=>server?.close())
const course={id:500,slug:'isolated-fixture'}
const keys=['title','description','curriculum','lesson_content','assessment','source_reviewed','assessment_reviewed']
function render(data,moderator=false,lang='en'){return renderToStaticMarkup(createElement(I18nextProvider,{i18n:locales.get(lang)},createElement(MemoryRouter,null,createElement(Form,{course,data,onSaved(){},moderator}))))}
function data(met=false){return {is_published:false,requirements:keys.map(key=>({key,label:key,met})),requests:[]}}
test('real blockers link to existing Studio screens and reused preview route; no author moderation',()=>{
 const html=render(data())
 for(const path of ['edit','curriculum','assessment'])assert.ok(html.includes(`/instructor/courses/500/${path}`))
 assert.ok(html.includes('/instructor/courses/isolated-fixture/preview'))
 assert.doesNotMatch(html,/href="\/instructor\/reviews"/)
 assert.match(html,/<button[^>]*type="submit"[^>]*disabled/)
 assert.ok(html.includes('Recommendations — not publication blockers'))
})
test('pending and published states disable requests and acknowledgements; moderator sees reviews',()=>{
 for(const current of [{...data(true),requests:[{id:1,status:'pending',created_at:'2026-11-18T00:00:00Z'}]},{...data(true),is_published:true}]){
  const html=render(current,true)
  assert.match(html,/<fieldset disabled=""/)
  assert.match(html,/<button[^>]*type="submit"[^>]*disabled/)
  assert.ok(html.includes('/instructor/reviews'))
  assert.equal((html.match(/type="checkbox" checked=""/g)||[]).length,2)
 }
 const pending=render({...data(true),requests:[{id:1,status:'pending',created_at:'2026-11-18T00:00:00Z'}]})
 assert.ok(pending.includes('reject the stale request'))
})
test('rejection feedback and server conditions/actions are localized in all three languages',()=>{
 for(const [lang,i18n] of locales){
  const html=render({...data(),requests:[{id:1,status:'rejected',note:'Fixture feedback',created_at:'2026-11-18T00:00:00Z'}]},false,lang)
  assert.ok(html.includes('Fixture feedback'))
  for(const key of keys)assert.ok(html.includes(i18n.t(`instructorStudio.publicationReadiness.actions.${key}`)))
  for(const key of ['status','requirements','blocked','recommendations','recommendationText','rejectedHint'])assert.ok(html.includes(i18n.t(`instructorStudio.publicationReadiness.${key}`)))
 }
})
test('review acknowledgement is still needed for a new request, even when a prior server snapshot reports reviewed',()=>{
 const html=render(data(true))
 assert.match(html,/<button[^>]*type="submit"[^>]*disabled/)
 assert.ok(html.includes('Review questions and answer keys'))
})
