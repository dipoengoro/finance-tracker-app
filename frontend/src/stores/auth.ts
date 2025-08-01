import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from "@/services/api";

// 'defineStore' adalah fungsi dari Pinia untuk membuat store baru.
// 'auth' adalah ID unik dari store ini.
export const useAuthStore = defineStore('auth', () => {
  // 1. STATE: Ini adalah data yang kita simpan.
  // Kita gunakan 'ref' agar datanya reaktif.
  const isAuthenticated = ref(false)
  const user = ref<any>(null)

  // 2. ACTIONS: Ini adalah fungsi untuk mengubah state.
  function setAuth(status: boolean) {
    isAuthenticated.value = status
  }

  async function checkAuthStatus(){
    try {
      const response = await apiClient.get('/')
    }
  }

  // 3. RETURN: Kita 'return' state dan actions agar bisa digunakan di komponen lain.
  return { isAuthenticated, setAuth }
})
