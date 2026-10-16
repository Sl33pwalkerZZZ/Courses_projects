import { ArrowDown, ArrowUpRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import Button from './ui/Button'
import Badge from './ui/Badge'
import AICompanion from './motion/AICompanion'
import AnimatedText from './motion/AnimatedText'
import EntrySignal from './motion/EntrySignal'
import ParticleField from './playground/ParticleField'
import './HomeHero.css'

export default function HomeHero() {
  const { t } = useTranslation()
  return (
    <section className="signal-hero" aria-labelledby="hero-title">
      <ParticleField />
      <EntrySignal />
      <div className="signal-hero-copy">
        <Badge className="signal-hero-eyebrow">{t('studio.eyebrow')}</Badge>
        <h1 id="hero-title"><AnimatedText text={t('studio.title')} /><br /><AnimatedText className="signal-hero-title-accent" text={t('studio.titleAccent')} /></h1>
        <p className="signal-hero-description">{t('studio.description')}</p>
        <div className="signal-hero-actions">
          <Button href="#course-library">{t('catalog.explore')}<ArrowDown size={18} aria-hidden="true" /></Button>
          <Button to="/register" variant="ghost">{t('catalog.start')}<ArrowUpRight size={18} aria-hidden="true" /></Button>
        </div>
      </div>
      <AICompanion />
    </section>
  )
}
