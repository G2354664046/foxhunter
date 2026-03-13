<template>
  <header class="bg-gray-900 border-b border-gray-700">
    <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <router-link to="/" class="text-xl font-bold text-green-400">
            FoxHunter
          </router-link>
        </div>
        <div class="flex items-center space-x-4">
          <router-link to="/" class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
            首页
          </router-link>
          <router-link to="/upload" class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
            文件检测
          </router-link>
          <router-link
            to="/samples"
            class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
          >
            检测记录
          </router-link>
        </div>
        <div class="flex items-center space-x-2">
          <router-link
            v-if="!isAuthed"
            to="/login"
            class="bg-green-400 text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:bg-green-500"
          >
            登录/注册
          </router-link>
          <button
            v-else
            class="bg-gray-800 text-gray-100 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700 border border-gray-700"
            @click="logout"
          >
            退出
          </button>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const { isAuthed } = storeToRefs(auth)

const logout = () => {
  auth.setToken(null)
  router.replace({ name: 'Login' })
}
</script>

<style scoped>
/* Header styles */
</style>