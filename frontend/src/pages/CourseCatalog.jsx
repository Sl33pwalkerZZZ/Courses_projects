import { useEffect, useState } from 'react'
import { ArrowDown, ArrowUpRight, BookOpen, Library, SearchX } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '../api'
import AmbientBackground from '../components/AmbientBackground'
import CatalogFilters from '../components/CatalogFilters'
import CourseCard from '../components/CourseCard'
import Reveal from '../components/Reveal'
import './CourseCatalog.css'

function courseCountLabel(count) {
  if (count % 100 >= 11 && count % 100 <= 14) return `${count} курсов`
  if (count % 10 === 1) return `${count} курс`
  if (count % 10 >= 2 && count % 10 <= 4) return `${count} курса`
  return `${count} курсов`
}

export default function CourseCatalog() {
  const [courses, setCourses] = useState(null)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [level, setLevel] = useState('')
  const [direction, setDirection] = useState('')
  const [retry, setRetry] = useState(0)

  useEffect(() => {
    let active = true
    api.get('/courses/')
      .then((res) => { if (active) setCourses(res.data) })
      .catch(() => { if (active) setError('Не удалось загрузить каталог. Проверьте соединение и попробуйте ещё раз.') })
    return () => { active = false }
  }, [retry])

  // Search and filters use the existing response; no extra API requests.
  const query = search.trim().toLocaleLowerCase('ru')
  const visibleCourses = (courses || []).filter((course) => (
    `${course.title} ${course.description}`.toLocaleLowerCase('ru').includes(query)
    && (!level || course.level === level)
    && (!direction || course.direction.slug === direction)
  ))
  const directions = [...new Map((courses || []).map((course) => (
    [course.direction.slug, course.direction]
  ))).values()].sort((a, b) => a.name.localeCompare(b.name, 'ru'))
  const hasFilters = Boolean(search || level || direction)

  function resetFilters() {
    setSearch('')
    setLevel('')
    setDirection('')
  }

  function retryLoading() {
    setError(null)
    setCourses(null)
    setRetry((value) => value + 1)
  }

  return (
    <div className="catalog-page">
      <AmbientBackground />
      <section className="catalog-hero" aria-labelledby="hero-title">
        <Reveal className="hero-copy">
          <p className="eyebrow"><span className="status-dot" /> ЗНАНИЯ ДЛЯ ЭПОХИ AI</p>
          <h1 id="hero-title">Новый интеллект.<br /><em>Ваши возможности.</em></h1>
          <p className="hero-description">
            Искусственный интеллект становится частью нашей работы.
            Научитесь применять его осмысленно — в учёбе, бизнесе и повседневных задачах.
          </p>
          <div className="hero-actions">
            <a className="academic-button" href="#course-library">Исследовать курсы <ArrowDown size={17} aria-hidden="true" /></a>
            <Link className="hero-secondary" to="/register">Начать обучение <ArrowUpRight size={16} aria-hidden="true" /></Link>
          </div>
          <div className="hero-note"><BookOpen size={16} aria-hidden="true" /> Практические знания. В вашем темпе.</div>
        </Reveal>
        <Reveal className="research-visual" delay={0.12}>
          <div className="research-topline"><span>ПОЛЕ ИССЛЕДОВАНИЙ</span><span>AI / 01</span></div>
          <div className="research-orbit" aria-hidden="true">
            <div className="orbit-ring orbit-ring-one" />
            <div className="orbit-ring orbit-ring-two" />
            <div className="orbit-ring orbit-ring-three" />
            <div className="orbit-axis" />
            <div className="orbit-core"><span>AI</span><small>human potential</small></div>
            <span className="orbit-node node-one" /><span className="orbit-node node-two" />
            <span className="orbit-label label-one">ЗНАНИЯ</span>
            <span className="orbit-label label-two">ПРАКТИКА</span>
            <span className="orbit-label label-three">ВОЗМОЖНОСТИ</span>
          </div>
          <div className="research-caption"><span className="caption-line" /> На пересечении человека и технологий</div>
        </Reveal>
      </section>
      <Reveal className="platform-intro">
        <span className="eyebrow">ОТ ТЕОРИИ К ПРАКТИКЕ</span>
        <p>Цифровая библиотека для тех, кто хочет понимать AI и применять его:
          от LLM и автоматизации до управления знаниями и личной продуктивности.</p>
      </Reveal>
      <section id="course-library" className="course-library" aria-labelledby="library-title" aria-busy={!courses && !error}>
        <Reveal className="library-heading">
          <div><p className="eyebrow">ВЫБЕРИТЕ СВОЁ НАПРАВЛЕНИЕ</p><h2 id="library-title">Каталог знаний</h2></div>
          <span className="course-count"><Library size={17} aria-hidden="true" />{courses ? courseCountLabel(courses.length) : 'Каталог курсов'}</span>
        </Reveal>
        <CatalogFilters search={search} onSearchChange={setSearch} level={level} onLevelChange={setLevel}
          direction={direction} onDirectionChange={setDirection} directions={directions}
          hasFilters={hasFilters} onReset={resetFilters} />
        <p className="catalog-results" role="status">
          {error ? 'Каталог временно недоступен' : !courses ? 'Загружаем библиотеку…'
            : hasFilters ? `Найдено: ${courseCountLabel(visibleCourses.length)}` : 'Откройте тему, которая вам интересна'}
        </p>
        {error ? (
          <div className="catalog-state" role="alert">
            <Library size={32} aria-hidden="true" /><h3>Библиотека скоро вернётся</h3><p>{error}</p>
            <button className="academic-button" onClick={retryLoading}>Попробовать снова</button>
          </div>
        ) : !courses ? (
          <div className="academic-course-grid" aria-hidden="true">
            {[0, 1, 2].map((index) => <div key={index} className="course-skeleton"><div /><span /><span /><span /></div>)}
          </div>
        ) : visibleCourses.length === 0 ? (
          <div className="catalog-state">
            <SearchX size={32} aria-hidden="true" />
            <h3>{hasFilters ? 'Попробуем другое направление?' : 'Библиотека готовится к открытию'}</h3>
            <p>{hasFilters ? 'Измените запрос или сбросьте фильтры, чтобы увидеть доступные курсы.' : 'Новые курсы появятся здесь после публикации. Загляните немного позже.'}</p>
            {hasFilters && <button className="academic-button" onClick={resetFilters}>Сбросить фильтры</button>}
          </div>
        ) : (
          <div className="academic-course-grid">
            {visibleCourses.map((course, index) => <CourseCard key={course.id} course={course} index={index} />)}
          </div>
        )}
      </section>
      <footer className="catalog-footer"><span>AI Courses</span><span>Любопытство — начало любого открытия.</span></footer>
    </div>
  )
}
