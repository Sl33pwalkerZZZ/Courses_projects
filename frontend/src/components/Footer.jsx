import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import useAuth from '../hooks/useAuth'
import './Footer.css'

export default function Footer() {
  const { t } = useTranslation()
  const authed = useAuth()

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-main">
          <nav className="footer-nav" aria-label={t('footer.navigation')}>
            <p className="eyebrow">{t('footer.explore')}</p>
            <div className="footer-links">
              <Link to="/">{t('header.catalog')} <ArrowUpRight size={15} aria-hidden="true" /></Link>
              <Link to={authed ? '/profile' : '/login'}>
                {t(authed ? 'header.profile' : 'header.login')} <ArrowUpRight size={15} aria-hidden="true" />
              </Link>
            </div>
          </nav>
          <div className="footer-decoration" aria-hidden="true"><span /><span /><i /></div>
        </div>
        <div className="footer-bottom">
          <p>{t('footer.project')}</p>
          <p>{t('footer.copyright', { year: new Date().getFullYear() })}</p>
        </div>
      </div>
    </footer>
  )
}
