import assert from 'node:assert/strict'
import { after, before, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { I18nextProvider } from 'react-i18next'
import { createInstance } from 'i18next'
import { createTestServer } from './helpers/vite.mjs'
import { lessonImagePlacements } from '../src/utils/lessonImagePlacements.js'
import { mediaLessonSections } from '../src/utils/mediaLessonPresentation.js'

const lesson = {title:'Any lesson',text_content:'First section\n\nOriginal theory\n\nNext section\n\nContinued theory',
 images:[{id:7,alt_text:{ru:'Схема процесса'}},{id:8,alt_text:{ru:'Другая схема'}}],
 learning_content:{content_language:'ru',source_sections:['First section','Next section'],interactions:[
 {type:'image_placement',image_id:7,after_section:'First section',caption:'Authored explanatory caption'}]}}
let server, Material
const i18n=createInstance()
before(async()=>{
 await i18n.init({lng:'ru',resources:{ru:{translation:{common:{loading:'Загрузка'}}}}})
 server=await createTestServer()
 Material=(await server.ssrLoadModule('/src/pages/LessonView.jsx')).LessonMaterial
})
after(async()=>{await server?.close()})

test('explicit placement uses authorized image ID and removes only that image from gallery',()=>{
 const sections=mediaLessonSections(lesson)
 assert.ok(sections)
 const result=lessonImagePlacements(lesson,sections)
 assert.equal(result.bySection.get('First section')[0].image.id,7)
 assert.deepEqual(result.gallery.map(i=>i.id),[8])
})

test('invalid references, anchors and duplicate placements preserve a sensible fallback',()=>{
 const section=mediaLessonSections(lesson)
 const placements=lesson.learning_content.interactions
 for(const bad of [{...placements[0],image_id:999},{...placements[0],after_section:'Missing'}, {...placements[0],caption:''}]){
  const result=lessonImagePlacements({...lesson,learning_content:{...lesson.learning_content,interactions:[bad]}},section)
  assert.equal(result.gallery.length,2)
  assert.equal(result.bySection.size,0)
 }
 const repeated=lessonImagePlacements({...lesson,learning_content:{...lesson.learning_content,interactions:[...placements,...placements]}},section)
 assert.equal(repeated.bySection.get('First section').length,1)
 assert.equal(lessonImagePlacements(lesson,null).gallery.length,2)
})

test('caption and figure appear between original theory sections without a duplicate teaching card',()=>{
 const html=renderToStaticMarkup(createElement(I18nextProvider,{i18n},createElement(Material,{lesson})))
 assert.equal((html.match(/<figure /g)||[]).length,1)
 assert.equal((html.match(/Authored explanatory caption/g)||[]).length,1)
 assert.ok(html.indexOf('Original theory')<html.indexOf('<figure'))
 assert.ok(html.indexOf('</figure>')<html.indexOf('Next section'))
 assert.match(html,/<figcaption>Authored explanatory caption<\/figcaption>/)
 assert.match(html,/Continued theory/)
 assert.match(html,/lesson-material-images/)
 assert.doesNotMatch(html,/learning-interaction/)
})

test('lessons without placements retain the original gallery and text',()=>{
 const without={...lesson,learning_content:{...lesson.learning_content,interactions:[]}}
 const html=renderToStaticMarkup(createElement(I18nextProvider,{i18n},createElement(Material,{lesson:without})))
 assert.doesNotMatch(html,/<figure/)
 assert.match(html,/lesson-material-images/)
 assert.match(html,/Original theory/)
 assert.equal(lessonImagePlacements(without,mediaLessonSections(without)).gallery.length,2)
})
