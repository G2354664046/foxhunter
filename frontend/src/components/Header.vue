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
          <div v-else ref="dropdownRef" class="relative">
            <button
              type="button"
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-green-600 text-sm font-semibold text-gray-900 ring-2 ring-gray-700 hover:bg-green-500 focus:outline-none focus:ring-2 focus:ring-green-400"
              :title="displayName || '已登录用户'"
              aria-label="用户菜单"
              :aria-expanded="menuOpen"
              aria-haspopup="true"
              @click="menuOpen = !menuOpen"
            >
              {{ avatarInitial }}
            </button>
            <transition
              enter-active-class="transition ease-out duration-100"
              enter-from-class="transform opacity-0 scale-95"
              enter-to-class="transform opacity-100 scale-100"
              leave-active-class="transition ease-in duration-75"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95"
            >
              <div
                v-show="menuOpen"
                class="absolute right-0 z-50 mt-2 w-48 origin-top-right rounded-md border border-gray-700 bg-gray-800 py-1 shadow-lg ring-1 ring-black/5"
                role="menu"
                aria-orientation="vertical"
              >
                <router-link
                  to="/profile"
                  role="menuitem"
                  class="block px-4 py-2 text-sm text-gray-200 hover:bg-gray-700"
                  @click="menuOpen = false"
                >
                  我的信息
                </router-link>
                <router-link
                  to="/settings"
                  role="menuitem"
                  class="block px-4 py-2 text-sm text-gray-200 hover:bg-gray-700"
                  @click="menuOpen = false"
                >
                  个人设置
                </router-link>
                <button
                  type="button"
                  role="menuitem"
                  class="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-gray-700"
                  @click="handleLogout"
                >
                  退出登录
                </button>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/auth'
import { getUsernameFromToken } from '../lib/jwt'

const router = useRouter()
const auth = useAuthStore()
const { isAuthed, token } = storeToRefs(auth)

const menuOpen = ref(false)
const dropdownRef = ref(null)

function onDocClick(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    menuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', onDocClick)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocClick)
})

const displayName = computed(() => getUsernameFromToken(token.value))
const avatarInitial = computed(() => {
  const name = displayName.value
  if (!name) return '?'
  return name.slice(0, 1).toUpperCase()
})

const handleLogout = () => {
  menuOpen.value = false
  auth.setToken(null)
  router.replace({ name: 'Login' })
}
</script>

<style scoped>
/* Header styles */
</style>
