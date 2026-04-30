import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../services/api'

export const useAdminStore = defineStore('admin', () => {
  const admin = ref(null)

  const isLoggedIn = computed(() => !!admin.value)
  const username = computed(() => admin.value?.username || '')
  const role = computed(() => admin.value?.role || '')

  function setAdmin(data) {
    admin.value = data
  }

  function clearAdmin() {
    admin.value = null
  }

  async function login(username, password) {
    const response = await authApi.login({ username, password })
    if (response.data.success) {
      setAdmin(response.data.admin)
      return response.data
    }
    throw new Error(response.data.message || '登录失败')
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearAdmin()
    }
  }

  async function fetchAdmin() {
    try {
      const response = await authApi.me()
      if (response.data.success) {
        setAdmin(response.data.admin)
        return response.data.admin
      }
    } catch (error) {
      console.error('Fetch admin error:', error)
    }
    clearAdmin()
    return null
  }

  return {
    admin,
    isLoggedIn,
    username,
    role,
    setAdmin,
    clearAdmin,
    login,
    logout,
    fetchAdmin
  }
})
