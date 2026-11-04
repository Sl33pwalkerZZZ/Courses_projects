// Isolated presentation fixtures only: no JWT, API adapters or real account access.
import React from 'react'
import { createRoot } from 'react-dom/client'
import { MemoryRouter, Routes, Route, useLocation } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import i18n from '../../src/i18n'
import StudioNavigation from '../../src/components/instructor/StudioNavigation'
import StudioDashboard from '../../src/components/instructor/StudioDashboard'
import StudioCourseCollection from '../../src/components/instructor/StudioCourseCollection'
import '../../src/index.css'
import '../../src/styles/v2-tokens.css'
import '../../src/pages/instructor/instructor.css'
import '../../src/pages/instructor/studio-command.css'
const params = new URLSearchParams(location.search)
const lang = params.get('lang') || 'ru'
i18n.changeLanguage(lang)
document.documentElement.dataset.theme = params.get('theme') || 'dark'
const identity = { is_moderator: params.get('role') === 'admin', can_manage_instructors: params.get('role') === 'admin' }
const courses = [1,2,3].map((id,index)=>({ id:900000+id, title:['Учебный медиапроект: от идеи до готового материала','Практические методы работы с ИИ','Подготовка и проверка учебного материала'][index], description:'Синтетический пример для проверки интерфейса. Это не запись курса в базе данных.', slug:`fixture-${id}`, direction:{name:'Учебные материалы'}, is_published:index===1, language:'ru',level:'beginner',module_count:5,lesson_count:15 }))
const ready = data => ({ data,loading:false,error:'',reload(){} })
const resource = params.get('state') === 'loading' ? {loading:true} : params.get('state') === 'error' ? {error:'Isolated network error',reload(){}} : ready(params.get('state') === 'empty'?[]:courses)
export function Destination(){const {pathname}=useLocation();return <p role="status" data-destination>{pathname}</p>}
export function Fixture(){return <main className="container"><p style={{fontSize:12}}>Isolated presentation fixture — no account, no API or database access</p><section className="instructor-studio studio-command-shell"><header className="instructor-heading"><div><p className="eyebrow">AI Courses / Studio</p><h1>{i18n.t('instructorStudio.title')}</h1><p>{i18n.t('instructorStudio.intro')}</p><p className="instructor-badge">{params.get('role')==='admin'?'Admin':'Author'} — fixture</p></div></header><StudioNavigation identity={identity}/><Routes><Route path="/instructor" element={<StudioDashboard moderator={identity.is_moderator} metrics={ready({courses:3,published:1,drafts:2,pending_publications:0,pending_submissions:0})} projects={resource}/>} /><Route path="/instructor/courses" element={<StudioCourseCollection courses={courses}/>} /><Route path="*" element={<Destination/>}/></Routes></section></main>}
createRoot(document.getElementById('root')).render(<I18nextProvider i18n={i18n}><MemoryRouter initialEntries={['/instructor']}><Fixture/></MemoryRouter></I18nextProvider>)
