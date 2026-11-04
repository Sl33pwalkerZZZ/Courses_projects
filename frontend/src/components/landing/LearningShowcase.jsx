import { useState } from 'react'
import { ArrowUpRight, ArrowDown } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import Reveal from '../Reveal'
import DepthSurface from './DepthSurface'
import LandingCoursePreview from './LandingCoursePreview'

export default function LearningShowcase({ courses, failed }) {
  const { t } = useTranslation()
  const [selectedId, setSelectedId] = useState(null)
  const visible = (courses || []).slice(0, 4)
  const selected = visible.find(course => course.id === selectedId) || visible[0]
  return <section id="learning-showcase" className="cinema-showcase" aria-labelledby="showcase-title">
    <Reveal><header className="cinema-section-heading"><p className="cinema-kicker">{t('cinema.showcaseLabel')}</p>
      <h2 id="showcase-title">{t('cinema.showcaseTitle')}</h2><p>{t('cinema.showcaseDescription')}</p></header></Reveal>
    <p className="sr-only" role="status">{selected ? `${t('cinema.overview')}: ${selected.title}` : ''}</p>
    <div className="cinema-showcase-grid">
      <div className="cinema-course-choices" role="group" aria-label={t('cinema.chooseCourse')}>
        {visible.map((course, index) => <button key={course.id} type="button" aria-pressed={course.id === selected?.id}
          onClick={() => setSelectedId(course.id)}><span className="cinema-choice-number" aria-hidden="true">0{index + 1}</span>
          <span><small>{course.direction.name}</small><strong>{course.title}</strong></span><ArrowUpRight size={18} aria-hidden="true" /></button>)}
        {!visible.length && <p>{t(failed ? 'catalog.unavailable' : !courses ? 'catalog.loading' : 'cinema.previewDescription')}</p>}
        <a href="#course-library" className="cinema-show-all">{t('catalog.explore')}<ArrowDown size={16} aria-hidden="true" /></a>
      </div>
      <DepthSurface><LandingCoursePreview course={selected} loading={!courses && !failed} failed={failed} /></DepthSurface>
    </div>
  </section>
}
