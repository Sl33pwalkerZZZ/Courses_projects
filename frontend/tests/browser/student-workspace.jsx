// No credentials, private endpoints or account impersonation: presentation only.
import React from 'react'
import { createRoot } from 'react-dom/client'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import i18n from '../../src/i18n'
import ThemeProvider from '../../src/theme/ThemeProvider'
import LessonCourseSidebar from '../../src/components/LessonCourseSidebar'
import { LessonMaterial } from '../../src/pages/LessonView'
import { EnrollmentCard } from '../../src/pages/Profile'
import { VideoContent } from '../../src/components/learning/LessonVideo'
import { AttachmentContent } from '../../src/components/learning/LessonAttachment'
import { VerificationDetails } from '../../src/pages/CertificateVerification'
import '../../src/index.css'
import '../../src/styles/v2-tokens.css'
import '../../src/styles/playground.css'
import '../../src/styles/amethyst-motion.css'
const params=new URLSearchParams(location.search)
i18n.changeLanguage(params.get('lang')||'ru')
document.documentElement.dataset.theme=params.get('theme')||'dark'
localStorage.setItem('ai-courses-theme',params.get('theme')||'dark')
const headings=['1. Учебное объяснение','2. Сравнение вариантов','3. Необязательная практика']
const lesson={id:999001,title:'Учебный материал: читаем, сравниваем и применяем',text_content:headings.map((h,i)=>h+'\n\n'+['Это синтетический текст для проверки читательского интерфейса. Он не относится к реальному курсу и не сохраняется в базу данных.','Вариант: Первый; Проверка: Сопоставьте условия\n\nВариант: Второй; Проверка: Найдите отличия','Практика выполняется по желанию. Это пример оформления инструкции, а не реальное задание.'][i]).join('\n\n'),learning_content:{content_language:'ru',objectives:['Прочитать пример','Сравнить варианты','Проверить понимание'],source_sections:headings,interactions:[]},images:[],assignments:[],attachments:[]}
const course={id:999000,slug:'synthetic-fixture',title:'Синтетический пример для проверки интерфейса',description:'Не является реальной записью курса.',author:'Fixture author',level:'beginner',direction:{name:'Учебные материалы'},modules:[{id:999010,order:1,title:'Учебный модуль',lessons:[lesson,{id:999002,order:2,title:'Следующий пример'}]}]}
const enrollment={id:999020,course,total_lessons:2,completed_lessons:1,progress_percent:50,is_completed:false,next_lesson_id:lesson.id,next_lesson_title:lesson.title}
export function StudentFixture(){return <main className="container legacy-page"><p style={{fontSize:12}}>Isolated presentation fixture — no account, API or database access</p>{params.get('page')==='profile'?<section className="profile-page"><header className="profile-heading"><p className="eyebrow">AI Courses</p><h1>{i18n.t('header.profile')}</h1><div className="profile-account"><span className="profile-avatar">Q</span><div><p className="profile-username">Fixture learner</p><p>Not a real account</p></div></div></header><div className="academic-course-grid"><EnrollmentCard enrollment={enrollment}/></div><section className="certificate-section"><h2>{i18n.t('certificates.myTitle')}</h2><p>{i18n.t('certificates.empty')}</p></section></section>:params.get('page')==='certificate'?<section className="certificate-verification"><h1>{i18n.t('certificates.verificationTitle')}</h1><VerificationDetails certificate={{status:params.get('status')||'valid',learner_initials:'Q. A.',course_title:course.title,issuer_name:'Fixture issuer',issued_at:'2026-11-03T00:00:00Z'}}/></section>:<div className="lesson-workspace"><div className="lesson-workspace-grid"><LessonCourseSidebar course={course} lessonId={lesson.id} enrollment={enrollment} completedIds={[999002]} onRefresh={()=>{}}/><article className="lesson-reading-area"><header className="lesson-reading-header"><p className="eyebrow">AI Courses</p><h1 id="lesson-title">{lesson.title}</h1></header><LessonMaterial lesson={lesson}/><p>Media presentation fixture — no playable media or protected requests</p><VideoContent asset={{label:'Fixture video player',transcript:'Fixture text equivalent'}} id="fixture-video" playback={null} onRetry={()=>{}} onError={()=>{}}/><AttachmentContent asset={{kind:'audio',label:'Fixture audio example',transcript:'Fixture audio transcript'}} id="fixture-audio"/><AttachmentContent asset={{kind:'srt',label:'Fixture subtitles',filename:'fixture.srt'}} id="fixture-srt" onRetry={()=>{}}/><nav className="lesson-pagination"><a className="lesson-pagination-link" href="#lesson-title">{i18n.t('lessonWorkspace.backToCourse')}</a></nav></article></div></div>}</main>}
createRoot(document.getElementById('root')).render(<I18nextProvider i18n={i18n}><ThemeProvider><MemoryRouter><StudentFixture/></MemoryRouter></ThemeProvider></I18nextProvider>)
