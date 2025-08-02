import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from "@/services/api";

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref<any>(null)

  function setAuth(status: boolean) {
    isAuthenticated.value = status
  }

  async function checkAuthStatus(){
    try {
      const response = await apiClient.get('/api/whoami/')
      isAuthenticated.value = true
      user.value = response.data
    } catch {
      isAuthenticated.value = false
      user.value = null
    }
  }

  return { isAuthenticated, user, setAuth, checkAuthStatus }
})
