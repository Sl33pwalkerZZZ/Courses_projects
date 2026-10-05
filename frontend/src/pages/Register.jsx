import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { register } from '../api'

export default function Register() {
  const { t } = useTranslation()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    try {
      await register(username, email, password)
      navigate('/')
    } catch (err) {
      const data = err.response?.data
      setError(data ? { message: Object.values(data).flat().join(' ') } : { key: 'auth.registerError' })
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h1>{t('auth.registerTitle')}</h1>
      {error && <p className="error">{error.key ? t(error.key) : error.message}</p>}
      <input placeholder={t('auth.username')} aria-label={t('auth.username')} value={username} onChange={(e) => setUsername(e.target.value)} required />
      <input placeholder={t('auth.email')} aria-label={t('auth.email')} type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input placeholder={t('auth.password')} aria-label={t('auth.password')} type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      <button className="btn-primary" type="submit">{t('auth.register')}</button>
    </form>
  )
}
