<template>
  <div class="page-card">
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索用户名/邮箱"
        clearable
        style="width: 220px"
        @clear="load"
      />
      <el-button type="primary" @click="load">查询</el-button>
      <el-button type="success" @click="openCreate">新增</el-button>
    </div>
    <el-table v-loading="loading" :data="items" stripe border class="mt-3">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="created_at" label="注册时间" width="180" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="openEdit(row)">编辑</el-button>
          <el-button type="danger" link @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="load"
        @size-change="onSizeChange"
      />
    </div>

    <el-dialog v-model="visible" :title="editId ? '编辑用户' : '新增用户'" width="480px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="88px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password :placeholder="editId ? '留空则不修改' : '至少6位'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import http from "@/api/http";
import { ElMessageBox } from "element-plus";

const loading = ref(false);
const saving = ref(false);
const items = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const keyword = ref("");

const visible = ref(false);
const editId = ref(null);
const formRef = ref();
const form = reactive({
  username: "",
  email: "",
  password: "",
});

const formRules = computed(() => ({
  username: [{ required: true, message: "必填", trigger: "blur" }],
  email: [{ required: true, message: "必填", trigger: "blur" }],
  password: editId.value
    ? []
    : [{ required: true, message: "必填", trigger: "blur" }],
}));

function openCreate() {
  editId.value = null;
  form.username = "";
  form.email = "";
  form.password = "";
  visible.value = true;
}

function openEdit(row) {
  editId.value = row.id;
  form.username = row.username;
  form.email = row.email;
  form.password = "";
  visible.value = true;
}

function onSizeChange() {
  page.value = 1;
  load();
}

async function load() {
  loading.value = true;
  try {
    const { data } = await http.get("/users", {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: keyword.value || undefined,
      },
    });
    items.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

async function submit() {
  const isCreate = !editId.value;
  if (isCreate) {
    await formRef.value?.validate().catch(() => null);
    if (!form.username || !form.email || !form.password) return;
  } else {
    if (!form.username || !form.email) return;
  }
  saving.value = true;
  try {
    if (isCreate) {
      await http.post("/users", {
        username: form.username,
        email: form.email,
        password: form.password,
      });
    } else {
      const body = {
        username: form.username,
        email: form.email,
      };
      if (form.password) body.password = form.password;
      await http.put(`/users/${editId.value}`, body);
    }
    visible.value = false;
    await load();
  } finally {
    saving.value = false;
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除用户「${row.username}」？关联样本将级联删除。`, "提示", {
    type: "warning",
  });
  await http.delete(`/users/${row.id}`);
  await load();
}

onMounted(load);
</script>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.mt-3 {
  margin-top: 12px;
}
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
