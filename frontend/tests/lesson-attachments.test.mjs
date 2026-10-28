import assert from 'node:assert/strict'
import { before, after, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { attachmentLayout, downloadAttachment, loadLessonAttachment } from '../src/utils/lessonAttachments.js'
import { createTestServer } from './helpers/vite.mjs'
let server, Body, Material
const instances=new Map()
before(async()=>{
 server=await createTestServer()
 Body=(await server.ssrLoadModule('/src/components/learning/LessonAttachment.jsx')).AttachmentContent
 Material=(await server.ssrLoadModule('/src/pages/LessonView.jsx')).LessonMaterial
 for(const language of ['ru','kk','en']){
  const dictionary=JSON.parse(await readFile(new URL(`../src/i18n/locales/${language}.json`,import.meta.url),'utf8'))
  const instance=createInstance();await instance.init({lng:language,resources:{[language]:{translation:dictionary}}});instances.set(language,instance)
 }
})
after(async()=>{await server?.close()})
const audio={id:7,kind:'audio',label:'Fixture narration',caption:'Fixture caption',transcript:'Original written equivalent',after_section:'Section',filename:'fixture.wav'}
const srt={id:8,kind:'srt',label:'Fixture subtitles',caption:'Illustrative times',filename:'fixture.srt',after_section:'Section'}
function render(props,language='en'){
 return renderToStaticMarkup(createElement(I18nextProvider,{i18n:instances.get(language)},createElement(Body,{id:'fixture',asset:audio,...props})))
}

test('native audio controls have label, transcript, caption and no autoplay in all locales',()=>{
 for(const language of ['ru','kk','en']){
  const html=render({src:'blob:private'},language)
  assert.match(html,/<audio controls="" preload="metadata" src="blob:private"/)
  assert.match(html,/aria-labelledby="fixture-label" aria-describedby="fixture-transcript"/)
  assert.match(html,/Original written equivalent/)
  assert.match(html,/<figcaption>Fixture caption/)
  assert.doesNotMatch(html,/autoplay|learning\.audioTranscript/)
 }
})

test('SRT download points only at a loaded private blob with original filename',()=>{
 const html=render({asset:srt,src:'blob:subtitles'})
 assert.match(html,/href="blob:subtitles" download="fixture.srt"/)
 assert.doesNotMatch(html,/<audio|\/media\//)
 const failed=render({asset:srt,error:true})
 assert.match(failed,/role="alert"/)
 assert.doesNotMatch(failed,/href=/)
})

test('attachments stay inline by exact anchor, unknown anchors use materials fallback',()=>{
 const lesson={attachments:[audio,{...srt,after_section:'unknown'}]}
 const positions=attachmentLayout(lesson,[{heading:'Section'}])
 assert.equal(positions.bySection.get('Section')[0],audio)
 assert.equal(positions.fallback[0].id,8)
 const value={text_content:'Section\n\nTheory\n\nNext\n\nMore theory',learning_content:{source_sections:['Section','Next'],interactions:[],content_language:'ru'},attachments:[audio]}
 const html=renderToStaticMarkup(createElement(I18nextProvider,{i18n:instances.get('en')},createElement(Material,{lesson:value})))
 assert.equal((html.match(/Fixture narration/g)||[]).length,1)
 assert.ok(html.indexOf('Theory')<html.indexOf('Fixture narration'))
 assert.ok(html.indexOf('Original written equivalent')<html.indexOf('Next'))
})

function harness(asset=audio,client={get:async()=>({data:new Blob(['fixture'],{type:'audio/wav'})})}){
 const loaded=[],errors=[],revoked=[],calls=[]
 const request=loadLessonAttachment({get:(...args)=>{calls.push(args);return client.get(...args)}},asset,src=>loaded.push(src),e=>errors.push(e),{createObjectURL:()=> 'blob:fixture',revokeObjectURL:src=>revoked.push(src)})
 return {request,loaded,errors,revoked,calls}
}

test('authenticated client blob request has cancellation and revokes URLs on disposal',async()=>{
 const state=harness();await state.request.promise
 assert.equal(state.calls[0][0],'/lesson-attachments/7/')
 assert.equal(state.calls[0][1].responseType,'blob')
 assert.ok(state.calls[0][1].signal instanceof AbortSignal)
 assert.deepEqual(state.loaded,['blob:fixture'])
 state.request.dispose();state.request.dispose()
 assert.deepEqual(state.revoked,['blob:fixture'])
})

test('failures, MIME mismatch, invalid IDs and stale responses never create usable sources',async()=>{
 for(const data of [new Blob(['bad'],{type:'text/html'}),new Blob([],{type:'audio/wav'}),{},new Blob(['bad'],{type:'application/x-subrip'})]){
  const state=harness(audio,{get:async()=>({data})});await state.request.promise
  assert.equal(state.loaded.length,0);assert.equal(state.errors.length,1)
 }
 for(const status of [401,403,404,500]){
  const state=harness(audio,{get:async()=>{throw {response:{status}}}});await state.request.promise
  assert.equal(state.loaded.length,0);assert.equal(state.errors.length,1)
 }
 const bad=harness({...audio,id:'https://untrusted.test'});await bad.request.promise;assert.equal(bad.calls.length,0)
 let resolve
 const stale=harness(audio,{get:()=>new Promise(r=>{resolve=r})})
 stale.request.dispose();resolve({data:new Blob(['late'],{type:'audio/wav'})});await stale.request.promise
 assert.deepEqual(stale.loaded,[]);assert.deepEqual(stale.errors,[])
})

test('SRT uses the same authorization loader and triggers an explicit download',async()=>{
 const state=harness(srt,{get:async()=>({data:new Blob(['fixture'],{type:'application/x-subrip'})})})
 await state.request.promise;assert.deepEqual(state.loaded,['blob:fixture']);state.request.dispose()
 const actions=[]
 const link={click:()=>actions.push('click'),remove:()=>actions.push('remove')}
 downloadAttachment('blob:subtitles','fixture.srt',{createElement:()=>link,body:{appendChild:()=>actions.push('append')}})
 assert.deepEqual(actions,['append','click','remove']);assert.equal(link.download,'fixture.srt');assert.equal(link.href,'blob:subtitles')
})
