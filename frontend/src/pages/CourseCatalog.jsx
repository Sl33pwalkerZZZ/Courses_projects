import { useEffect, useState } from 'react'
import { ArrowDown, ArrowUpRight, BookOpen, Library, SearchX } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../api'
import AmbientBackground from '../components/AmbientBackground'
import CatalogFilters from '../components/CatalogFilters'
import CourseCard from '../components/CourseCard'
import Reveal from '../components/Reveal'
import './CourseCatalog.css'

export default function CourseCatalog() {
  const { t, i18n } = useTranslation()
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
      .catch(() => { if (active) setError('catalog.error') })
    return () => { active = false }
  }, [retry])

  // Search and filters use the existing response; no extra API requests.
  const query = search.trim().toLocaleLowerCase(i18n.resolvedLanguage)
  const visibleCourses = (courses || []).filter((course) => (
    `${course.title} ${course.description}`.toLocaleLowerCase(i18n.resolvedLanguage).includes(query)
    && (!level || course.level === level)
    && (!direction || course.direction.slug === direction)
  ))
  const directions = [...new Map((courses || []).map((course) => (
    [course.direction.slug, course.direction]
  ))).values()].sort((a, b) => a.name.localeCompare(b.name, i18n.resolvedLanguage))
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
          <p className="eyebrow"><span className="status-dot" /> {t('catalog.eyebrow')}</p>
          <h1 id="hero-title">{t('catalog.title')}<br /><em>{t('catalog.subtitle')}</em></h1>
          <p className="hero-description">
            {t('catalog.description')}
          </p>
          <div className="hero-actions">
            <a className="academic-button" href="#course-library">{t('catalog.explore')} <ArrowDown size={17} aria-hidden="true" /></a>
            <Link className="hero-secondary" to="/register">{t('catalog.start')} <ArrowUpRight size={16} aria-hidden="true" /></Link>
          </div>
          <div className="hero-note"><BookOpen size={16} aria-hidden="true" /> {t('catalog.note')}</div>
        </Reveal>
        <Reveal className="research-visual" delay={0.12}>
          <div className="research-topline"><span>{t('catalog.research')}</span><span>AI / 01</span></div>
          <div className="research-orbit" aria-hidden="true">
            <div className="orbit-ring orbit-ring-one" />
            <div className="orbit-ring orbit-ring-two" />
            <div className="orbit-ring orbit-ring-three" />
            <div className="orbit-axis" />
            <div className="orbit-core"><span>AI</span><small>{t('catalog.potential')}</small></div>
            <span className="orbit-node node-one" /><span className="orbit-node node-two" />
            <span className="orbit-label label-one">{t('catalog.knowledge')}</span>
            <span className="orbit-label label-two">{t('catalog.practice')}</span>
            <span className="orbit-label label-three">{t('catalog.possibilities')}</span>
          </div>
          <div className="research-caption"><span className="caption-line" /> {t('catalog.caption')}</div>
        </Reveal>
      </section>
      <Reveal className="platform-intro">
        <span className="eyebrow">{t('catalog.introLabel')}</span>
        <p>{t('catalog.intro')}</p>
      </Reveal>
      <section id="course-library" className="course-library" aria-labelledby="library-title" aria-busy={!courses && !error}>
        <Reveal className="library-heading">
          <div><p className="eyebrow">{t('catalog.libraryLabel')}</p><h2 id="library-title">{t('catalog.libraryTitle')}</h2></div>
          <span className="course-count"><Library size={17} aria-hidden="true" />{courses ? t('catalog.courseCount', { count: courses.length }) : t('header.catalog')}</span>
        </Reveal>
        <CatalogFilters search={search} onSearchChange={setSearch} level={level} onLevelChange={setLevel}
          direction={direction} onDirectionChange={setDirection} directions={directions}
          hasFilters={hasFilters} onReset={resetFilters} />
        <p className="catalog-results" role="status">
          {error ? t('catalog.unavailable') : !courses ? t('catalog.loading')
            : hasFilters ? t('catalog.found', { courses: t('catalog.courseCount', { count: visibleCourses.length }) }) : t('catalog.prompt')}
        </p>
        {error ? (
          <div className="catalog-state" role="alert">
            <Library size={32} aria-hidden="true" /><h3>{t('catalog.errorTitle')}</h3><p>{t(error)}</p>
            <button className="academic-button" onClick={retryLoading}>{t('common.retry')}</button>
          </div>
        ) : !courses ? (
          <div className="academic-course-grid" aria-hidden="true">
            {[0, 1, 2].map((index) => <div key={index} className="course-skeleton"><div /><span /><span /><span /></div>)}
          </div>
        ) : visibleCourses.length === 0 ? (
          <div className="catalog-state">
            <SearchX size={32} aria-hidden="true" />
            <h3>{t(hasFilters ? 'catalog.emptyTitle' : 'catalog.noCoursesTitle')}</h3>
            <p>{t(hasFilters ? 'catalog.emptyDescription' : 'catalog.noCoursesDescription')}</p>
            {hasFilters && <button className="academic-button" onClick={resetFilters}>{t('common.reset')}</button>}
          </div>
        ) : (
          <div className="academic-course-grid">
            {visibleCourses.map((course, index) => <CourseCard key={course.id} course={course} index={index} />)}
          </div>
        )}
      </section>
      <footer className="catalog-footer"><span>AI Courses</span><span>{t('catalog.footer')}</span></footer>
    </div>
  )
}
