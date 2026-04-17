<template>
  <el-container class="admin-layout">
    <el-aside width="220px" class="admin-sidebar">
      <div class="admin-logo">FoxHunter 后台</div>
      <el-menu
        :default-active="active"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>控制台</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/samples">
          <el-icon><FolderOpened /></el-icon>
          <span>检测记录</span>
        </el-menu-item>
        <el-menu-item index="/cnn-results">
          <el-icon><Document /></el-icon>
          <span>CNN样本</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="admin-header" height="50px">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item v-if="title">{{ title }}</el-breadcrumb-item>
        </el-breadcrumb>
        <div class="flex items-center gap-3">
          <span class="text-gray-500 text-sm">{{ auth.me?.nickname || auth.me?.username }}</span>
          <el-button type="primary" link @click="onLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { Odometer, User, FolderOpened, Document } from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const active = computed(() => route.path);
const title = computed(() => route.meta?.title || "");

async function onLogout() {
  await auth.logout();
  router.push("/login");
}
</script>

<style scoped>
.flex {
  display: flex;
}
.items-center {
  align-items: center;
}
.gap-3 {
  gap: 12px;
}
.text-gray-500 {
  color: #606266;
}
.text-sm {
  font-size: 13px;
}
</style>
