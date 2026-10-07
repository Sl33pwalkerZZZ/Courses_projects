import { ArrowLeft, BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Reveal from './Reveal'
import './AuthLayout.css'

export default function AuthLayout({ mode, children }) {
  const { t } = useTranslation()

  return (
    <section className="auth-page" aria-labelledby="auth-title">
      <Link className="auth-back" to="/"><ArrowLeft size={16} aria-hidden="true" />{t('auth.backToCatalog')}</Link>
      <div className="auth-grid">
        <Reveal className="auth-intro" immediate>
          <p className="eyebrow">{t('auth.eyebrow')}</p>
          <h2>{t(`auth.${mode}Welcome`)}</h2>
          <p className="auth-intro-description">{t(`auth.${mode}Description`)}</p>
          <div className="auth-illustration" aria-hidden="true">
            <span className="auth-orbit auth-orbit-one" /><span className="auth-orbit auth-orbit-two" />
            <span className="auth-orbit-dot" />
            <span className="auth-book"><BookOpen size={42} strokeWidth={1} /></span>
            <span className="auth-illustration-caption">{t('card.artLabel')}</span>
          </div>
          <p className="auth-note"><BookOpen size={16} aria-hidden="true" />{t('catalog.note')}</p>
        </Reveal>
        <Reveal className="auth-panel" delay={0.08} immediate>
          {children}
        </Reveal>
      </div>
    </section>
  )
}
