import api from './api'

export const authService = {
  async login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('forgeguard_token', data.access_token)
    localStorage.setItem('forgeguard_user', JSON.stringify(data.user))
    return data.user
  },

  async register(fullName, email, password, role = 'OPERATOR') {
    const { data } = await api.post('/auth/register', {
      full_name: fullName,
      email,
      password,
      role,
    })
    localStorage.setItem('forgeguard_token', data.access_token)
    localStorage.setItem('forgeguard_user', JSON.stringify(data.user))
    return data.user
  },

  logout() {
    localStorage.removeItem('forgeguard_token')
    localStorage.removeItem('forgeguard_user')
  },

  getCurrentUser() {
    const raw = localStorage.getItem('forgeguard_user')
    return raw ? JSON.parse(raw) : null
  },

  getToken() {
    return localStorage.getItem('forgeguard_token')
  },

  isAuthenticated() {
    return !!localStorage.getItem('forgeguard_token')
  },
}
