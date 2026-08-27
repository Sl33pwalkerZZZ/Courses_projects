import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

const api = axios.create({ baseURL: API_URL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api

export async function login(username, password) {
  const { data } = await api.post('/auth/token/', { username, password })
  localStorage.setItem('access', data.access)
  localStorage.setItem('refresh', data.refresh)
  return data
}

export async function register(username, email, password) {
  await api.post('/auth/register/', { username, email, password })
  return login(username, password)
}

export function logout() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem('access'))
}
