<template>
  <div class="min-h-screen bg-gray-900 text-white py-12">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-gray-800 rounded-lg p-6 shadow-lg">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-green-400">检测记录</h2>
          <button
            class="text-sm text-gray-300 hover:text-white underline"
            @click="loadSamples"
          >
            刷新
          </button>
        </div>

        <div v-if="loading" class="text-center py-10 text-gray-400">
          加载中...
        </div>

        <div v-else-if="samples.length === 0" class="text-center py-10 text-gray-400">
          暂无检测记录，先去上传一个样本吧～
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-700">
            <thead class="bg-gray-900">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  ID
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  文件名
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  状态
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  创建时间
                </th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody class="bg-gray-800 divide-y divide-gray-700">
              <tr
                v-for="item in samples"
                :key="item.id"
                class="hover:bg-gray-750 transition-colors"
              >
                <td class="px-4 py-3 text-sm text-gray-300">
                  {{ item.id }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-100 truncate max-w-xs">
                  {{ item.filename }}
                </td>
                <td class="px-4 py-3 text-sm">
                  <span :class="statusClass(item.status)">
                    {{ statusText(item.status) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm text-gray-400 whitespace-nowrap">
                  {{ formatDate(item.created_at) }}
                </td>
                <td class="px-4 py-3 text-sm text-right space-x-2 whitespace-nowrap">
                  <router-link
                    :to="`/results/${item.id}`"
                    class="inline-flex items-center px-3 py-1 rounded-md text-xs font-medium bg-green-500 text-gray-900 hover:bg-green-400"
                  >
                    查看结果
                  </router-link>
                  <button
                    class="inline-flex items-center px-3 py-1 rounded-md text-xs font-medium bg-red-500 text-white hover:bg-red-400"
                    @click="remove(item.id)"
                  >
                    删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../lib/api'

const samples = ref([])
const loading = ref(false)

const loadSamples = async () => {
  loading.value = true
  try {
    const resp = await api.get('/api/v1/samples')
    samples.value = resp.data
  } catch (e) {
    console.error('加载样本列表失败', e)
  } finally {
    loading.value = false
  }
}

const remove = async (id) => {
  if (!confirm('确定要删除这条记录吗？')) return
  try {
    await api.delete(`/api/v1/samples/${id}`)
    samples.value = samples.value.filter((s) => s.id !== id)
  } catch (e) {
    console.error('删除失败', e)
  }
}

const formatDate = (val) => {
  if (!val) return ''
  return new Date(val).toLocaleString('zh-CN')
}

const statusText = (status) => {
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

const statusClass = (status) => {
  switch (status) {
    case 'completed':
      return 'inline-flex px-2 py-1 rounded-full text-xs font-semibold bg-green-500/20 text-green-300'
    case 'failed':
      return 'inline-flex px-2 py-1 rounded-full text-xs font-semibold bg-red-500/20 text-red-300'
    case 'processing':
      return 'inline-flex px-2 py-1 rounded-full text-xs font-semibold bg-yellow-500/20 text-yellow-300'
    default:
      return 'inline-flex px-2 py-1 rounded-full text-xs font-semibold bg-gray-500/20 text-gray-300'
  }
}

onMounted(() => {
  loadSamples()
})
</script>

<style scoped>
.bg-gray-750 {
  background-color: #272a3a;
}
</style>

