import assert from 'node:assert/strict'
import { before,after,test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { readFile } from 'node:fs/promises'
import { createInstance } from 'i18next'
import { I18nextProvider } from 'react-i18next'
import { createTestServer } from './helpers/vite.mjs'
let server, Reading, Navigation, Learning
before(async()=>{server=await createTestServer();Reading=(await server.ssrLoadModule('/src/components/learning/MediaLessonReading.jsx')).default;Navigation=(await server.ssrLoadModule('/src/components/learning/LessonSectionNavigation.jsx')).default;Learning=(await server.ssrLoadModule('/src/components/learning/LearningContent.jsx')).default})
after(async()=>{await server?.close()})
for(const lang of ['ru','kk','en'])test(`section navigation points to actual headings without changing content in ${lang}`,async()=>{
 const dict=JSON.parse(await readFile(new URL(`../src/i18n/locales/${lang}.json`,import.meta.url)));const i18n=createInstance();await i18n.init({lng:lang,resources:{[lang]:{translation:dict}},interpolation:{escapeValue:false}})
 const render=(Component,props)=>renderToStaticMarkup(createElement(I18nextProvider,{i18n},createElement(Component,props)))
 const sections=[{heading:'1. Объяснение',kind:'theory',blocks:[{type:'paragraph',kind:'paragraph',text:'Original paragraph <script>'}]},{heading:'2. Пример',kind:'example',blocks:[{type:'paragraph',kind:'paragraph',text:'Original second paragraph'}]}]
 const before=JSON.stringify(sections)
 const html=render(Reading,{sections})
 const targets=[...html.matchAll(/href="#([^"]+)"/g)].map(m=>decodeURIComponent(m[1]))
 assert.equal(targets.length,2)
 for(const target of targets)assert.ok(html.includes(`id="${target}" tabindex="-1"`))
 assert.ok(html.includes(dict.studentVisual.onThisPage));assert.match(html,/Original paragraph &lt;script&gt;/)
 assert.match(html,/Original second paragraph/);assert.equal(JSON.stringify(sections),before)
 assert.equal(render(Navigation,{sections:sections.slice(0,1),prefix:'test'}),'')
 const objectives=render(Learning,{content:{objectives:['Original objective'],content_language:'ru'},showLanguageNotice:false})
 assert.match(objectives,/class="learning-objectives"/);assert.match(objectives,/Original objective/)
})
