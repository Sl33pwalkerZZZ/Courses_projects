import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../api'

export default function Login() {
  const { t } = useTranslation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    try {
      await login(username, password)
      navigate('/')
    } catch {
      setError('auth.loginError')
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h1>{t('auth.loginTitle')}</h1>
      {error && <p className="error">{t(error)}</p>}
      <input placeholder={t('auth.username')} aria-label={t('auth.username')} value={username} onChange={(e) => setUsername(e.target.value)} required />
      <input placeholder={t('auth.password')} aria-label={t('auth.password')} type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      <button className="btn-primary" type="submit">{t('auth.login')}</button>
      <p>{t('auth.noAccount')} <Link to="/register">{t('auth.register')}</Link></p>
    </form>
  )
}
