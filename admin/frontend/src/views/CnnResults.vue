<template>
  <div class="page-card">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="图片名/标签" clearable style="width: 200px" />
      <el-input v-model="filterSampleId" placeholder="样本ID" clearable style="width: 110px" />
      <el-button type="primary" @click="load">查询</el-button>
      <el-button type="success" @click="openCreate">新增</el-button>
    </div>
    <el-table v-loading="loading" :data="items" stripe border class="mt-3" max-height="520">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="sample_id" label="样本ID" width="90" />
      <el-table-column prop="image_name" label="灰度图" min-width="130" show-overflow-tooltip />
      <el-table-column prop="predicted_label" label="预测类别" width="120" />
      <el-table-column prop="predicted_index" label="索引" width="70" />
      <el-table-column prop="probability" label="置信度" width="100">
        <template #default="{ row }">{{ row.probability?.toFixed?.(4) ?? row.probability }}</template>
      </el-table-column>
      <el-table-column prop="is_malware" label="恶意" width="70">
        <template #default="{ row }">{{ row.is_malware ? "是" : "否" }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="170" />
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

    <el-dialog v-model="visible" :title="editId ? '编辑检测记录' : '新增检测记录'" width="560px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-form-item label="样本ID" prop="sample_id">
          <el-input-number v-model="form.sample_id" :min="1" class="w-full" />
        </el-form-item>
        <el-form-item label="图片文件名" prop="image_name">
          <el-input v-model="form.image_name" />
        </el-form-item>
        <el-form-item label="图片路径" prop="image_path">
          <el-input v-model="form.image_path" />
        </el-form-item>
        <el-form-item label="预测索引" prop="predicted_index">
          <el-input-number v-model="form.predicted_index" :min="0" class="w-full" />
        </el-form-item>
        <el-form-item label="预测标签" prop="predicted_label">
          <el-input v-model="form.predicted_label" />
        </el-form-item>
        <el-form-item label="置信度" prop="probability">
          <el-input-number v-model="form.probability" :min="0" :max="1" :step="0.01" class="w-full" />
        </el-form-item>
        <el-form-item label="是否恶意">
          <el-switch v-model="form.is_malware" />
        </el-form-item>
        <el-form-item label="权重路径">
          <el-input v-model="form.weights_path" />
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
import { ElMessageBox } from "element-plus";

const loading = ref(false);
const saving = ref(false);
const items = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const keyword = ref("");
const filterSampleId = ref("");

const visible = ref(false);
const editId = ref(null);
const formRef = ref();
const form = reactive({
  sample_id: 1,
  image_name: "",
  image_path: "",
  predicted_index: 0,
  predicted_label: "",
  probability: 0.5,
  is_malware: true,
  weights_path: "",
});

const rules = {
  sample_id: [{ required: true, message: "必填", trigger: "blur" }],
  image_name: [{ required: true, message: "必填", trigger: "blur" }],
  image_path: [{ required: true, message: "必填", trigger: "blur" }],
  predicted_label: [{ required: true, message: "必填", trigger: "blur" }],
};

function openCreate() {
  editId.value = null;
  Object.assign(form, {
    sample_id: 1,
    image_name: "",
    image_path: "",
    predicted_index: 0,
    predicted_label: "",
    probability: 0.5,
    is_malware: true,
    weights_path: "",
  });
  visible.value = true;
}

function openEdit(row) {
  editId.value = row.id;
  form.sample_id = row.sample_id;
  form.image_name = row.image_name;
  form.image_path = row.image_path;
  form.predicted_index = row.predicted_index;
  form.predicted_label = row.predicted_label;
  form.probability = row.probability;
  form.is_malware = !!row.is_malware;
  form.weights_path = row.weights_path || "";
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
    };
    if (filterSampleId.value) params.sample_id = Number(filterSampleId.value);
    const { data } = await http.get("/cnn-results", { params });
    items.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

async function submit() {
  await formRef.value?.validate().catch(() => null);
  saving.value = true;
  try {
    const body = { ...form, weights_path: form.weights_path || null };
    if (editId.value) {
      await http.put(`/cnn-results/${editId.value}`, body);
    } else {
      await http.post("/cnn-results", body);
    }
    visible.value = false;
    await load();
  } finally {
    saving.value = false;
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除记录 #${row.id}？`, "提示", { type: "warning" });
  await http.delete(`/cnn-results/${row.id}`);
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
