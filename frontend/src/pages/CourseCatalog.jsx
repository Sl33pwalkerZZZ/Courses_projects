import { useEffect, useState } from 'react'
import { Library } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import api from '../api'
import CatalogFilters from '../components/CatalogFilters'
import CourseCard from '../components/CourseCard'
import HomeHero from '../components/HomeHero'
import Badge from '../components/ui/Badge'
import { CatalogSkeleton, CatalogState } from '../components/CatalogState'
import LearningWorkflow from '../components/LearningWorkflow'
import SignalStory from '../components/motion/SignalStory'
import DiscoveryDirections from '../components/motion/DiscoveryDirections'
import AnimatedText from '../components/motion/AnimatedText'
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
    <div className="catalog-page v2-scope">
      <HomeHero />
      <SignalStory />
      <section id="course-library" className="course-library" aria-labelledby="library-title" aria-busy={!courses && !error}>
        <div className="library-heading studio-section-heading">
          <div><p className="studio-eyebrow">{t('studio.libraryLabel')}</p><h2 id="library-title"><AnimatedText text={t('studio.libraryTitle')} /></h2>
            <p className="studio-section-description">{t('studio.libraryDescription')}</p></div>
          <Badge className="course-count"><Library size={16} aria-hidden="true" />{courses ? t('catalog.courseCount', { count: courses.length }) : t('header.catalog')}</Badge>
        </div>
        <DiscoveryDirections directions={directions} selected={direction} onSelect={setDirection} />
        <CatalogFilters search={search} onSearchChange={setSearch} level={level} onLevelChange={setLevel}
          direction={direction} onDirectionChange={setDirection} directions={directions}
          hasFilters={hasFilters} onReset={resetFilters} />
        <p className="catalog-results" role="status">
          {error ? t('catalog.unavailable') : !courses ? t('catalog.loading')
            : hasFilters ? t('catalog.found', { courses: t('catalog.courseCount', { count: visibleCourses.length }) }) : t('catalog.prompt')}
        </p>
        {error ? (
          <CatalogState kind="error" onAction={retryLoading} />
        ) : !courses ? (
          <CatalogSkeleton />
        ) : visibleCourses.length === 0 ? (
          <CatalogState kind={hasFilters ? 'filtered' : 'empty'} onAction={resetFilters} />
        ) : (
          <div className="academic-course-grid">
            {visibleCourses.map((course, index) => <CourseCard key={course.id} course={course} index={index} />)}
          </div>
        )}
      </section>
      <LearningWorkflow />
    </div>
  )
}
