import { ref, readonly } from 'vue'
import { authApi } from '../services/api'

const user = ref(null)
const isLoading = ref(false)

export function useUserStore() {
  const fetchUser = async () => {
    isLoading.value = true
    try {
      const response = await authApi.me()
      if (response.data.success) {
        user.value = response.data.user
      } else {
        user.value = null
      }
    } catch {
      user.value = null
    } finally {
      isLoading.value = false
    }
  }

  const setUser = (newUser) => {
    user.value = newUser
  }

  const clearUser = () => {
    user.value = null
  }

  return {
    user: readonly(user),
    isLoading: readonly(isLoading),
    fetchUser,
    setUser,
    clearUser
  }
}
