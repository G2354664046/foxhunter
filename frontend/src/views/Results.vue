<template>
  <div class="min-h-screen bg-gray-900 text-white py-10">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-2xl font-bold text-green-400 mb-8 text-center">
        检测结果
      </h1>

      <div v-if="loading" class="text-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400 mx-auto"></div>
        <p class="mt-4 text-gray-400">加载中…</p>
      </div>

      <template v-else-if="result">
        <!-- 圆环 + 摘要 -->
        <div class="grid gap-6 md:grid-cols-2 md:items-stretch">
          <div
            class="bg-gray-800/80 rounded-xl border border-gray-700 p-4 flex flex-col items-center justify-center min-h-[280px]"
          >
            <p class="text-xs text-gray-500 mb-2 w-full text-center">
              {{ voteCaption }}
            </p>
            <div ref="donutChartEl" class="w-full h-[220px]"></div>
          </div>

          <div
            class="bg-gray-800/80 rounded-xl border border-gray-700 p-6 flex flex-col justify-center"
          >
            <h2 class="text-lg font-semibold text-green-400 mb-4">摘要</h2>
            <dl class="space-y-3 text-sm">
              <div class="flex justify-between gap-4 border-b border-gray-700 pb-2">
                <dt class="text-gray-500 shrink-0">检测类型</dt>
                <dd class="text-gray-200 text-right">{{ kindLabel }}</dd>
              </div>
              <div class="flex justify-between gap-4 border-b border-gray-700 pb-2">
                <dt class="text-gray-500 shrink-0">综合判定</dt>
                <dd :class="verdictClass" class="text-right font-semibold">
                  {{ verdictText }}
                </dd>
              </div>
              <div class="flex justify-between gap-4 border-b border-gray-700 pb-2">
                <dt class="text-gray-500 shrink-0">{{ subjectLabel }}</dt>
                <dd class="text-gray-200 text-right break-all">{{ result.filename }}</dd>
              </div>
              <div class="flex justify-between gap-4 border-b border-gray-700 pb-2">
                <dt class="text-gray-500 shrink-0">状态</dt>
                <dd :class="getStatusColor(result.status)" class="text-right">
                  {{ getStatusText(result.status) }}
                </dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-gray-500 shrink-0">检测时间</dt>
                <dd class="text-gray-200 text-right">{{ formatDate(result.created_at) }}</dd>
              </div>
            </dl>
          </div>
        </div>

        <!-- 切换 -->
        <div class="mt-8 flex rounded-lg overflow-hidden border border-gray-700 bg-gray-800/50">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            type="button"
            class="flex-1 py-3 px-2 text-sm font-medium transition sm:text-base"
            :class="
              activePanel === tab.key
                ? 'bg-green-600/20 text-green-400 border-b-2 border-green-500'
                : 'text-gray-400 hover:text-gray-200 border-b-2 border-transparent'
            "
            @click="activePanel = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 面板内容 -->
        <div class="mt-4 rounded-xl border border-gray-700 bg-gray-800/60 p-6 min-h-[240px]">
          <!-- 检测结果 -->
          <div v-show="activePanel === 'result'" class="space-y-6">
            <div v-if="parsedResult">
              <p class="text-gray-300 mb-4">
                综合 <strong class="text-gray-200">cxn_random_forest</strong>、<strong class="text-gray-200">cxn_cnn</strong>（占位）与
                <strong class="text-gray-200">VirusTotal</strong> 多引擎结果；圆环在有 VT 数据时同步为多引擎恶意/总数比。
              </p>
              <p v-if="parsedResult.cxn_models_note" class="text-xs text-gray-500 mb-4">
                {{ parsedResult.cxn_models_note }}
              </p>
              <div class="grid sm:grid-cols-2 gap-6">
                <div class="bg-gray-900/60 rounded-lg p-4">
                  <h3 class="text-sm font-semibold text-green-400 mb-3">综合结论</h3>
                  <p class="text-xl font-bold" :class="parsedResult.is_malware ? 'text-red-400' : 'text-green-400'">
                    {{ parsedResult.is_malware ? '恶意软件' : '安全文件' }}
                  </p>
                  <p class="text-sm text-gray-500 mt-2">
                    置信度 {{ (parsedResult.confidence * 100).toFixed(1) }}%
                  </p>
                </div>
                <div class="bg-gray-900/60 rounded-lg p-4">
                  <h3 class="text-sm font-semibold text-green-400 mb-3">cxn 模型得分（占位）</h3>
                  <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="text-gray-400">cxn_random_forest</span>
                      <span>{{ (parsedResult.rf_score * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-400">cxn_cnn</span>
                      <span>{{ (parsedResult.cnn_score * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                  <div ref="barChartEl" class="mt-6 h-40 w-full"></div>
                </div>
              </div>

              <!-- VirusTotal -->
              <div
                v-if="parsedResult.virustotal?.configured && parsedResult.virustotal.status === 'ok'"
                class="mt-6 bg-gray-900/60 rounded-lg p-4 border border-gray-700"
              >
                <h3 class="text-sm font-semibold text-green-400 mb-3">VirusTotal 多引擎</h3>
                <div class="grid sm:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span class="text-gray-500">恶意 / 可疑引擎数</span>
                    <p class="text-lg font-mono text-gray-100">
                      {{ parsedResult.virustotal.stats?.malicious_votes ?? 0 }}
                      <span class="text-gray-500">/</span>
                      {{ parsedResult.virustotal.stats?.total_engines ?? '—' }}
                    </p>
                  </div>
                  <div v-if="parsedResult.virustotal.meaningful_name" class="text-gray-400 break-all">
                    VT 名称：{{ parsedResult.virustotal.meaningful_name }}
                  </div>
                </div>
                <a
                  v-if="parsedResult.virustotal.permalink"
                  :href="parsedResult.virustotal.permalink"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-block mt-3 text-green-400 hover:text-green-300 text-sm"
                >
                  在 VirusTotal 网页查看 →
                </a>
              </div>
              <div
                v-else-if="parsedResult.virustotal && !parsedResult.virustotal.configured"
                class="mt-6 text-sm text-gray-500 bg-gray-900/40 rounded-lg p-4"
              >
                未配置 VIRUSTOTAL_API_KEY，已跳过 VirusTotal 云端检测。
              </div>
              <div
                v-else-if="parsedResult.virustotal?.status === 'error'"
                class="mt-6 text-sm text-red-400/90 bg-red-950/30 rounded-lg p-4"
              >
                VirusTotal：{{ parsedResult.virustotal.error || '请求失败' }}
              </div>
            </div>
            <div v-else-if="result.result" class="text-gray-300 text-sm">
              <p class="mb-2 text-gray-500">未解析为 JSON 模型结果，原始结果见「详细信息」。</p>
            </div>
            <div v-else class="text-gray-500 text-sm">
              暂无检测结果，请稍后刷新或查看「详细信息」。
            </div>
          </div>

          <!-- 详细信息 -->
          <div v-show="activePanel === 'detail'" class="space-y-4">
            <label class="block text-xs text-gray-500">原始 JSON / 文本</label>
            <pre
              class="bg-gray-900 rounded-lg p-4 text-xs text-gray-300 overflow-x-auto max-h-[480px] overflow-y-auto"
            >{{ detailJson }}</pre>
          </div>

          <!-- 社区讨论 -->
          <div v-show="activePanel === 'community'" class="space-y-4">
            <p class="text-gray-400 text-sm">
              社区讨论功能即将开放，敬请期待。您可在此留下对样本判定的意见或参考链接（占位）。
            </p>
            <textarea
              rows="5"
              disabled
              class="w-full rounded-lg bg-gray-900 border border-gray-700 border-dashed px-3 py-2 text-sm text-gray-500 cursor-not-allowed resize-none"
              placeholder="讨论区暂未开放…"
            />
            <p class="text-xs text-gray-600">提示：上线后将支持用户评论与引用情报。</p>
          </div>
        </div>
      </template>

      <div v-else class="text-center py-16">
        <p class="text-gray-400">未找到检测结果</p>
        <router-link to="/" class="text-green-400 hover:text-green-300 mt-4 inline-block">
          返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../lib/api'
import * as echarts from 'echarts'

const RESULTS_PREVIEW_KEY = 'foxhunter_results_preview'

const route = useRoute()
const result = ref(null)
const loading = ref(true)
const parsedResult = ref(null)
const donutChartEl = ref(null)
const barChartEl = ref(null)
const activePanel = ref('result')

const tabs = [
  { key: 'result', label: '检测结果' },
  { key: 'detail', label: '详细信息' },
  { key: 'community', label: '社区讨论' }
]

/** file | url | hash — 用于圆环占位（默认 file） */
const resultKind = computed(() => {
  const t = (route.query.type || 'file').toString().toLowerCase()
  if (t === 'url' || t === 'hash') return t
  return 'file'
})

const kindLabel = computed(() => {
  const k = resultKind.value
  if (k === 'url') return 'URL 检测'
  if (k === 'hash') return '哈希查询'
  return '文件检测（样本）'
})

const subjectLabel = computed(() => {
  const k = resultKind.value
  if (k === 'url') return '检测 URL'
  if (k === 'hash') return '哈希值'
  return '文件名'
})

const voteCaption = computed(() => {
  if (resultKind.value === 'file') {
    const vt = parsedResult.value?.virustotal
    if (vt?.status === 'ok' && vt.stats?.total_engines) {
      return '多引擎投票（VirusTotal；cxn_random_forest / cxn_cnn 为占位分数）'
    }
    return '多引擎投票（无 VirusTotal 数据时为占位 1/10）'
  }
  return '单引擎结果（当前哈希/URL 仅 1 个检测 API）'
})

const voteStats = computed(() => {
  if (resultKind.value === 'url' || resultKind.value === 'hash') {
    const mal = parsedResult.value?.is_malware ? 1 : 0
    return {
      malicious: mal,
      total: 1,
      label: '1/1'
    }
  }
  const vt = parsedResult.value?.virustotal
  if (vt?.status === 'ok' && vt.stats?.total_engines) {
    const mal = Number(vt.stats.malicious_votes ?? 0)
    const total = Math.max(Number(vt.stats.total_engines), 1)
    return {
      malicious: mal,
      total,
      label: `${mal}/${total}`
    }
  }
  return {
    malicious: 1,
    total: 10,
    label: '1/10'
  }
})

const verdictText = computed(() => {
  if (!result.value) return '—'
  if (result.value.status !== 'completed') {
    return result.value.status === 'failed' ? '检测失败' : '处理中'
  }
  if (parsedResult.value && typeof parsedResult.value.is_malware === 'boolean') {
    return parsedResult.value.is_malware ? '恶意' : '安全'
  }
  if (result.value.result) return '已返回（未解析）'
  return '暂无结果'
})

const verdictClass = computed(() => {
  if (!result.value || result.value.status !== 'completed') return 'text-gray-300'
  if (parsedResult.value && typeof parsedResult.value.is_malware === 'boolean') {
    return parsedResult.value.is_malware ? 'text-red-400' : 'text-green-400'
  }
  return 'text-gray-200'
})

const detailJson = computed(() => {
  if (!result.value) return ''
  const r = result.value.result
  if (r == null || r === '') return '（无）'
  if (typeof r === 'string') {
    try {
      return JSON.stringify(JSON.parse(r), null, 2)
    } catch {
      return r
    }
  }
  return JSON.stringify(r, null, 2)
})

let donutChart = null
let barChart = null

function buildDonutOption() {
  const { malicious, total, label } = voteStats.value
  const safe = Math.max(0, total - malicious)
  return {
    series: [
      {
        type: 'pie',
        radius: ['52%', '72%'],
        avoidLabelOverlap: false,
        itemStyle: { borderColor: '#1f2937', borderWidth: 2 },
        label: { show: false },
        emphasis: { disabled: true },
        data: [
          { value: malicious, name: '恶意', itemStyle: { color: '#f87171' } },
          { value: safe, name: '未判定恶意', itemStyle: { color: '#4ade80' } }
        ]
      }
    ],
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: '42%',
        style: {
          text: label,
          fill: '#f3f4f6',
          fontSize: 22,
          fontWeight: 'bold'
        }
      },
      {
        type: 'text',
        left: 'center',
        top: '54%',
        style: {
          text: '投票数',
          fill: '#9ca3af',
          fontSize: 12
        }
      }
    ],
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    }
  }
}

function renderDonut() {
  nextTick(() => {
    if (!donutChartEl.value || !result.value) return
    if (!donutChart) donutChart = echarts.init(donutChartEl.value)
    donutChart.setOption(buildDonutOption(), true)
  })
}

function renderBar() {
  if (!parsedResult.value) return
  nextTick(() => {
    if (!barChartEl.value || !parsedResult.value) return
    if (!barChart) barChart = echarts.init(barChartEl.value)
    const v = parsedResult.value
    barChart.setOption({
      grid: { left: 40, right: 16, top: 16, bottom: 24 },
      xAxis: { type: 'category', data: ['RF', 'CNN'] },
      yAxis: { type: 'value', max: 1, axisLabel: { formatter: (v) => `${(v * 100).toFixed(0)}%` } },
      series: [
        {
          type: 'bar',
          data: [v.rf_score, v.cnn_score],
          itemStyle: { color: '#4ade80', borderRadius: [4, 4, 0, 0] }
        }
      ],
      tooltip: { formatter: '{b}: {c}' }
    })
  })
}

function disposeCharts() {
  donutChart?.dispose()
  donutChart = null
  barChart?.dispose()
  barChart = null
}

function onResize() {
  donutChart?.resize()
  barChart?.resize()
}

let pollTimer = null

function clearPoll() {
  if (pollTimer != null) {
    clearTimeout(pollTimer)
    pollTimer = null
  }
}

function loadFromPreview() {
  const raw = sessionStorage.getItem(RESULTS_PREVIEW_KEY)
  if (!raw) {
    result.value = null
    parsedResult.value = null
    return
  }
  try {
    const { type, data, at } = JSON.parse(raw)
    const created = at ? new Date(at).toISOString() : new Date().toISOString()
    if (type === 'url' && data) {
      result.value = {
        id: null,
        filename: data.url || '—',
        status: 'completed',
        result: JSON.stringify(data),
        created_at: created
      }
    } else if (type === 'hash' && data) {
      result.value = {
        id: null,
        filename: data.hash || data.file_hash || '—',
        status: 'completed',
        result: JSON.stringify(data),
        created_at: created
      }
    }
    if (result.value?.result) {
      try {
        const outer = JSON.parse(result.value.result)
        if (outer && typeof outer.is_malware === 'boolean') {
          parsedResult.value = outer
        } else {
          parsedResult.value = null
        }
      } catch {
        parsedResult.value = null
      }
    }
  } catch (e) {
    console.error(e)
    result.value = null
    parsedResult.value = null
  }
}

async function fetchSampleResult(id) {
  const response = await api.get(`/api/v1/result/${id}`)
  result.value = response.data
  if (response.data.result) {
    try {
      parsedResult.value = JSON.parse(response.data.result)
    } catch {
      parsedResult.value = null
    }
  } else {
    parsedResult.value = null
  }
  return response.data.status
}

async function loadResult(id) {
  clearPoll()
  disposeCharts()
  loading.value = true
  result.value = null
  parsedResult.value = null

  if (id === 'preview') {
    try {
      loadFromPreview()
    } finally {
      loading.value = false
    }
    return
  }

  try {
    const status = await fetchSampleResult(id)
    loading.value = false
    if (status === 'pending' || status === 'processing') {
      const poll = async () => {
        try {
          const s = await fetchSampleResult(id)
          if (s === 'pending' || s === 'processing') {
            pollTimer = setTimeout(poll, 2000)
          }
        } catch (e) {
          console.error(e)
        }
      }
      pollTimer = setTimeout(poll, 2000)
    }
  } catch (e) {
    console.error('Failed to load result:', e)
    loading.value = false
  }
}

watch(
  () => route.params.id,
  (id) => {
    if (id) loadResult(id)
  },
  { immediate: true }
)

onMounted(() => {
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  clearPoll()
  window.removeEventListener('resize', onResize)
  disposeCharts()
})

watch(
  [result, voteStats, resultKind],
  () => {
    nextTick(() => renderDonut())
  },
  { deep: true }
)

watch(
  [parsedResult, activePanel],
  () => {
    if (activePanel.value !== 'result') return
    nextTick(() => renderBar())
  },
  { deep: true }
)

watch(activePanel, (panel) => {
  if (panel === 'result') {
    nextTick(() => {
      renderDonut()
      renderBar()
    })
  }
})

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusColor = (status) => {
  switch (status) {
    case 'completed':
      return 'text-green-400'
    case 'failed':
      return 'text-red-400'
    case 'processing':
      return 'text-yellow-400'
    default:
      return 'text-gray-400'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'completed':
      return '检测完成'
    case 'failed':
      return '检测失败'
    case 'processing':
      return '检测中'
    default:
      return '等待中'
  }
}
</script>

<style scoped>
</style>
