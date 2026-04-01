import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin' || state.user?.role === 'super_admin',
    isSuperAdmin: (state) => state.user?.role === 'super_admin',
    userColor: (state) => {
      const u = state.user?.username || ''
      const colors = ['#6366f1','#8b5cf6','#ec4899','#10b981','#f59e0b','#3b82f6','#ef4444','#14b8a6']
      let h = 0
      for (let i = 0; i < u.length; i++) h = u.charCodeAt(i) + ((h << 5) - h)
      return colors[Math.abs(h) % colors.length]
    }
  },
  actions: {
    async login(username, password) {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      this.token = response.data.access_token
      localStorage.setItem('token', this.token)
      await this.fetchUser()
    },
    async register(username, password) {
      await api.post('/auth/register', { username, password })
      await this.login(username, password)
    },
    async fetchUser() {
      if (!this.token) return
      try {
        const response = await api.get('/user/me')
        this.user = response.data
      } catch (e) {
        this.logout()
      }
    },
    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
    }
  }
})
