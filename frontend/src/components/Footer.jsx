import { ArrowUpRight, BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import useAuth from '../hooks/useAuth'
import LanguageSwitcher from './LanguageSwitcher'
import './Footer.css'

export default function Footer() {
  const { t } = useTranslation()
  const authed = useAuth()

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-main">
          <div className="footer-about">
            <Link to="/" className="footer-brand" aria-label={t('header.home')}>
              <span className="brand-mark"><BookOpen size={22} aria-hidden="true" /></span>
              <span>AI <span className="brand-serif">Courses</span></span>
            </Link>
            <p>{t('footer.description')}</p>
          </div>
          <nav className="footer-nav" aria-label={t('footer.navigation')}>
            <p className="eyebrow">{t('footer.explore')}</p>
            <Link to="/">{t('header.catalog')} <ArrowUpRight size={15} aria-hidden="true" /></Link>
            <Link to={authed ? '/profile' : '/login'}>
              {t(authed ? 'header.profile' : 'header.login')} <ArrowUpRight size={15} aria-hidden="true" />
            </Link>
          </nav>
          <div className="footer-preferences">
            <p className="eyebrow">{t('header.language')}</p>
            <LanguageSwitcher />
            <div className="footer-decoration" aria-hidden="true"><span /><span /><i /></div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>{t('footer.project')}</p>
          <p>{t('footer.copyright', { year: new Date().getFullYear() })}</p>
        </div>
      </div>
    </footer>
  )
}
