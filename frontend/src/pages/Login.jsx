import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../api'

export default function Login() {
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
      setError('Неверный логин или пароль.')
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h1>Вход</h1>
      {error && <p className="error">{error}</p>}
      <input placeholder="Логин" value={username} onChange={(e) => setUsername(e.target.value)} required />
      <input placeholder="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      <button className="btn-primary" type="submit">Войти</button>
      <p>Нет аккаунта? <Link to="/register">Зарегистрироваться</Link></p>
    </form>
  )
}
