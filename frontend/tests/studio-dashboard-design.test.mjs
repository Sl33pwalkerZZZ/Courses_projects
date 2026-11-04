import assert from 'node:assert/strict'
import { before, after, test } from 'node:test'
import { readFile } from 'node:fs/promises'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
let server, Nav, Dashboard, Collection
before(async()=>{server=await createTestServer();Nav=(await server.ssrLoadModule('/src/components/instructor/StudioNavigation.jsx')).default;Dashboard=(await server.ssrLoadModule('/src/components/instructor/StudioDashboard.jsx')).default;Collection=(await server.ssrLoadModule('/src/components/instructor/StudioCourseCollection.jsx')).default})
after(async()=>{await server?.close()})
const course={id:9001,title:'Existing course <script>',description:'Existing content',language:'ru',direction:{name:'Media'},is_published:false,module_count:5,lesson_count:15,level:'beginner'}
const ready=data=>({data,loading:false,error:'',reload(){}})
for(const lang of ['ru','kk','en']){
 test(`Studio navigation and course actions retain roles and routes in ${lang}`,async()=>{
  const dict=JSON.parse(await readFile(new URL(`../src/i18n/locales/${lang}.json`,import.meta.url)));const i18n=createInstance();await i18n.init({lng:lang,resources:{[lang]:{translation:dict}},interpolation:{escapeValue:false}})
  const render=(Component,props)=>renderToStaticMarkup(createElement(I18nextProvider,{i18n},createElement(MemoryRouter,{initialEntries:['/instructor']},createElement(Component,props))))
  for(const admin of [false,true]){
   const html=render(Nav,{identity:{is_moderator:admin,can_manage_instructors:admin}})
   for(const path of ['/instructor','/instructor/courses','/instructor/submissions','/instructor/import'])assert.ok(html.includes(`href="${path}"`))
   for(const path of ['enrollment-requests','reviews','instructors'])assert.equal(html.includes(`href="/instructor/${path}"`),admin)
   assert.match(html,/aria-expanded="false" aria-controls=/)
   assert.match(html,/aria-current="page"/)
  }
  const roleOnly=render(Nav,{identity:{is_moderator:false,can_manage_instructors:true}})
  assert.match(roleOnly,/href="\/instructor\/instructors"/);assert.doesNotMatch(roleOnly,/href="\/instructor\/reviews"/)
  const html=render(Dashboard,{metrics:ready({courses:1,published:0,drafts:1,pending_publications:0,pending_submissions:0,revenue:9999}),projects:ready([course])})
  for(const path of ['/instructor/courses/9001/edit','/instructor/courses/9001/curriculum','/instructor/courses/new','/instructor/import','/instructor/submissions'])assert.ok(html.includes(`href="${path}"`))
  assert.match(html,/Existing course &lt;script&gt;/);assert.doesNotMatch(html,/9999|revenue|studioVisual\.|<script>/)
  assert.equal((html.match(/<dd>/g)||[]).length,8)
  const missing=render(Dashboard,{metrics:ready({courses:1}),projects:ready([])})
  assert.equal((missing.match(/<dd>/g)||[]).length,1)
  assert.ok(missing.includes(dict.instructorStudio.noCourses))
  const loading=render(Dashboard,{metrics:{loading:true},projects:{loading:true}})
  assert.match(loading,/role="status"/);assert.doesNotMatch(loading,/Existing course/)
  const error=render(Dashboard,{metrics:{error:'<private-error>',reload(){}},projects:ready([])})
  assert.match(error,/role="alert"/);assert.match(error,/&lt;private-error&gt;/)
  const metadataMissing=render(Collection,{courses:[{...course,module_count:undefined,lesson_count:undefined}]})
  assert.doesNotMatch(metadataMissing,/NaN|undefined/)
 })
}
