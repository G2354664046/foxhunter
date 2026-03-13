<template>
  <div class="min-h-screen bg-gray-900 text-white relative overflow-hidden">
    <!-- 星空背景 -->
    <div class="starfield fixed inset-0 pointer-events-none z-0" ref="starfield"></div>

    <!-- 星云效果 -->
    <div class="nebula nebula-1 fixed rounded-full blur-3xl pointer-events-none z-0"></div>
    <div class="nebula nebula-2 fixed rounded-full blur-3xl pointer-events-none z-0"></div>
    <div class="nebula nebula-3 fixed rounded-full blur-3xl pointer-events-none z-0"></div>

    <!-- 萤火虫容器 -->
    <div class="fixed inset-0 pointer-events-none z-1" ref="fireflies"></div>

    <!-- 主内容 -->
    <div class="relative z-10 flex items-center justify-center min-h-screen">
      <div class="w-full max-w-md p-8 bg-gray-800 rounded-lg">
        <h2 class="text-2xl font-bold mb-6">{{ mode === 'login' ? '登录' : '注册' }}</h2>
        <form @submit.prevent="submit">
          <div class="mb-4">
            <label class="block text-sm mb-1">用户名</label>
            <input v-model="username" type="text" class="w-full px-3 py-2 bg-gray-700 rounded" required />
          </div>
          <div v-if="mode === 'register'" class="mb-4">
            <label class="block text-sm mb-1">邮箱</label>
            <input v-model="email" type="email" class="w-full px-3 py-2 bg-gray-700 rounded" required />
          </div>
          <div class="mb-6">
            <label class="block text-sm mb-1">密码</label>
            <input v-model="password" type="password" class="w-full px-3 py-2 bg-gray-700 rounded" required />
          </div>
          <button type="submit" class="w-full bg-green-400 text-gray-900 py-2 rounded">
            {{ mode === 'login' ? '登录' : '注册' }}
          </button>
        </form>
        <p class="mt-4 text-center">
          <a href="#" @click.prevent="toggleMode" class="text-blue-400">
            {{ mode === 'login' ? '没有账户？注册' : '已有账户？登录' }}
          </a>
        </p>
        <p v-if="mode === 'login'" class="mt-2 text-center">
          <router-link to="/forgot-password" class="text-blue-400">忘记密码？</router-link>
        </p>
        <p v-if="errorMsg" class="mt-4 text-red-400 text-center">{{ errorMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '../lib/api'
import { useAuthStore } from '../stores/auth'

const username = ref('')
const email = ref('')
const password = ref('')
const mode = ref('login')
const errorMsg = ref('')
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

// 星空和萤火虫相关
const starfield = ref(null)
const fireflies = ref(null)
const firefliesData = ref([])

// initialize mode from query param
onMounted(() => {
  if (route.query.mode === 'register') {
    mode.value = 'register'
  }
  // 创建星空和萤火虫效果
  createStarfield()
  createFireflies()
  animateFireflies()
})

const toggleMode = () => {
  errorMsg.value = ''
  mode.value = mode.value === 'login' ? 'register' : 'login'
}

const submit = () => {
  errorMsg.value = ''
  if (mode.value === 'login') {
    login()
  } else {
    register()
  }
}

const login = async () => {
  try {
    const form = new URLSearchParams()
    form.append('username', username.value)
    form.append('password', password.value)
    const resp = await api.post('/api/v1/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    auth.setToken(resp.data.access_token)
    const redirect = route.query.redirect || '/'
    router.replace(redirect)
  } catch (e) {
    errorMsg.value = '登录失败，请检查用户名/密码'
  }
}

const register = async () => {
  try {
    await api.post('/api/v1/auth/register', {
      username: username.value,
      email: email.value,
      password: password.value
    })
    // 注册成功后自动登录
    mode.value = 'login'
    await login()
  } catch (e) {
    errorMsg.value = '注册失败：用户名或邮箱已存在'
  }
}

// 星空和萤火虫动画函数
const createStarfield = () => {
  if (!starfield.value) return

  const starCount = 150
  for (let i = 0; i < starCount; i++) {
    const star = document.createElement('div')
    star.className = 'star'

    const size = Math.random() * 2 + 1
    const x = Math.random() * 100
    const y = Math.random() * 100
    const duration = Math.random() * 3 + 2
    const minOpacity = Math.random() * 0.3 + 0.2

    star.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${x}%;
      top: ${y}%;
      --duration: ${duration}s;
      --min-opacity: ${minOpacity};
      animation-delay: ${Math.random() * duration}s;
    `

    starfield.value.appendChild(star)
  }
}

const createFireflies = () => {
  if (!fireflies.value) return

  const count = 25
  for (let i = 0; i < count; i++) {
    const firefly = document.createElement('div')
    firefly.className = 'firefly'

    const fireflyData = {
      el: firefly,
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: 0,
      vy: 0,
      phase: Math.random() * Math.PI * 2
    }

    firefliesData.value.push(fireflyData)
    fireflies.value.appendChild(firefly)
  }
}

const animateFireflies = () => {
  firefliesData.value.forEach(f => {
    f.phase += 0.02
    f.vx += Math.sin(f.phase) * 0.01
    f.vy += Math.cos(f.phase * 0.7) * 0.01

    f.vx *= 0.99
    f.vy *= 0.99

    f.x += f.vx
    f.y += f.vy

    // 边界检测
    if (f.x < 0) f.x = window.innerWidth
    if (f.x > window.innerWidth) f.x = 0
    if (f.y < 0) f.y = window.innerHeight
    if (f.y > window.innerHeight) f.y = 0

    f.el.style.transform = `translate(${f.x}px, ${f.y}px)`
  })

  requestAnimationFrame(animateFireflies)
}
</script>

<style>
/* 星空背景 */
.starfield {
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  background: #ffffff;
  border-radius: 50%;
  animation: twinkle var(--duration) ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: var(--min-opacity); transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* 星云效果 */
.nebula {
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}

.nebula-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 100, 150, 0.15) 0%, transparent 70%);
  top: -200px;
  right: -100px;
}

.nebula-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(100, 0, 120, 0.1) 0%, transparent 70%);
  bottom: 10%;
  left: -100px;
}

.nebula-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(0, 212, 170, 0.08) 0%, transparent 70%);
  top: 40%;
  right: 20%;
}

/* 萤火虫粒子 */
.firefly {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #00d4aa;
  border-radius: 50%;
  box-shadow:
    0 0 6px 2px #00d4aa,
    0 0 12px 4px rgba(0, 212, 170, 0.3),
    0 0 20px 6px rgba(0, 212, 170, 0.1);
  pointer-events: none;
  z-index: 1;
  animation: firefly-glow 3s ease-in-out infinite;
}

@keyframes firefly-glow {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}
</style>
