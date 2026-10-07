import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../api'
import { ArrowUpRight } from 'lucide-react'
import AuthLayout from '../components/AuthLayout'
import AuthField from '../components/AuthField'

export default function Register() {
  const { t } = useTranslation()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
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
      await register(username, email, password)
      navigate('/')
    } catch (err) {
      const data = err.response?.data
      setError(data ? { message: Object.values(data).flat().join(' ') } : { key: 'auth.registerError' })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout mode="register">
      <h1 id="auth-title">{t('auth.registerTitle')}</h1>
      <p className="auth-form-description">{t('auth.registerFormDescription')}</p>
      <form className="auth-form" onSubmit={handleSubmit} aria-labelledby="auth-title" aria-busy={submitting}>
        {error && <p className="auth-error" role="alert">{error.key ? t(error.key) : error.message}</p>}
        <AuthField name="username" label={t('auth.username')} autoComplete="username" maxLength={150}
          value={username} onChange={(e) => setUsername(e.target.value)} disabled={submitting} required />
        <AuthField name="email" label={t('auth.email')} hint={t('auth.emailHint')} type="email" autoComplete="email" maxLength={254}
          value={email} onChange={(e) => setEmail(e.target.value)} disabled={submitting} />
        <AuthField name="password" label={t('auth.password')} hint={t('auth.passwordHint')} type="password" autoComplete="new-password" minLength={8}
          value={password} onChange={(e) => setPassword(e.target.value)} disabled={submitting} required />
        <button className="academic-button auth-submit" type="submit" disabled={submitting}>
          {t(submitting ? 'auth.creatingAccount' : 'auth.register')} <ArrowUpRight size={17} aria-hidden="true" />
        </button>
      </form>
      <p className="auth-switch">{t('auth.hasAccount')} <Link to="/login">{t('auth.login')}</Link></p>
    </AuthLayout>
  )
}
