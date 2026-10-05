import { ArrowUpRight, BookOpen, LogOut } from 'lucide-react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { isAuthenticated, logout } from '../api'
import ThemeToggle from './ThemeToggle'
import LanguageSwitcher from './LanguageSwitcher'
import './Header.css'

export default function Header() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const authed = isAuthenticated()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <>
      <a className="skip-link" href="#main-content">{t('header.skip')}</a>
      <header className="site-header">
        <div className="header-inner">
          <Link to="/" className="brand" aria-label={t('header.home')}>
            <span className="brand-mark"><BookOpen size={22} aria-hidden="true" /></span>
            <span>AI <span className="brand-serif">Courses</span><small>{t('header.tagline')}</small></span>
          </Link>
          <nav className="header-nav" aria-label={t('header.navigation')}>
            <NavLink to="/" end className="catalog-nav-link">{t('header.catalog')}</NavLink>
            <span className="nav-divider" aria-hidden="true" />
            {authed ? (
              <button className="header-login" onClick={handleLogout}>
                {t('header.logout')} <LogOut size={16} aria-hidden="true" />
              </button>
            ) : (
              <>
                <Link to="/login" className="header-login">{t('header.login')}</Link>
                <Link to="/register" className="header-register">
                  {t('header.register')} <ArrowUpRight size={16} aria-hidden="true" />
                </Link>
              </>
            )}
          </nav>
          <div className="header-preferences">
            <LanguageSwitcher />
            <ThemeToggle />
          </div>
        </div>
      </header>
    </>
  )
}
