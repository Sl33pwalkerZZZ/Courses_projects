import { ArrowDown, ArrowUpRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { motion, useReducedMotion } from 'motion/react'
import Button from './ui/Button'
import Badge from './ui/Badge'
import SignalMap from './SignalMap'
import ParticleField from './playground/ParticleField'
import './HomeHero.css'

export default function HomeHero() {
  const { t } = useTranslation()
  const reduced = useReducedMotion()
  return (
    <section className="signal-hero" aria-labelledby="hero-title">
      <ParticleField />
      <div className="signal-hero-copy">
        <Badge className="signal-hero-eyebrow">{t('studio.eyebrow')}</Badge>
        <h1 id="hero-title">{t('studio.title')}<br /><motion.span initial={reduced ? false : { y: 12 }} animate={{ y: 0 }} transition={{ duration: reduced ? 0 : .35 }}>{t('studio.titleAccent')}</motion.span></h1>
        <p className="signal-hero-description">{t('studio.description')}</p>
        <div className="signal-hero-actions">
          <Button href="#course-library">{t('catalog.explore')}<ArrowDown size={18} aria-hidden="true" /></Button>
          <Button to="/register" variant="ghost">{t('catalog.start')}<ArrowUpRight size={18} aria-hidden="true" /></Button>
        </div>
      </div>
      <SignalMap />
    </section>
  )
}
