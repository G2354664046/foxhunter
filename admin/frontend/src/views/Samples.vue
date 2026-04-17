<template>
  <div class="page-card">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="文件名/哈希" clearable style="width: 200px" />
      <el-input v-model="filterUserId" placeholder="用户ID" clearable style="width: 100px" />
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 130px">
        <el-option label="pending" value="pending" />
        <el-option label="processing" value="processing" />
        <el-option label="completed" value="completed" />
        <el-option label="failed" value="failed" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
      <el-button type="success" @click="openCreate">新增</el-button>
    </div>
    <el-table v-loading="loading" :data="items" stripe border class="mt-3" max-height="520">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="user_id" label="用户" width="80" />
      <el-table-column prop="filename" label="文件名" min-width="140" show-overflow-tooltip />
      <el-table-column prop="sample_type" label="类型" width="90" />
      <el-table-column prop="hash" label="SHA256" min-width="160" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="140" fixed="right">
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

    <el-dialog v-model="visible" :title="editId ? '编辑样本' : '新增样本'" width="640px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户ID" prop="user_id">
          <el-input-number v-model="form.user_id" :min="1" class="w-full" />
        </el-form-item>
        <el-form-item label="文件名" prop="filename">
          <el-input v-model="form.filename" />
        </el-form-item>
        <el-form-item label="样本类型" prop="sample_type">
          <el-select v-model="form.sample_type" class="w-full">
            <el-option label="file" value="file" />
            <el-option label="url" value="url" />
            <el-option label="hash" value="hash" />
          </el-select>
        </el-form-item>
        <el-form-item label="SHA256" prop="hash">
          <el-input v-model="form.hash" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" class="w-full">
            <el-option label="pending" value="pending" />
            <el-option label="processing" value="processing" />
            <el-option label="completed" value="completed" />
            <el-option label="failed" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务ID">
          <el-input v-model="form.task_id" />
        </el-form-item>
        <el-form-item label="result 文本">
          <el-input v-model="form.result" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="result_json">
          <el-input
            v-model="form.resultJsonStr"
            type="textarea"
            :rows="5"
            placeholder='JSON 对象，如 {"key":"value"}，可留空'
          />
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
import { onMounted, reactive, ref } from "vue";
import http from "@/api/http";
import { ElMessage, ElMessageBox } from "element-plus";

const loading = ref(false);
const saving = ref(false);
const items = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const keyword = ref("");
const filterUserId = ref("");
const filterStatus = ref("");

const visible = ref(false);
const editId = ref(null);
const formRef = ref();
const form = reactive({
  user_id: 1,
  filename: "",
  sample_type: "file",
  hash: "",
  status: "pending",
  result: "",
  resultJsonStr: "",
  task_id: "",
});

const rules = {
  user_id: [{ required: true, message: "必填", trigger: "blur" }],
  filename: [{ required: true, message: "必填", trigger: "blur" }],
  hash: [{ required: true, message: "必填", trigger: "blur" }],
};

function parseJsonField() {
  if (!form.resultJsonStr?.trim()) return null;
  return JSON.parse(form.resultJsonStr);
}

function openCreate() {
  editId.value = null;
  Object.assign(form, {
    user_id: 1,
    filename: "",
    sample_type: "file",
    hash: "",
    status: "pending",
    result: "",
    resultJsonStr: "",
    task_id: "",
  });
  visible.value = true;
}

function openEdit(row) {
  editId.value = row.id;
  form.user_id = row.user_id;
  form.filename = row.filename;
  form.sample_type = row.sample_type || "file";
  form.hash = row.hash;
  form.status = row.status;
  form.result = row.result || "";
  form.task_id = row.task_id || "";
  form.resultJsonStr =
    row.result_json != null ? JSON.stringify(row.result_json, null, 2) : "";
  visible.value = true;
}

function onSizeChange() {
  page.value = 1;
  load();
}

async function load() {
  loading.value = true;
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      status: filterStatus.value || undefined,
    };
    if (filterUserId.value) params.user_id = Number(filterUserId.value);
    const { data } = await http.get("/samples", { params });
    items.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

async function submit() {
  await formRef.value?.validate().catch(() => null);
  let resultJson = null;
  try {
    resultJson = parseJsonField();
  } catch {
    ElMessage.error("result_json 不是合法 JSON");
    return;
  }
  saving.value = true;
  try {
    const body = {
      user_id: form.user_id,
      filename: form.filename,
      sample_type: form.sample_type,
      hash: form.hash,
      status: form.status,
      result: form.result || null,
      result_json: resultJson,
      task_id: form.task_id || null,
    };
    if (editId.value) {
      await http.put(`/samples/${editId.value}`, body);
    } else {
      await http.post("/samples", body);
    }
    visible.value = false;
    await load();
  } finally {
    saving.value = false;
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除样本 #${row.id}？`, "提示", { type: "warning" });
  await http.delete(`/samples/${row.id}`);
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
.w-full {
  width: 100%;
}
</style>
