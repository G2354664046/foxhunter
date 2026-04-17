<template>
  <div>
    <el-row :gutter="16" class="mb-4">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="num">{{ summary.users ?? "-" }}</div>
          <div class="label">注册用户</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="num">{{ summary.samples ?? "-" }}</div>
          <div class="label">样本总数</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="num">{{ summary.cnn_results ?? "-" }}</div>
          <div class="label">CNN 检测记录</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="num">{{ summary.samples_by_status?.completed ?? "-" }}</div>
          <div class="label">已完成样本</div>
        </el-card>
      </el-col>
    </el-row>

    <div class="page-card mb-4">
      <div class="section-title">样本状态分布</div>
      <el-descriptions :column="4" border size="small" class="mt-3">
        <el-descriptions-item label="待处理">
          {{ summary.samples_by_status?.pending ?? 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="处理中">
          {{ summary.samples_by_status?.processing ?? 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="已完成">
          {{ summary.samples_by_status?.completed ?? 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="失败">
          {{ summary.samples_by_status?.failed ?? 0 }}
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <div class="page-card">
      <div class="section-title">FoxHunter 主系统状态</div>
      <p class="hint">通过 HTTP 探测主 API。</p>
      <el-alert
        v-if="fh.reachable"
        type="success"
        :closable="false"
        show-icon
        class="mt-2"
      >
        <template #title>
          主系统在线 — {{ fh.url }}（HTTP {{ fh.status_code }}）
        </template>
        <pre class="json-pre">{{ JSON.stringify(fh.response, null, 2) }}</pre>
      </el-alert>
      <el-alert v-else type="error" :closable="false" show-icon class="mt-2">
        <template #title>主系统不可达：{{ fh.url }}</template>
        {{ fh.error || "请确认 FoxHunter 后端已启动且 FOXHUNTER_API_BASE 配置正确" }}
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import http from "@/api/http";

const summary = reactive({
  users: 0,
  samples: 0,
  cnn_results: 0,
  samples_by_status: {},
});

const fh = ref({
  reachable: false,
  url: "",
  status_code: null,
  response: null,
  error: "",
});

onMounted(async () => {
  const [{ data: s }, { data: f }] = await Promise.all([
    http.get("/dashboard/summary"),
    http.get("/dashboard/foxhunter"),
  ]);
  Object.assign(summary, s);
  fh.value = f;
});
</script>

<style scoped>
.mb-4 {
  margin-bottom: 16px;
}
.mt-2 {
  margin-top: 8px;
}
.mt-3 {
  margin-top: 12px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
.hint {
  color: #909399;
  font-size: 13px;
  margin: 8px 0 0;
}
.json-pre {
  margin: 8px 0 0;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
