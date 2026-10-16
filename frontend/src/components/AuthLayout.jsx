import { ArrowLeft, Sparkles } from 'lucide-react'
import { motion } from 'motion/react'
import { useReducedMotion } from '../hooks/useMotionPreferences'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import AICompanion from './motion/AICompanion'
import ParticleField from './playground/ParticleField'
import Badge from './ui/Badge'
import './AuthLayout.css'

export default function AuthLayout({ mode, children }) {
  const { t } = useTranslation()
  const reducedMotion = useReducedMotion()

  return (
    <section className="auth-page v2-scope" aria-labelledby="auth-title">
      <Link className="auth-back" to="/"><ArrowLeft size={18} aria-hidden="true" />{t('auth.backToCatalog')}</Link>
      <div className="auth-grid">
        <aside className="auth-intro" aria-labelledby="auth-welcome">
          <ParticleField />
          <Badge className="auth-eyebrow">{t('studio.eyebrow')}</Badge>
          <h2 id="auth-welcome">{t(`auth.${mode}Welcome`)}</h2>
          <p className="auth-intro-description">{t(`auth.${mode}Description`)}</p>
          <div className="auth-illustration" aria-hidden="true"><AICompanion /></div>
          <p className="auth-note"><Sparkles size={18} aria-hidden="true" />{t('catalog.note')}</p>
        </aside>
        <motion.div key={mode} className="auth-panel"
          initial={reducedMotion ? false : { y: 12 }} animate={{ y: 0 }}
          transition={{ duration: reducedMotion ? 0 : 0.24, ease: [0.2, 0.8, 0.2, 1] }}>
          {children}
        </motion.div>
      </div>
    </section>
  )
}
