import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../api'
import { ArrowUpRight } from 'lucide-react'
import AuthLayout from '../components/AuthLayout'
import AuthField from '../components/AuthField'

export default function Login() {
  const { t } = useTranslation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    if (submitting) return
    setError(null)
    setSubmitting(true)
    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err.response?.status === 401 ? 'auth.loginError' : 'auth.connectionError')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout mode="login">
      <h1 id="auth-title">{t('auth.loginTitle')}</h1>
      <p className="auth-form-description">{t('auth.loginFormDescription')}</p>
      <form className="auth-form" onSubmit={handleSubmit} aria-labelledby="auth-title" aria-busy={submitting}>
        {error && <p className="auth-error" role="alert">{t(error)}</p>}
        <AuthField name="username" label={t('auth.username')} autoComplete="username" maxLength={150}
          value={username} onChange={(e) => setUsername(e.target.value)} disabled={submitting} required />
        <AuthField name="password" label={t('auth.password')} type="password" autoComplete="current-password"
          value={password} onChange={(e) => setPassword(e.target.value)} disabled={submitting} required />
        <button className="academic-button auth-submit" type="submit" disabled={submitting}>
          {t(submitting ? 'auth.signingIn' : 'auth.login')} <ArrowUpRight size={17} aria-hidden="true" />
        </button>
      </form>
      <p className="auth-switch">{t('auth.noAccount')} <Link to="/register">{t('auth.register')}</Link></p>
    </AuthLayout>
  )
}
