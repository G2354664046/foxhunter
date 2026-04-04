<template>
  <div class="min-h-screen bg-gray-900 text-white py-12">
    <div class="max-w-xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-gray-800 rounded-lg p-8">
        <h2 class="text-2xl font-bold text-green-400 mb-2">个人信息</h2>
        <p class="text-sm text-gray-500 mb-6">修改用户名、邮箱或密码前，请先填写当前密码以验证身份。</p>

        <p v-if="loading" class="text-gray-400">加载中…</p>
        <div v-else-if="loadError" class="text-sm text-red-400">{{ loadError }}</div>
        <template v-else>
          <div v-if="successMsg" class="mb-4 text-sm text-green-400">{{ successMsg }}</div>
          <div v-if="submitError" class="mb-4 text-sm text-red-400">{{ submitError }}</div>

          <form class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="block text-sm text-gray-400 mb-1">用户名</label>
            <input
              v-model="form.username"
              type="text"
              required
              autocomplete="username"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-green-500 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">邮箱</label>
            <input
              v-model="form.email"
              type="email"
              required
              autocomplete="email"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-green-500 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">当前密码</label>
            <input
              v-model="form.currentPassword"
              type="password"
              required
              autocomplete="current-password"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-green-500 focus:outline-none"
              placeholder="必填，用于验证身份"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">新密码</label>
            <input
              v-model="form.newPassword"
              type="password"
              autocomplete="new-password"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-green-500 focus:outline-none"
              placeholder="留空表示不修改"
            />
          </div>
          <div v-if="form.newPassword">
            <label class="block text-sm text-gray-400 mb-1">确认新密码</label>
            <input
              v-model="form.confirmPassword"
              type="password"
              autocomplete="new-password"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-green-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            class="w-full bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="submitting"
          >
            {{ submitting ? '保存中…' : '保存修改' }}
          </button>
        </form>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { api } from '../lib/api'

const auth = useAuthStore()

const form = reactive({
  username: '',
  email: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const loading = ref(true)
const loadError = ref('')
const submitError = ref('')
const successMsg = ref('')
const submitting = ref(false)

function detailMessage(e) {
  const d = e.response?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) {
    return d.map((x) => x.msg || JSON.stringify(x)).join('；')
  }
  return '请求失败'
}

async function loadProfile() {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await api.get('/api/v1/auth/me')
    form.username = data.username
    form.email = data.email
  } catch (e) {
    loadError.value = detailMessage(e) || '无法加载个人信息'
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)

async function submit() {
  submitError.value = ''
  successMsg.value = ''
  if (form.newPassword && form.newPassword !== form.confirmPassword) {
    submitError.value = '两次输入的新密码不一致'
    return
  }
  if (form.newPassword && form.newPassword.length < 6) {
    submitError.value = '新密码至少 6 位'
    return
  }
  submitting.value = true
  try {
    const body = {
      username: form.username.trim(),
      email: form.email.trim(),
      current_password: form.currentPassword,
      new_password: form.newPassword.trim() || null
    }
    const { data } = await api.patch('/api/v1/auth/me', body)
    if (data.access_token) {
      auth.setToken(data.access_token)
    }
    form.currentPassword = ''
    form.newPassword = ''
    form.confirmPassword = ''
    successMsg.value = '保存成功'
    form.username = data.username
    form.email = data.email
  } catch (e) {
    submitError.value = detailMessage(e)
  } finally {
    submitting.value = false
  }
}
</script>
