import { ArrowUpRight, BookOpen, LogOut } from 'lucide-react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { isAuthenticated, logout } from '../api'
import './Header.css'

export default function Header() {
  const navigate = useNavigate()
  const authed = isAuthenticated()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <>
      <a className="skip-link" href="#main-content">Перейти к содержанию</a>
      <header className="site-header">
        <div className="header-inner">
          <Link to="/" className="brand" aria-label="AI Courses — главная">
            <span className="brand-mark"><BookOpen size={22} aria-hidden="true" /></span>
            <span>AI <span className="brand-serif">Courses</span><small>БИБЛИОТЕКА НОВЫХ ЗНАНИЙ</small></span>
          </Link>
          <nav className="header-nav" aria-label="Основная навигация">
            <NavLink to="/" end className="catalog-nav-link">Каталог курсов</NavLink>
            <span className="nav-divider" aria-hidden="true" />
            {authed ? (
              <button className="header-login" onClick={handleLogout}>
                Выйти <LogOut size={16} aria-hidden="true" />
              </button>
            ) : (
              <>
                <Link to="/login" className="header-login">Войти</Link>
                <Link to="/register" className="header-register">
                  Регистрация <ArrowUpRight size={16} aria-hidden="true" />
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
    </>
  )
}
