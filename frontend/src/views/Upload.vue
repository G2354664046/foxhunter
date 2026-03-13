<template>
  <div class="min-h-screen bg-gray-900 text-white py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-gray-800 rounded-lg p-8">
        <h2 class="text-2xl font-bold text-green-400 mb-6 text-center">
          文件检测
        </h2>

        <div class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center mb-6">
          <input
            ref="fileInput"
            type="file"
            @change="handleFileSelect"
            class="hidden"
            accept=".exe,.dll,.bin"
          />
          <div v-if="!selectedFile" @click="$refs.fileInput.click()" class="cursor-pointer">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p class="text-gray-300">点击选择文件或拖拽文件到此处</p>
            <p class="text-sm text-gray-500 mt-2">支持 .exe, .dll, .bin 文件</p>
          </div>
          <div v-else class="text-center">
            <p class="text-green-400 font-semibold">{{ selectedFile.name }}</p>
            <p class="text-sm text-gray-400">{{ formatFileSize(selectedFile.size) }}</p>
            <button
              @click="uploadFile"
              :disabled="uploading"
              class="mt-4 bg-green-500 hover:bg-green-600 disabled:bg-gray-600 text-white font-bold py-2 px-4 rounded transition duration-300"
            >
              {{ uploading ? '检测中...' : '开始检测' }}
            </button>
          </div>
        </div>

        <div v-if="uploadResult" class="bg-gray-700 rounded-lg p-4">
          <h3 class="text-lg font-semibold text-green-400 mb-2">检测结果</h3>
          <div class="space-y-2">
            <p><span class="text-gray-400">文件:</span> {{ uploadResult.filename }}</p>
            <p><span class="text-gray-400">状态:</span>
              <span :class="getStatusColor(uploadResult.status)">
                {{ getStatusText(uploadResult.status) }}
              </span>
            </p>
            <p v-if="uploadResult.result"><span class="text-gray-400">结果:</span> {{ uploadResult.result }}</p>
            <router-link
              v-if="uploadResult.id"
              :to="`/results/${uploadResult.id}`"
              class="inline-block mt-2 text-green-400 hover:text-green-300"
            >
              查看详细结果 →
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { api } from '../lib/api'

const fileInput = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadResult = ref(null)

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const response = await api.post('/api/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    uploadResult.value = {
      id: response.data.sample_id,
      filename: selectedFile.value.name,
      status: 'pending',
      result: null
    }
    // Poll for results
    pollResult(response.data.sample_id)
  } catch (error) {
    console.error('Upload failed:', error)
    uploadResult.value = {
      filename: selectedFile.value.name,
      status: 'failed',
      result: '上传失败'
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
      setTimeout(poll, 2000) // Poll every 2 seconds
    } catch (error) {
      console.error('Polling failed:', error)
    }
  }
  poll()
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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
/* Upload page styles */
</style>