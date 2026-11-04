import { ArrowDown, ArrowUpRight, BookOpen, PencilLine, Route } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { motion } from 'motion/react'
import { useReducedMotion } from '../hooks/useMotionPreferences'
import Button from './ui/Button'
import AnimatedText from './motion/AnimatedText'
import ParticleField from './playground/ParticleField'
import DepthSurface from './landing/DepthSurface'
import LandingCoursePreview from './landing/LandingCoursePreview'
import './HomeHero.css'

export default function HomeHero({ courses = null, failed = false }) {
  const { t } = useTranslation()
  const reduced = useReducedMotion()
  return <section className="signal-hero cinema-hero" aria-labelledby="hero-title">
    <div className="cinema-spatial-grid" aria-hidden="true" /><ParticleField />
    <div className="signal-hero-copy">
      <p className="cinema-kicker"><span aria-hidden="true" />{t('cinema.eyebrow')}</p>
      <h1 id="hero-title"><AnimatedText text={t('cinema.title')} /><br /><AnimatedText className="signal-hero-title-accent" text={t('cinema.titleAccent')} /></h1>
      <p className="signal-hero-description">{t('cinema.description')}</p>
      <div className="signal-hero-actions">
        <Button href="#course-library">{t('catalog.explore')}<ArrowDown size={18} aria-hidden="true" /></Button>
        <Button href="#learning-workflow" variant="ghost">{t('cinema.howItWorks')}<ArrowUpRight size={18} aria-hidden="true" /></Button>
      </div>
    </div>
    <motion.div className="cinema-hero-visual" initial={reduced ? false : { y: 24 }} animate={{ y: 0 }}
      transition={{ duration: reduced ? 0 : .8, ease: [.2,.8,.2,1] }}>
      <div className="cinema-orbit cinema-orbit-one" aria-hidden="true" /><div className="cinema-orbit cinema-orbit-two" aria-hidden="true" />
      <DepthSurface><LandingCoursePreview course={courses?.[0]} loading={!courses && !failed} failed={failed} /></DepthSurface>
      <div className="cinema-learning-strip"><span><BookOpen size={16} aria-hidden="true" />{t('cinema.read')}</span><span><PencilLine size={16} aria-hidden="true" />{t('cinema.try')}</span><span><Route size={16} aria-hidden="true" />{t('cinema.continue')}</span></div>
    </motion.div>
    <a className="cinema-scroll-cue" href="#learning-showcase"><ArrowDown size={16} aria-hidden="true" />{t('cinema.scroll')}</a>
  </section>
}
