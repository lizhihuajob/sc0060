<template>
  <div class="reports-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>举报管理</span>
          <div class="header-actions">
            <el-select
              v-model="searchForm.status"
              placeholder="选择状态"
              clearable
              style="width: 120px; margin-right: 10px;"
              @change="handleSearch"
            >
              <el-option label="全部" value="" />
              <el-option label="待处理" value="pending" />
              <el-option label="已处理" value="resolved" />
              <el-option label="已驳回" value="dismissed" />
            </el-select>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="reports" style="width: 100%" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="reporter" label="举报人" width="120">
          <template #default="scope">
            {{ scope.row.reporter?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="举报类型" width="100">
          <template #default="scope">
            <el-tag :type="getTargetTypeTagType(scope.row.target_type)" size="small">
              {{ getTargetTypeName(scope.row.target_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason_name" label="举报原因" width="120" />
        <el-table-column prop="target" label="举报内容" min-width="200" show-overflow-tooltip>
          <template #default="scope">
            <div v-if="scope.row.target">
              <template v-if="scope.row.target_type === 'post'">
                <span class="text-muted">帖子:</span> {{ scope.row.target.title }}
              </template>
              <template v-else-if="scope.row.target_type === 'comment'">
                <span class="text-muted">评论:</span> {{ scope.row.target.content }}
              </template>
              <template v-else-if="scope.row.target_type === 'user'">
                <span class="text-muted">用户:</span> {{ scope.row.target.username }}
              </template>
            </div>
            <span v-else class="text-muted">已删除</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)" size="small">
              {{ scope.row.status_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="举报时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" text @click="viewDetail(scope.row)">
              详情
            </el-button>
            <template v-if="scope.row.status === 'pending'">
              <el-button type="success" text @click="handleResolve(scope.row)">
                处理
              </el-button>
              <el-button type="warning" text @click="handleDismiss(scope.row)">
                驳回
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.perPage"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchReports"
          @current-change="fetchReports"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailVisible" title="举报详情" width="700px">
      <el-descriptions :column="2" border v-if="currentReport">
        <el-descriptions-item label="举报ID">{{ currentReport.id }}</el-descriptions-item>
        <el-descriptions-item label="举报人">
          {{ currentReport.reporter?.username || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="举报类型">
          <el-tag :type="getTargetTypeTagType(currentReport.target_type)" size="small">
            {{ getTargetTypeName(currentReport.target_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="举报原因">{{ currentReport.reason_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTagType(currentReport.status)" size="small">
            {{ currentReport.status_name }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="举报时间">
          {{ formatDate(currentReport.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="详细说明" :span="2">
          {{ currentReport.reason_detail || '无' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">举报目标</el-divider>
      <div class="target-info" v-if="currentReport.target">
        <template v-if="currentReport.target_type === 'post'">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="帖子标题">{{ currentReport.target.title }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="currentReport.target.is_hidden ? 'danger' : 'success'" size="small">
                {{ currentReport.target.is_hidden ? '已下架' : '正常' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </template>
        <template v-else-if="currentReport.target_type === 'comment'">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="评论内容">{{ currentReport.target.content }}</el-descriptions-item>
          </el-descriptions>
        </template>
        <template v-else-if="currentReport.target_type === 'user'">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="用户名">{{ currentReport.target.username }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="currentReport.target.is_banned ? 'danger' : 'success'" size="small">
                {{ currentReport.target.is_banned ? '已封禁' : '正常' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </template>
      </div>
      <el-empty v-else description="目标已被删除" />

      <el-divider content-position="left">处理信息</el-divider>
      <el-descriptions :column="2" border size="small" v-if="currentReport.status !== 'pending'">
        <el-descriptions-item label="处理人">
          {{ currentReport.handler?.username || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="处理时间">
          {{ formatDate(currentReport.handled_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="处理备注" :span="2">
          {{ currentReport.handled_note || '无' }}
        </el-descriptions-item>
      </el-descriptions>
      <el-empty v-else description="尚未处理" :image-size="60" />

      <template #footer>
        <div v-if="currentReport?.status === 'pending'">
          <el-button type="success" @click="handleResolveDetail">
            标记为已处理
          </el-button>
          <el-button type="warning" @click="handleDismissDetail">
            驳回举报
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="handleVisible" title="处理说明" width="500px">
      <el-form :model="handleForm" label-width="80px">
        <el-form-item label="处理备注">
          <el-input
            v-model="handleForm.note"
            type="textarea"
            :rows="4"
            placeholder="请输入处理备注（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleVisible = false">取消</el-button>
        <el-button :type="handleAction === 'resolve' ? 'success' : 'warning'" @click="confirmHandle">
          确认处理
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { reportApi } from '../services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const reports = ref([])
const detailVisible = ref(false)
const currentReport = ref(null)
const handleVisible = ref(false)
const pendingHandleReport = ref(null)
const handleAction = ref('resolve')

const handleForm = reactive({
  note: ''
})

const searchForm = reactive({
  status: ''
})

const pagination = reactive({
  page: 1,
  perPage: 20,
  total: 0
})

const fetchReports = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage
    }
    
    if (searchForm.status) {
      params.status = searchForm.status
    }

    const response = await reportApi.getList(params)
    if (response.data.success) {
      reports.value = response.data.reports
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('获取举报列表失败:', error)
    ElMessage.error('获取举报列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchReports()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getTargetTypeName = (type) => {
  const names = {
    post: '帖子',
    comment: '评论',
    user: '用户'
  }
  return names[type] || type
}

const getTargetTypeTagType = (type) => {
  const types = {
    post: 'primary',
    comment: 'success',
    user: 'warning'
  }
  return types[type] || 'info'
}

const getStatusTagType = (status) => {
  const types = {
    pending: 'warning',
    resolved: 'success',
    dismissed: 'info'
  }
  return types[status] || 'info'
}

const viewDetail = async (row) => {
  try {
    const response = await reportApi.getById(row.id)
    if (response.data.success) {
      currentReport.value = response.data.report
      detailVisible.value = true
    }
  } catch (error) {
    console.error('获取举报详情失败:', error)
    ElMessage.error('获取举报详情失败')
  }
}

const handleResolve = (row) => {
  pendingHandleReport.value = row
  handleAction.value = 'resolve'
  handleForm.note = ''
  handleVisible.value = true
}

const handleDismiss = (row) => {
  pendingHandleReport.value = row
  handleAction.value = 'dismiss'
  handleForm.note = ''
  handleVisible.value = true
}

const handleResolveDetail = () => {
  pendingHandleReport.value = currentReport.value
  handleAction.value = 'resolve'
  handleForm.note = ''
  detailVisible.value = false
  handleVisible.value = true
}

const handleDismissDetail = () => {
  pendingHandleReport.value = currentReport.value
  handleAction.value = 'dismiss'
  handleForm.note = ''
  detailVisible.value = false
  handleVisible.value = true
}

const confirmHandle = async () => {
  if (!pendingHandleReport.value) return

  try {
    let response
    if (handleAction.value === 'resolve') {
      response = await reportApi.resolve(pendingHandleReport.value.id, handleForm.note)
      ElMessage.success('举报已处理')
    } else {
      response = await reportApi.dismiss(pendingHandleReport.value.id, handleForm.note)
      ElMessage.success('举报已驳回')
    }
    
    handleVisible.value = false
    fetchReports()
  } catch (error) {
    console.error('处理举报失败:', error)
  }
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.reports-page {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.target-info {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.text-muted {
  color: #909399;
}
</style>
