import { useEffect, useRef, useState } from 'react'
import { ArrowUpRight, LogOut, Menu, X } from 'lucide-react'
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { logout } from '../api'
import useAuth from '../hooks/useAuth'
import ThemeToggle from './ThemeToggle'
import LanguageSwitcher from './LanguageSwitcher'
import Button from './ui/Button'
import Dialog from './ui/Dialog'
import './Header.css'

export default function Header() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { pathname, hash } = useLocation()
  const authed = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const headerRef = useRef(null)

  // Router hash links need a scroll after the destination has mounted.
  useEffect(() => {
    if (pathname !== '/' || hash !== '#course-library') return
    document.getElementById('course-library')?.scrollIntoView()
  }, [pathname, hash])

  // Hash links stay clear even when translations or text zoom grow the header.
  useEffect(() => {
    const observer = new ResizeObserver(([entry]) => {
      document.documentElement.style.setProperty('--v2-header-height', `${entry.borderBoxSize[0].blockSize}px`)
    })
    observer.observe(headerRef.current)
    const desktop = window.matchMedia('(min-width: 1024px)')
    const closeOnDesktop = () => { if (desktop.matches) setMenuOpen(false) }
    desktop.addEventListener('change', closeOnDesktop)
    return () => {
      observer.disconnect()
      desktop.removeEventListener('change', closeOnDesktop)
      document.documentElement.style.removeProperty('--v2-header-height')
    }
  }, [])

  function handleLogout() {
    setMenuOpen(false)
    logout()
    navigate('/login')
  }

  function navigation() {
    return <>
      <Link to="/#course-library" className="catalog-nav-link" onClick={() => {
        setMenuOpen(false)
        // Also works when this exact hash is already selected.
        document.getElementById('course-library')?.scrollIntoView()
      }}>{t('header.catalog')}</Link>
      {authed ? <>
        <NavLink to="/profile" className="catalog-nav-link" onClick={() => setMenuOpen(false)}>{t('header.profile')}</NavLink>
        <Button variant="ghost" onClick={handleLogout}>{t('header.logout')}<LogOut size={16} aria-hidden="true" /></Button>
      </> : <>
        <Link to="/login" className="header-login" onClick={() => setMenuOpen(false)}>{t('header.login')}</Link>
        <Button to="/register" onClick={() => setMenuOpen(false)}>{t('header.register')}<ArrowUpRight size={16} aria-hidden="true" /></Button>
      </>}
    </>
  }

  return (
    <>
      <a className="skip-link v2-skip-link" href="#main-content">{t('header.skip')}</a>
      <header ref={headerRef} className="site-header v2-scope">
        <div className="header-inner">
          <Link to="/" className="brand" aria-label={t('header.home')}>AI <span aria-hidden="true">/</span> COURSES</Link>
          <nav className="header-nav" aria-label={t('header.navigation')}>{navigation()}</nav>
          <div className="header-preferences">
            <div className="header-desktop-language"><LanguageSwitcher /></div>
            <div className="header-quick-theme"><ThemeToggle /></div>
          </div>
          <Button variant="secondary" className="header-menu-toggle v2-icon-button"
            aria-label={t('header.menu')} aria-haspopup="dialog" aria-expanded={menuOpen}
            onClick={() => setMenuOpen(true)}><Menu size={20} aria-hidden="true" /></Button>
        </div>
      </header>
      {menuOpen && <Dialog labelledBy="mobile-menu-title" className="header-menu v2-scope" onClose={() => setMenuOpen(false)}>
        <div className="header-menu-heading">
          <h2 id="mobile-menu-title">{t('header.navigation')}</h2>
          <Button variant="ghost" className="v2-icon-button" aria-label={t('header.closeMenu')} onClick={() => setMenuOpen(false)}><X size={20} aria-hidden="true" /></Button>
        </div>
        <nav aria-label={t('header.navigation')} className="header-menu-nav">{navigation()}</nav>
        <div className="header-menu-preferences">
          <span>{t('header.language')}</span><LanguageSwitcher />
          <span>{t('studio.appearance')}</span><ThemeToggle />
        </div>
      </Dialog>}
    </>
  )
}
