import assert from 'node:assert/strict'
import { before, after, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createTestServer } from './helpers/vite.mjs'
import { requestVideoPlayback, safePlaybackPath } from '../src/utils/lessonVideo.js'
import { attachmentLayout } from '../src/utils/lessonAttachments.js'
let server, Video
before(async () => { server = await createTestServer(); Video = (await server.ssrLoadModule('/src/components/learning/LessonVideo.jsx')).VideoContent })
after(async () => server?.close())
test('native accessible video supports subtitles/poster and loading/error without autoplay',()=>{
 const asset={label:'Instruction',transcript:'Equivalent',caption:'Context'}
 const html=renderToStaticMarkup(createElement(Video,{asset,id:'v',playback:{url:'/api/lesson-attachments/8/playback/',subtitles:'/api/lesson-attachments/9/playback/'},poster:'blob:small-image'}))
 assert.match(html,/<video[^>]*controls=""/);assert.match(html,/aria-labelledby="v-label"/);assert.match(html,/kind="subtitles"/);assert.match(html,/Equivalent/);assert.match(html,/poster="blob:small-image"/);assert.doesNotMatch(html,/autoplay|Bearer|access_token/)
 assert.match(renderToStaticMarkup(createElement(Video,{asset,id:'v'})),/role="status"/)
 assert.match(renderToStaticMarkup(createElement(Video,{asset,id:'v',playback:{error:'unauthorized'}})),/role="alert"/)
})
test('grant uses sameorigin authenticated API; obsolete requests cannot supply media',async()=>{
 const calls=[],loaded=[]
 const req=requestVideoPlayback({post:async(...args)=>{calls.push(args);return {data:{url:'/api/lesson-attachments/8/playback/'}}}},8,data=>loaded.push(data),()=>assert.fail('unexpected failure'));await req.promise
 assert.equal(calls[0][2].baseURL,'/api');assert.equal(calls[0][2].signal,undefined);assert.equal(loaded.length,1)
 let resolve
 const late=requestVideoPlayback({post:()=>new Promise(r=>resolve=r)},8,()=>assert.fail('obsolete callback'),()=>assert.fail('obsolete error'));late.dispose();resolve({data:{url:'/api/lesson-attachments/8/playback/'}});await late.promise
 for(const value of ['https://evil.test/x','//evil.test','/media/private.mp4','/api/lesson-attachments/8/playback/?token=secret'])assert.equal(safePlaybackPath(value),null)
 for(const status of [401,403,500]){let failure;const failed=requestVideoPlayback({post:async()=>{throw {response:{status}}}},8,()=>assert.fail('unexpected source'),e=>failure=e);await failed.promise;assert.equal(failure.response.status,status)}
})
test('unique same-section VTT pairs inline without duplicate track card or audio changes',()=>{
 const audio={id:1,kind:'audio',after_section:'A'},video={id:2,kind:'video',after_section:'A'},vtt={id:3,kind:'vtt',after_section:'A'}
 const layout=attachmentLayout({attachments:[audio,video,vtt]},[{heading:'A'}]);assert.equal(layout.bySection.get('A').length,2);assert.equal(layout.bySection.get('A')[1].subtitle_attachment_id,3)
 const ambiguous=attachmentLayout({attachments:[video,{...video,id:4},vtt]},[{heading:'A'}]);assert.equal(ambiguous.bySection.get('A')[0].subtitle_attachment_id,undefined)
})
test('grant cleanup revokes the exact capability without another account JWT, including late grants',async()=>{
 const originalFetch=globalThis.fetch, revoked=[]
 globalThis.fetch=async(url,options)=>{revoked.push([url,options]);return {ok:true}}
 try {
  const request=requestVideoPlayback({post:async()=>({data:{url:'/api/lesson-attachments/8/playback/',revoke_token:'revocation-only-proof'}})},8,()=>{},()=>assert.fail())
  await request.promise;request.dispose()
  assert.equal(revoked.length,1);assert.deepEqual(JSON.parse(revoked[0][1].body),{revoke_token:'revocation-only-proof'});assert.equal(revoked[0][1].headers.Authorization,undefined)
  let resolve
  const late=requestVideoPlayback({post:()=>new Promise(r=>resolve=r)},8,()=>assert.fail(),()=>assert.fail());late.dispose();resolve({data:{url:'/api/lesson-attachments/8/playback/',revoke_token:'late-proof'}});await late.promise
  assert.equal(revoked.length,2);assert.deepEqual(JSON.parse(revoked[1][1].body),{revoke_token:'late-proof'})
 } finally {globalThis.fetch=originalFetch}
})

test('scoped playback paths accept non-secret selectors and reject credential URLs',()=>{
 for(const path of ['/api/lesson-attachments/8/playback/21/','/api/lesson-attachments/9/playback/22/'])assert.equal(safePlaybackPath(path),path)
 for(const path of ['/api/lesson-attachments/8/playback/0/','/api/lesson-attachments/8/playback/secret/','/api/lesson-attachments/8/playback/21/?token=x','//evil.test/api/lesson-attachments/8/playback/21/'])assert.equal(safePlaybackPath(path),null)
 // New frontend can still talk to an old backend; it never invents public paths.
 assert.equal(safePlaybackPath('/api/lesson-attachments/8/playback/'),'/api/lesson-attachments/8/playback/')
})

test('late disposed A cookie and cleanup cannot invalidate active B for the same attachment',async()=>{
 const originalFetch=globalThis.fetch, pending=[], cookies=new Map(),revoked=new Set(),loaded=[]
 globalThis.fetch=async(_url,options)=>{const proof=JSON.parse(options.body).revoke_token;revoked.add(proof);cookies.delete(proof);return {ok:true}}
 const client={post:()=>new Promise(resolve=>pending.push(proof=>{cookies.set(proof,true);resolve({data:{url:`/api/lesson-attachments/8/playback/${proof}/`,revoke_token:proof}})}))}
 try{
  const a=requestVideoPlayback(client,8,()=>assert.fail('obsolete callback'),()=>assert.fail());a.dispose()
  const b=requestVideoPlayback(client,8,data=>loaded.push(data),()=>assert.fail())
  pending[1]('22');await b.promise;pending[0]('21');await a.promise
  assert.deepEqual(loaded.map(v=>v.url),['/api/lesson-attachments/8/playback/22/'])
  assert.ok(cookies.has('22'));assert.ok(!revoked.has('22'));assert.ok(revoked.has('21'))
  b.dispose();assert.ok(revoked.has('22'));assert.equal(cookies.size,0)
 }finally{globalThis.fetch=originalFetch}
})

test('independent players and paired subtitles dispose only their own grant slots',async()=>{
 const originalFetch=globalThis.fetch,revoked=[];let gid=30
 globalThis.fetch=async(_url,options)=>{revoked.push(JSON.parse(options.body).revoke_token);return {ok:true}}
 const client={post:async path=>{const id=path.split('/')[2],slot=++gid;return {data:{url:`/api/lesson-attachments/${id}/playback/${slot}/`,revoke_token:String(slot)}}}}
 try{
  const loads=[]
  const one=requestVideoPlayback(client,8,v=>loads.push(v),()=>assert.fail(),9)
  const two=requestVideoPlayback(client,10,v=>loads.push(v),()=>assert.fail())
  const three=requestVideoPlayback(client,11,v=>loads.push(v),()=>assert.fail())
  await Promise.all([one.promise,two.promise,three.promise]);assert.equal(loads.length,3)
  assert.ok(loads.some(v=>v.subtitles?.startsWith('/api/lesson-attachments/9/playback/')))
  one.dispose();assert.equal(revoked.length,2)
  two.dispose();three.dispose();assert.equal(new Set(revoked).size,4)
 }finally{globalThis.fetch=originalFetch}
})
