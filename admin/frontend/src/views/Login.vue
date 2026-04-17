<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="login-title">FoxHunter 管理后台</div>
      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent>
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="管理员账号"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
            :prefix-icon="Lock"
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            :loading="loading"
            @click="onSubmit"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { User, Lock } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import { ElMessage } from "element-plus";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const loading = ref(false);
const formRef = ref();

const form = reactive({
  username: "",
  password: "",
});

const rules = {
  username: [{ required: true, message: "请输入账号", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

async function onSubmit() {
  await formRef.value?.validate().catch(() => null);
  if (!form.username || !form.password) return;
  loading.value = true;
  try {
    await auth.login(form.username, form.password);
    ElMessage.success("登录成功");
    const redirect = route.query.redirect || "/dashboard";
    router.replace(redirect);
  } finally {
    loading.value = false;
  }
}
</script>
