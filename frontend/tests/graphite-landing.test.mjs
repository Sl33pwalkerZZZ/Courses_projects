import assert from 'node:assert/strict'
import { before, after, test } from 'node:test'
import { readFileSync } from 'node:fs'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { createTestServer } from './helpers/vite.mjs'
let server, Catalog, Workflow
before(async()=>{ server=await createTestServer();Catalog=(await server.ssrLoadModule('/src/pages/CourseCatalog.jsx')).default;Workflow=(await server.ssrLoadModule('/src/components/LearningWorkflow.jsx')).default })
after(async()=>{await server?.close()})
for(const lang of ['ru','kk','en']) test(`landing narrative and catalog actions remain readable in ${lang}`,async()=>{
 const dictionary=JSON.parse(readFileSync(new URL(`../src/i18n/locales/${lang}.json`,import.meta.url)))
 const i18n=createInstance();await i18n.init({lng:lang,resources:{[lang]:{translation:dictionary}},interpolation:{escapeValue:false}})
 const render=c=>renderToStaticMarkup(createElement(I18nextProvider,{i18n},createElement(MemoryRouter,null,createElement(c))))
 const html=render(Catalog)
 assert.equal((html.match(/<h1\b/g)||[]).length,1)
 for(const key of ['title','titleEnd','description','workflowTitle','libraryTitle','closingTitle']) assert.ok(html.includes(dictionary.landing[key]),key)
 assert.ok(html.indexOf('id="learning-workflow"')<html.indexOf('id="course-library"'))
 assert.match(html,/href="#course-library"/);assert.match(html,/href="\/register"/)
 assert.match(html,/aria-busy="true"/);assert.match(html,/data-ascii-mode="static"/)
 assert.doesNotMatch(html,/particle-field|cinema-orbit|cinema-showcase|signal-story|landing\.[a-zA-Z]|completed_lessons/)
 const flow=render(Workflow);assert.equal((flow.match(/<li>/g)||[]).length,3)
})
test('normalized license bytes and upstream provenance stay pinned',async()=>{
 const { createHash }=await import('node:crypto')
 const current=readFileSync(new URL('../public/fonts/IBMPlexMono-OFL.txt',import.meta.url),'utf8')
 assert.equal(createHash('sha256').update(current).digest('hex'),'d741e57d5f865e294df801f96b7b5161a88b211df65887e4358d271c9fc5fb4f')
 assert.doesNotMatch(current,/\r|[ \t]+$/m)
 const manifest=JSON.parse(readFileSync(new URL('../public/fonts/provenance.json',import.meta.url)))
 assert.equal(manifest.ibm_plex_mono.files.find(x=>x.file==='OFL.txt').upstream_sha256,'7e6b2818edbd8f6a01ae80641cc8f16a51080d08fb4e532be3a0b6f74adb07da')
})
