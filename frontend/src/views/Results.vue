<template>
  <div class="min-h-screen bg-gray-900 text-white py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-gray-800 rounded-lg p-8">
        <h2 class="text-2xl font-bold text-green-400 mb-6 text-center">
          检测结果详情
        </h2>

        <div v-if="loading" class="text-center py-8">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400 mx-auto"></div>
          <p class="mt-4 text-gray-400">加载中...</p>
        </div>

        <div v-else-if="result" class="space-y-6">
          <!-- 基本信息 -->
          <div class="bg-gray-700 rounded-lg p-4">
            <h3 class="text-lg font-semibold text-green-400 mb-3">基本信息</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="text-gray-400">文件名:</span>
                <span class="ml-2">{{ result.filename }}</span>
              </div>
              <div>
                <span class="text-gray-400">状态:</span>
                <span :class="getStatusColor(result.status)" class="ml-2">
                  {{ getStatusText(result.status) }}
                </span>
              </div>
              <div>
                <span class="text-gray-400">检测时间:</span>
                <span class="ml-2">{{ formatDate(result.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 检测结果 -->
          <div v-if="result.result" class="bg-gray-700 rounded-lg p-4">
            <h3 class="text-lg font-semibold text-green-400 mb-3">检测结果</h3>
            <div class="space-y-4">
              <div v-if="parsedResult">
                <div class="flex items-center mb-4">
                  <span class="text-lg mr-4">检测结果:</span>
                  <span :class="parsedResult.is_malware ? 'text-red-400' : 'text-green-400'" class="text-xl font-bold">
                    {{ parsedResult.is_malware ? '恶意软件' : '安全文件' }}
                  </span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- 置信度图表 -->
                  <div>
                    <h4 class="text-md font-semibold mb-2">置信度分析</h4>
                    <div class="bg-gray-800 p-4 rounded">
                      <div class="flex justify-between mb-2">
                        <span>总体置信度</span>
                        <span>{{ (parsedResult.confidence * 100).toFixed(1) }}%</span>
                      </div>
                      <div class="w-full bg-gray-600 rounded-full h-2">
                        <div
                          class="bg-green-500 h-2 rounded-full"
                          :style="{ width: (parsedResult.confidence * 100) + '%' }"
                        ></div>
                      </div>
                    </div>
                  </div>

                  <!-- 模型详情 + chart -->
                  <div>
                    <h4 class="text-md font-semibold mb-2">模型分析</h4>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span>随机森林得分:</span>
                        <span>{{ (parsedResult.rf_score * 100).toFixed(1) }}%</span>
                      </div>
                      <div class="flex justify-between">
                        <span>CNN得分:</span>
                        <span>{{ (parsedResult.cnn_score * 100).toFixed(1) }}%</span>
                      </div>
                    </div>
                    <div ref="scoreChart" class="mt-4 h-48"></div>
                  </div>
                </div>
              </div>
              <div v-else>
                <pre class="bg-gray-800 p-4 rounded text-sm overflow-x-auto">{{ result.result }}</pre>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!loading" class="text-center py-8">
          <p class="text-gray-400">未找到检测结果</p>
          <router-link to="/upload" class="text-green-400 hover:text-green-300 mt-4 inline-block">
            返回上传页面
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../lib/api'
import * as echarts from 'echarts'

const route = useRoute()
const result = ref(null)
const loading = ref(true)
const parsedResult = ref(null)
const scoreChart = ref(null)

watch(parsedResult, (val) => {
  if (val && scoreChart.value) {
    const chart = echarts.init(scoreChart.value)
    chart.setOption({
      xAxis: { type: 'category', data: ['RF', 'CNN'] },
      yAxis: { type: 'value', max: 1 },
      series: [{ type: 'bar', data: [val.rf_score, val.cnn_score], itemStyle: { color: '#4ade80' } }],
      tooltip: { formatter: '{b}: {c}'}
    })
  }
})

onMounted(async () => {
  const sampleId = route.params.id
  try {
    const response = await api.get(`/api/v1/result/${sampleId}`)
    result.value = response.data
    if (response.data.result) {
      try {
        parsedResult.value = JSON.parse(response.data.result)
      } catch (e) {
        // If not JSON, keep as string
      }
    }
  } catch (error) {
    console.error('Failed to load result:', error)
  } finally {
    loading.value = false
  }
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusColor = (status) => {
  switch (status) {
    case 'completed': return 'text-green-400'
    case 'failed': return 'text-red-400'
    case 'processing': return 'text-yellow-400'
    default: return 'text-gray-400'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'completed': return '检测完成'
    case 'failed': return '检测失败'
    case 'processing': return '检测中'
    default: return '等待中'
  }
}
</script>

<style scoped>
/* Results page styles */
</style>