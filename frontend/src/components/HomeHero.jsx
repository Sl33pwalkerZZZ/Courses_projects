import { useRef } from 'react'
import { ArrowDown, ArrowUpRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import Button from './ui/Button'
import AsciiLearning from './landing/AsciiLearning'
import useHeroDepth from '../hooks/useHeroDepth'
import './HomeHero.css'

export default function HomeHero() {
  const { t } = useTranslation()
  const section = useRef(null)
  useHeroDepth(section)
  return <section ref={section} className="gl-hero" aria-labelledby="hero-title">
    <div className="gl-hero-heading"><h1 id="hero-title">{t('landing.title')}<span>{t('landing.titleEnd')}</span></h1></div>
    <div className="gl-hero-visual"><AsciiLearning/><p className="gl-visual-caption">{t('liquid.visualCaption')}</p></div>
    <div className="gl-hero-copy"><p className="gl-hero-description">{t('landing.description')}</p>
      <div className="gl-hero-actions"><Button href="#course-library">{t('catalog.explore')}<ArrowUpRight size={18} aria-hidden="true"/></Button><a href="#learning-workflow">{t('landing.how')}<ArrowDown size={16} aria-hidden="true"/></a></div>
      <p className="gl-hero-note">{t('landing.note')}</p>
    </div>
    <ol className="gl-hero-stages" aria-label={t('liquid.visualCaption')}><li>{t('landing.information')}</li><li>{t('landing.structure')}</li><li>{t('landing.practice')}</li></ol>
  </section>
}
