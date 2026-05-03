import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value)

  async function checkAuth() {
    try {
      const response = await api.get('/auth/user/')
      user.value = response.data
    } catch (error) {
      user.value = null
      token.value = null
    }
  }

  async function login(credentials) {
    loading.value = true
    try {
      const response = await api.post('/auth/login/', credentials)
      user.value = response.data.user
      token.value = null
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Přihlášení selhalo.',
      }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await api.post('/auth/logout/')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      user.value = null
      token.value = null
    }
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    checkAuth,
    login,
    logout,
  }
})
