import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null
  }),

  getters: {
    isAuthed: (state) => !!state.token
  },

  actions: {
    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('access_token', token)
      } else {
        localStorage.removeItem('access_token')
      }
    }
  }
})

