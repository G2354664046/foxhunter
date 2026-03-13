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
    <div class="relative z-10">
      <!-- Hero 区域 -->
      <section class="px-6 pt-16 pb-12">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="hero-title text-4xl md:text-5xl font-bold mb-6 leading-tight reveal">
            恶意文件检测平台
          </h1>
          <p class="text-lg mb-10 reveal text-gray-400" style="animation-delay: 0.1s;">
            整合数十款主流杀毒引擎，提供全面的恶意软件检测与分析服务
          </p>

          <!-- Tab 切换 -->
          <div class="flex justify-center mb-6 reveal" style="animation-delay: 0.2s;">
            <button
              @click="activeTab = 'file'"
              :class="['tab-btn', { active: activeTab === 'file' }]"
              data-tab="file"
            >
              文件检测
            </button>
            <button
              @click="activeTab = 'url'"
              :class="['tab-btn', { active: activeTab === 'url' }]"
              data-tab="url"
            >
              URL检测
            </button>
            <button
              @click="activeTab = 'hash'"
              :class="['tab-btn', { active: activeTab === 'hash' }]"
              data-tab="hash"
            >
              哈希查询
            </button>
          </div>

          <!-- 文件上传区 -->
          <div v-if="activeTab === 'file'" class="tab-content reveal" data-tab="file" style="animation-delay: 0.3s;">
            <div class="upload-zone p-12 cursor-pointer" @click="triggerFileUpload" @dragover.prevent @drop="handleFileDrop">
              <input
                ref="fileInput"
                type="file"
                class="hidden"
                @change="handleFileSelect"
                accept=".exe,.dll,.bin"
              />
              <div v-if="!selectedFile">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-4 upload-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="text-gray-300">点击选择文件或拖拽文件到此处</p>
                <p class="text-sm text-gray-500 mt-2">支持 .exe, .dll, .bin 文件</p>
              </div>
              <div v-else class="text-center">
                <p class="text-green-400 font-semibold">{{ selectedFile.name }}</p>
                <p class="text-sm text-gray-400">{{ formatFileSize(selectedFile.size) }}</p>
                <button
                  class="scan-btn inline-block mt-6"
                  @click.stop="uploadFile"
                  :disabled="uploading"
                >
                  {{ uploading ? '检测中...' : '开始检测' }}
                </button>
              </div>
            </div>

            <!-- 检测过程与结果 -->
            <div v-if="uploadResult || uploadError" class="mt-6 text-left bg-gray-800 rounded-lg p-4 text-sm">
              <div v-if="uploadError" class="text-red-400 mb-2">
                {{ uploadError }}
              </div>
              <div v-if="uploadResult">
                <div class="mb-1">
                  <span class="font-semibold text-green-400">文件：</span>
                  <span class="text-gray-200 break-all">{{ uploadResult.filename }}</span>
                </div>
                <div class="mb-1">
                  <span class="font-semibold text-green-400">状态：</span>
                  <span class="text-gray-200">
                    {{ uploadResult.status }}
                  </span>
                </div>
                <div v-if="uploadResult.id" class="mt-2">
                  <router-link
                    :to="`/results/${uploadResult.id}`"
                    class="text-green-400 hover:text-green-300 text-sm"
                  >
                    查看详细结果 →
                  </router-link>
                </div>
              </div>
            </div>
          </div>

      <!-- URL 检测 -->
      <div v-if="activeTab === 'url'" class="tab-content reveal" data-tab="url">
        <div class="max-w-2xl mx-auto">
          <input
            v-model="urlInput"
            type="url"
            placeholder="请输入要检测的URL..."
            class="url-input w-full"
          />
          <button class="scan-btn mt-4" @click="scanUrl" :disabled="urlLoading">
            {{ urlLoading ? '检测中...' : '检测URL' }}
          </button>

          <div v-if="urlError" class="mt-4 text-sm text-red-400">
            {{ urlError }}
          </div>

          <div v-if="urlResult" class="mt-4 text-left bg-gray-800 rounded-lg p-4 text-sm">
            <div class="mb-2">
              <span class="font-semibold text-green-400">检测URL：</span>
              <span class="text-gray-200 break-all">{{ urlResult.url }}</span>
            </div>
            <div class="mb-2">
              <span class="font-semibold text-green-400">提供方：</span>
              <span class="text-gray-200">{{ urlResult.provider }}</span>
            </div>
            <div class="mt-2 text-gray-300">
              <div class="font-semibold mb-1">原始结果（JSON）：</div>
              <pre class="bg-gray-900 rounded-md p-3 overflow-x-auto text-xs text-gray-200">
{{ formattedUrlJson }}
              </pre>
            </div>
          </div>
        </div>
      </div>

          <!-- 哈希查询 -->
          <div v-if="activeTab === 'hash'" class="tab-content reveal" data-tab="hash">
            <div class="max-w-2xl mx-auto">
              <input
                v-model="hashInput"
                type="text"
                placeholder="请输入文件哈希值..."
                class="url-input w-full"
              />
          <button class="scan-btn mt-4" @click="queryHash" :disabled="hashLoading">
            {{ hashLoading ? '查询中...' : '查询哈希' }}
          </button>

          <div v-if="hashError" class="mt-4 text-sm text-red-400">
            {{ hashError }}
          </div>

          <div v-if="hashResult" class="mt-4 text-left bg-gray-800 rounded-lg p-4 text-sm">
            <div class="mb-2">
              <span class="font-semibold text-green-400">查询哈希：</span>
              <span class="text-gray-200 break-all">{{ hashResult.hash }}</span>
            </div>
            <div class="mb-2">
              <span class="font-semibold text-green-400">提供方：</span>
              <span class="text-gray-200">{{ hashResult.provider }}</span>
            </div>
            <div class="mt-2 text-gray-300">
              <div class="font-semibold mb-1">原始结果（JSON）：</div>
              <pre class="bg-gray-900 rounded-md p-3 overflow-x-auto text-xs text-gray-200">
{{ formattedHashJson }}
              </pre>
            </div>
          </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 实时统计 -->
      <section class="px-6 py-12">
        <div class="max-w-6xl mx-auto">
          <div class="grid md:grid-cols-4 gap-4 mb-12">
            <div class="feature-card text-center reveal">
              <div class="text-2xl font-bold text-green-400 mb-2">{{ stats.todayScans }}</div>
              <div class="text-sm text-gray-400">今日检测</div>
            </div>
            <div class="feature-card text-center reveal" style="animation-delay: 0.1s;">
              <div class="text-2xl font-bold text-red-400 mb-2">{{ stats.malwareFound }}</div>
              <div class="text-sm text-gray-400">发现恶意</div>
            </div>
            <div class="feature-card text-center reveal" style="animation-delay: 0.2s;">
              <div class="text-2xl font-bold text-yellow-400 mb-2">{{ stats.pendingScans }}</div>
              <div class="text-sm text-gray-400">待处理</div>
            </div>
            <div class="feature-card text-center reveal" style="animation-delay: 0.3s;">
              <div class="text-2xl font-bold text-blue-400 mb-2">{{ stats.engines }}</div>
              <div class="text-sm text-gray-400">检测引擎</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 功能模块 -->
      <section class="px-6 py-12">
        <div class="max-w-6xl mx-auto">
          <h2 class="text-2xl font-semibold mb-8 reveal">核心功能</h2>
          <div class="grid md:grid-cols-3 gap-6">
            <div class="feature-card reveal">
              <div class="feature-icon">
                <svg class="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold mb-2">多引擎检测</h3>
              <p class="text-gray-400 text-sm">整合30+主流杀毒引擎，提供全面的恶意软件检测覆盖</p>
            </div>

            <div class="feature-card reveal" style="animation-delay: 0.1s;">
              <div class="feature-icon">
                <svg class="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold mb-2">实时扫描</h3>
              <p class="text-gray-400 text-sm">毫秒级响应，支持大文件快速预览和深度分析</p>
            </div>

            <div class="feature-card reveal" style="animation-delay: 0.2s;">
              <div class="feature-icon">
                <svg class="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold mb-2">详细报告</h3>
              <p class="text-gray-400 text-sm">提供检测结果、行为分析、相似样本等全方位报告</p>
            </div>

            <div class="feature-card reveal" style="animation-delay: 0.3s;">
              <div class="feature-icon">
                <svg class="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold mb-2">隐私保护</h3>
              <p class="text-gray-400 text-sm">文件不存储，检测过程匿名，保护用户隐私安全</p>
            </div>

            <div class="feature-card reveal" style="animation-delay: 0.4s;">
              <div class="feature-icon">
                <svg class="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold mb-2">开源免费</h3>
              <p class="text-gray-400 text-sm">完全开源免费，无任何功能限制，支持个人和企业使用</p>
            </div>

            <div class="feature-card reveal" style="animation-delay: 0.5s;">
              <div class="feature-icon">
                <svg class="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold mb-2">API支持</h3>
              <p class="text-gray-400 text-sm">提供RESTful API，支持第三方应用集成和批量检测</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 最近检测 -->
      <section class="px-6 py-12">
        <div class="max-w-6xl mx-auto">
          <h2 class="text-2xl font-semibold mb-8 reveal">最近检测动态</h2>
          <div class="stats-panel reveal">
            <div v-for="item in recentScans" :key="item.id" class="stat-item p-4 border-b border-gray-700 last:border-b-0">
              <div class="flex justify-between items-center">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <span class="font-medium">{{ item.filename }}</span>
                    <span :class="getStatusClass(item.status)" class="status-badge">
                      {{ getStatusText(item.status) }}
                    </span>
                  </div>
                  <div class="text-sm text-gray-400">
                    {{ item.timestamp }} • {{ item.size }}
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm text-gray-400 mb-1">检测进度</div>
                  <div class="progress-bar w-24">
                    <div :class="getProgressClass(item.status)" class="progress-fill" :style="{ width: item.progress + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 检测引擎 -->
      <section class="px-6 py-12">
        <div class="max-w-6xl mx-auto">
          <h2 class="text-2xl font-semibold mb-8 reveal">检测引擎覆盖</h2>
          <div class="stats-panel p-6 reveal">
            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              <div v-for="engine in engines" :key="engine.name" class="text-center p-3 rounded-lg bg-gray-800">
                <div class="text-green-400 font-semibold text-sm">{{ engine.name }}</div>
                <div class="text-xs text-gray-400 mt-1">{{ engine.version }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <footer class="px-6 py-12 border-t border-gray-700">
        <div class="max-w-6xl mx-auto">
          <div class="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 class="text-lg font-semibold text-green-400 mb-4">FoxHunter</h3>
              <p class="text-gray-400 text-sm">专业的恶意软件检测平台</p>
            </div>
            <div>
              <h4 class="font-semibold mb-4">产品</h4>
              <ul class="space-y-2 text-sm text-gray-400">
                <li><a href="#" class="hover:text-white">文件检测</a></li>
                <li><a href="#" class="hover:text-white">URL检测</a></li>
                <li><a href="#" class="hover:text-white">API文档</a></li>
              </ul>
            </div>
            <div>
              <h4 class="font-semibold mb-4">支持</h4>
              <ul class="space-y-2 text-sm text-gray-400">
                <li><a href="#" class="hover:text-white">帮助中心</a></li>
                <li><a href="#" class="hover:text-white">联系我们</a></li>
                <li><a href="#" class="hover:text-white">状态监控</a></li>
              </ul>
            </div>
            <div>
              <h4 class="font-semibold mb-4">关于</h4>
              <ul class="space-y-2 text-sm text-gray-400">
                <li><a href="#" class="hover:text-white">开源项目</a></li>
                <li><a href="#" class="hover:text-white">隐私政策</a></li>
                <li><a href="#" class="hover:text-white">使用条款</a></li>
              </ul>
            </div>
          </div>
          <div class="pt-8 border-t border-gray-700 text-center text-sm text-gray-400">
            © 2024 FoxHunter. 开源免费的恶意软件检测平台.
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../lib/api'

// 响应式数据
const activeTab = ref('file')
const selectedFile = ref(null)
const urlInput = ref('')
const hashInput = ref('')
const fileInput = ref(null)
const starfield = ref(null)
const fireflies = ref(null)
// const router = useRouter()

// 统计数据
const stats = ref({
  todayScans: 1247,
  malwareFound: 89,
  pendingScans: 23,
  engines: 32
})

// 最近检测：从后端动态获取
const recentScans = ref([])
const recentLoading = ref(false)
const recentError = ref('')

// 首页上传检测状态
const uploading = ref(false)
const uploadResult = ref(null)
const uploadError = ref('')

// 检测引擎
const engines = ref([
  { name: 'CXN_ML', version: '1.0.1' },
  { name: 'YARA', version: '4.2.3' },
  { name: 'VirusTotal', version: 'API v3' },
  { name: 'MalwareBazaar', version: '1.0' },
  { name: 'Hybrid Analysis', version: '2.1' },
  { name: 'Joe Sandbox', version: '3.0' }
])

// 萤火虫动画数据
const firefliesData = ref([])

// 文件处理方法
const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const handleFileDrop = (event) => {
  event.preventDefault()
  const files = event.dataTransfer.files
  if (files.length > 0) {
    selectedFile.value = files[0]
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// URL 检测结果
const urlLoading = ref(false)
const urlResult = ref(null)
const urlError = ref('')

const formattedUrlJson = computed(() => {
  if (!urlResult.value) return ''
  try {
    return JSON.stringify(urlResult.value.raw_result ?? urlResult.value, null, 2)
  } catch (e) {
    return String(urlResult.value)
  }
})

// 哈希查询结果
const hashLoading = ref(false)
const hashResult = ref(null)
const hashError = ref('')

const formattedHashJson = computed(() => {
  if (!hashResult.value) return ''
  try {
    return JSON.stringify(hashResult.value.raw_result ?? hashResult.value, null, 2)
  } catch (e) {
    return String(hashResult.value)
  }
})

// URL和哈希处理方法
const scanUrl = async () => {
  if (!urlInput.value) return
  urlError.value = ''
  urlResult.value = null
  urlLoading.value = true
  try {
    const resp = await api.get('/api/v1/url/scan', {
      params: { url: urlInput.value }
    })
    urlResult.value = resp.data
  } catch (e) {
    console.error('URL 检测失败', e)
    urlError.value = 'URL 检测失败，请稍后重试或检查后端 URL 扫描服务是否已部署。'
  } finally {
    urlLoading.value = false
  }
}

const queryHash = async () => {
  if (!hashInput.value) return
  hashError.value = ''
  hashResult.value = null
  hashLoading.value = true
  try {
    const resp = await api.get('/api/v1/hash/scan', {
      params: { file_hash: hashInput.value }
    })
    hashResult.value = resp.data
  } catch (e) {
    console.error('哈希查询失败', e)
    hashError.value = '哈希查询失败，请稍后重试或检查后端 VirusTotal API Key 是否已配置。'
  } finally {
    hashLoading.value = false
  }
}

// 首页文件上传并检测（与 Upload 页逻辑一致）
const uploadFile = async () => {
  if (!selectedFile.value || uploading.value) return

  uploadError.value = ''
  uploadResult.value = null
  uploading.value = true

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const response = await api.post('/api/v1/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    uploadResult.value = {
      id: response.data.sample_id,
      filename: selectedFile.value.name,
      status: 'pending',
      result: null
    }
    pollResult(response.data.sample_id)
  } catch (error) {
    console.error('首页上传失败:', error)
    if (error.response && error.response.status === 401) {
      uploadError.value = '请先登录后再进行文件检测。'
    } else {
      uploadError.value = '上传或检测失败，请稍后重试。'
    }
  } finally {
    uploading.value = false
  }
}

const pollResult = async (sampleId) => {
  const poll = async () => {
    try {
      const response = await api.get(`/api/v1/result/${sampleId}`)
      uploadResult.value = response.data
      if (response.data.status === 'completed' || response.data.status === 'failed') {
        return
      }
      setTimeout(poll, 2000)
    } catch (error) {
      console.error('结果轮询失败:', error)
    }
  }
  poll()
}

// 最近检测动态
const fetchRecentScans = async () => {
  recentLoading.value = true
  recentError.value = ''
  try {
    const resp = await api.get('/api/v1/samples/recent')
    const items = resp.data?.items ?? []
    recentScans.value = items.map((item) => ({
      id: item.id,
      filename: item.filename,
      status: item.status,
      timestamp: new Date(item.created_at).toLocaleString(),
      // 复用 size 字段展示（脱敏后的）用户名
      size: item.username ? `用户：${item.username}` : '',
      progress: 100
    }))
  } catch (e) {
    console.error('加载最近检测动态失败', e)
    recentError.value = '加载最近检测动态失败，请稍后重试。'
  } finally {
    recentLoading.value = false
  }
}

// 状态相关方法
const getStatusClass = (status) => {
  switch (status) {
    case 'safe': return 'status-safe'
    case 'malware': return 'status-danger'
    case 'suspicious': return 'status-warning'
    default: return 'status-safe'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'safe': return '安全'
    case 'malware': return '恶意'
    case 'suspicious': return '可疑'
    case 'processing': return '检测中'
    case 'completed': return '完成'
    default: return status
  }
}

const getProgressClass = (status) => {
  switch (status) {
    case 'malware': return 'bg-red-500'
    case 'safe': return 'bg-green-500'
    case 'processing': return 'bg-yellow-500'
    default: return 'bg-gray-500'
  }
}

// 动画和特效
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

// 滚动显示动画
const handleReveal = () => {
  const reveals = document.querySelectorAll('.reveal')
  const windowHeight = window.innerHeight

  reveals.forEach(el => {
    const elementTop = el.getBoundingClientRect().top
    const elementVisible = 100

    if (elementTop < windowHeight - elementVisible) {
      el.classList.add('visible')
    }
  })
}

// 监听 activeTab 变化，立即显示对应的 tab 内容
watch(activeTab, (newTab) => {
  nextTick(() => {
    // 移除所有 tab-content 的 visible 类
    const tabContents = document.querySelectorAll('.tab-content')
    tabContents.forEach(el => el.classList.remove('visible'))
    // 添加 visible 类给当前激活的 tab
    const activeContent = document.querySelector(`.tab-content[data-tab="${newTab}"]`)
    if (activeContent) activeContent.classList.add('visible')
  })
})

// 生命周期
onMounted(() => {
  createStarfield()
  createFireflies()
  animateFireflies()
  handleReveal()
  window.addEventListener('scroll', handleReveal)

  // 为初始激活的 tab 添加 visible 类
  nextTick(() => {
    const activeContent = document.querySelector(`.tab-content[data-tab="${activeTab.value}"]`)
    if (activeContent) activeContent.classList.add('visible')
  })

  // 加载最近检测动态
  fetchRecentScans()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleReveal)
})
</script>

<style>
/* Global styles needed for dynamically injected elements (stars, fireflies, animations) */
/* 自定义CSS变量和样式 */
:root {
  --bg-deep: #050510;
  --bg-primary: #0a0a1a;
  --bg-secondary: #0f0f24;
  --bg-card: rgba(15, 15, 40, 0.7);
  --accent: #00d4aa;
  --accent-glow: rgba(0, 212, 170, 0.3);
  --text-primary: #e8e8f0;
  --text-secondary: #8888a0;
  --border: rgba(100, 100, 140, 0.2);
  --warning: #ff6b4a;
  --safe: #00d4aa;
  --suspicious: #ffc107;
}

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

/* 萤火虫粒子 */
.firefly {
  position: absolute;
  width: 4px;
  height: 4px;
  background: var(--accent);
  border-radius: 50%;
  box-shadow:
    0 0 6px 2px var(--accent),
    0 0 12px 4px var(--accent-glow),
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

<style scoped>

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Space Grotesk', sans-serif;
  background: var(--bg-deep);
  color: var(--text-primary);
  min-height: 100vh;
  overflow-x: hidden;
}

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
  background: var(--accent);
  border-radius: 50%;
  box-shadow:
    0 0 6px 2px var(--accent),
    0 0 12px 4px var(--accent-glow),
    0 0 20px 6px rgba(0, 212, 170, 0.1);
  pointer-events: none;
  z-index: 1;
  animation: firefly-glow 3s ease-in-out infinite;
}

@keyframes firefly-glow {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}

/* 主容器 */
.main-container {
  position: relative;
  z-index: 10;
  min-height: 100vh;
}

/* 上传区域 */
.upload-zone {
  background: var(--bg-card);
  border: 2px dashed var(--border);
  border-radius: 16px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.upload-zone::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0, 212, 170, 0.05) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.upload-zone:hover,
.upload-zone.drag-over {
  border-color: var(--accent);
  background: rgba(15, 15, 40, 0.9);
  box-shadow: 0 0 40px var(--accent-glow);
}

.upload-zone:hover::before,
.upload-zone.drag-over::before {
  opacity: 1;
}

.upload-icon {
  transition: transform 0.4s ease;
}

.upload-zone:hover .upload-icon {
  transform: translateY(-4px);
}

/* 扫描按钮 */
.scan-btn {
  background: linear-gradient(135deg, var(--accent) 0%, #00a080 100%);
  color: var(--bg-deep);
  font-weight: 600;
  border: none;
  border-radius: 12px;
  padding: 14px 32px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.scan-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.scan-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px var(--accent-glow);
}

.scan-btn:hover::before {
  transform: translateX(100%);
}

.scan-btn:active {
  transform: translateY(0);
}

/* Tab切换 */
.tab-btn {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 10px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  font-size: 14px;
}

.tab-btn:first-child {
  border-radius: 8px 0 0 8px;
}

.tab-btn:last-child {
  border-radius: 0 8px 8px 0;
}

.tab-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--bg-deep);
}

.tab-btn:hover:not(.active) {
  border-color: var(--accent);
  color: var(--text-primary);
}

/* URL输入框 */
.url-input {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  width: 100%;
  transition: all 0.3s ease;
}

.url-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 20px var(--accent-glow);
}

.url-input::placeholder {
  color: var(--text-secondary);
}

/* 功能卡片 */
.feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 212, 170, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.feature-card:hover::before {
  opacity: 1;
}

.feature-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, rgba(0, 212, 170, 0.2) 0%, rgba(0, 212, 170, 0.05) 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

/* 统计面板 */
.stats-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
}

.stat-item {
  border-bottom: 1px solid var(--border);
  transition: background 0.3s ease;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-item:hover {
  background: rgba(0, 212, 170, 0.03);
}

.progress-bar {
  height: 6px;
  background: rgba(100, 100, 140, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 1s ease-out;
}

/* 滚动显示动画 */
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}

/* 状态标签 */
.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-safe {
  background: rgba(0, 212, 170, 0.15);
  color: var(--safe);
}

.status-warning {
  background: rgba(255, 193, 7, 0.15);
  color: var(--suspicious);
}

.status-danger {
  background: rgba(255, 107, 74, 0.15);
  color: var(--warning);
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
  background: rgba(100, 100, 140, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 100, 140, 0.5);
}

/* 响应式 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem !important;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }
}

/* 减少动画 */
@media (prefers-reduced-motion: reduce) {
  .star,
  .firefly,
  .reveal {
    animation: none;
    transition: none;
  }

  .reveal {
    opacity: 1;
    transform: none;
  }
}
</style>