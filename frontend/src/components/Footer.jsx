import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useEffect } from 'react'
import useAuth from '../hooks/useAuth'
import './Footer.css'

export function StudioFooter({ authed, home = true }) {
  const { t } = useTranslation()
  useEffect(() => {
    // Auth pages can link here before asynchronous course cards have loaded.
    // Land on the workflow after that existing layout has reached its final height.
    if (!home || window.location.hash !== '#learning-workflow') return
    const catalog = document.getElementById('course-library')
    const target = document.getElementById('learning-workflow')
    if (!catalog || !target) return
    let observer
    function land() {
      if (window.location.hash !== '#learning-workflow') {
        observer?.disconnect()
      } else if (catalog.getAttribute('aria-busy') !== 'true') {
        target.scrollIntoView()
        observer?.disconnect()
      }
    }
    observer = new MutationObserver(land)
    observer.observe(catalog, { attributes: true, attributeFilter: ['aria-busy'] })
    land()
    return () => observer.disconnect()
  }, [home])
  return (
    <footer className="site-footer studio-footer v2-scope">
      <div className="studio-footer-inner">
        <div className="studio-footer-top">
          <div className="studio-footer-about">
            <Link to="/" className="brand" aria-label={t('header.home')}>AI <span aria-hidden="true">/</span> COURSES</Link>
            <p>{t('footer.description')}</p>
          </div>
          <nav aria-label={t('footer.navigation')}>
            <p className="studio-eyebrow">{t('studio.footerLabel')}</p>
            <a href={`${home ? '' : '/'}#course-library`}>{t('header.catalog')}<ArrowUpRight size={16} aria-hidden="true" /></a>
            <a href={`${home ? '' : '/'}#learning-workflow`}>{t('studio.workflowTitle')}<ArrowUpRight size={16} aria-hidden="true" /></a>
            <Link to={authed ? '/profile' : '/login'}>{t(authed ? 'header.profile' : 'header.login')}<ArrowUpRight size={16} aria-hidden="true" /></Link>
          </nav>
        </div>
        <div className="studio-footer-bottom">
          <p>{t('footer.project')}</p>
          <p>{t('footer.copyright', { year: new Date().getFullYear() })}</p>
        </div>
      </div>
    </footer>
  )
}

export default function Footer({ studio = false, home = true }) {
  const { t } = useTranslation()
  const authed = useAuth()

  if (studio) return <StudioFooter authed={authed} home={home} />

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
