import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { register } from '../api'

export default function Register() {
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
      setError(data ? Object.values(data).flat().join(' ') : 'Не удалось зарегистрироваться.')
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h1>Регистрация</h1>
      {error && <p className="error">{error}</p>}
      <input placeholder="Логин" value={username} onChange={(e) => setUsername(e.target.value)} required />
      <input placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input placeholder="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      <button className="btn-primary" type="submit">Зарегистрироваться</button>
    </form>
  )
}
