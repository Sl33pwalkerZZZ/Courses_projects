import { Link, useNavigate } from 'react-router-dom'
import { isAuthenticated, logout } from '../api'

export default function Header() {
  const navigate = useNavigate()
  const authed = isAuthenticated()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="header">
      <Link to="/" className="logo">AI Courses</Link>
      <nav className="nav">
        {authed ? (
          <button className="btn-link" onClick={handleLogout}>Выйти</button>
        ) : (
          <>
            <Link to="/login">Войти</Link>
            <Link to="/register" className="btn-primary">Регистрация</Link>
          </>
        )}
      </nav>
    </header>
  )
}
