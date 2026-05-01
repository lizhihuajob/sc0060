<template>
  <div class="announcements-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统公告</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              发布公告
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="announcements" style="width: 100%" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="250" show-overflow-tooltip>
          <template #default="scope">
            <div class="title-cell">
              <el-tag v-if="scope.row.is_pinned" type="warning" size="small" effect="dark" style="margin-right: 8px;">
                置顶
              </el-tag>
              <span>{{ scope.row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="admin" label="发布者" width="100">
          <template #default="scope">
            {{ scope.row.admin?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'" size="small">
              {{ scope.row.status_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发布时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button type="primary" text @click="viewDetail(scope.row)">
              详情
            </el-button>
            <el-button
              v-if="!scope.row.is_pinned"
              type="warning"
              text
              @click="handlePin(scope.row)"
            >
              置顶
            </el-button>
            <el-button
              v-else
              type="info"
              text
              @click="handleUnpin(scope.row)"
            >
              取消置顶
            </el-button>
            <el-button type="danger" text @click="handleDelete(scope.row)">
              删除
            </el-button>
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
          @size-change="fetchAnnouncements"
          @current-change="fetchAnnouncements"
        />
      </div>
    </el-card>

    <el-dialog v-model="formVisible" :title="isEdit ? '编辑公告' : '发布公告'" width="700px">
      <el-form :model="announcementForm" label-width="100px">
        <el-form-item label="标题" required>
          <el-input
            v-model="announcementForm.title"
            placeholder="请输入公告标题"
            maxlength="200"
          />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input
            v-model="announcementForm.content"
            type="textarea"
            :rows="10"
            placeholder="请输入公告内容"
          />
        </el-form-item>
        <el-form-item label="是否置顶">
          <el-switch
            v-model="announcementForm.is_pinned"
            :active-value="1"
            :inactive-value="0"
            active-text="置顶"
            inactive-text="不置顶"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          发布
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="公告详情" width="700px">
      <el-descriptions :column="2" border v-if="currentAnnouncement">
        <el-descriptions-item label="公告ID">{{ currentAnnouncement.id }}</el-descriptions-item>
        <el-descriptions-item label="标题" :span="1">{{ currentAnnouncement.title }}</el-descriptions-item>
        <el-descriptions-item label="发布者">
          {{ currentAnnouncement.admin?.username || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="是否置顶">
          <el-tag :type="currentAnnouncement.is_pinned ? 'warning' : 'info'" size="small">
            {{ currentAnnouncement.is_pinned ? '已置顶' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentAnnouncement.status === 'active' ? 'success' : 'info'" size="small">
            {{ currentAnnouncement.status_name }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布时间">
          {{ formatDate(currentAnnouncement.created_at) }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">公告内容</el-divider>
      <div class="announcement-content" v-if="currentAnnouncement">
        <pre>{{ currentAnnouncement.content }}</pre>
      </div>

      <template #footer>
        <div v-if="currentAnnouncement">
          <el-button
            v-if="currentAnnouncement.is_pinned"
            type="info"
            @click="handleUnpinDetail"
          >
            取消置顶
          </el-button>
          <el-button
            v-else
            type="warning"
            @click="handlePinDetail"
          >
            置顶
          </el-button>
          <el-button type="primary" @click="handleEdit">
            编辑
          </el-button>
          <el-button type="danger" @click="handleDeleteDetail">
            删除
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { announcementApi } from '../services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const announcements = ref([])
const formVisible = ref(false)
const detailVisible = ref(false)
const currentAnnouncement = ref(null)
const isEdit = ref(false)
const submitting = ref(false)

const announcementForm = reactive({
  title: '',
  content: '',
  is_pinned: 0
})

const pagination = reactive({
  page: 1,
  perPage: 20,
  total: 0
})

const fetchAnnouncements = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage
    }

    const response = await announcementApi.getList(params)
    if (response.data.success) {
      announcements.value = response.data.announcements
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('获取公告列表失败:', error)
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const resetForm = () => {
  announcementForm.title = ''
  announcementForm.content = ''
  announcementForm.is_pinned = 0
  isEdit.value = false
}

const handleCreate = () => {
  resetForm()
  formVisible.value = true
}

const viewDetail = async (row) => {
  try {
    const response = await announcementApi.getById(row.id)
    if (response.data.success) {
      currentAnnouncement.value = response.data.announcement
      detailVisible.value = true
    }
  } catch (error) {
    console.error('获取公告详情失败:', error)
    ElMessage.error('获取公告详情失败')
  }
}

const handleEdit = () => {
  if (!currentAnnouncement.value) return
  
  isEdit.value = true
  announcementForm.title = currentAnnouncement.value.title
  announcementForm.content = currentAnnouncement.value.content
  announcementForm.is_pinned = currentAnnouncement.value.is_pinned
  
  detailVisible.value = false
  formVisible.value = true
}

const handlePin = async (row) => {
  try {
    await ElMessageBox.confirm('确定要置顶该公告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await announcementApi.pin(row.id)
    if (response.data.success) {
      ElMessage.success('公告已置顶')
      fetchAnnouncements()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('置顶公告失败:', error)
    }
  }
}

const handleUnpin = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消置顶该公告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await announcementApi.unpin(row.id)
    if (response.data.success) {
      ElMessage.success('公告已取消置顶')
      fetchAnnouncements()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消置顶公告失败:', error)
    }
  }
}

const handlePinDetail = async () => {
  if (!currentAnnouncement.value) return
  
  try {
    await ElMessageBox.confirm('确定要置顶该公告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await announcementApi.pin(currentAnnouncement.value.id)
    if (response.data.success) {
      ElMessage.success('公告已置顶')
      currentAnnouncement.value.is_pinned = 1
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('置顶公告失败:', error)
    }
  }
}

const handleUnpinDetail = async () => {
  if (!currentAnnouncement.value) return
  
  try {
    await ElMessageBox.confirm('确定要取消置顶该公告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await announcementApi.unpin(currentAnnouncement.value.id)
    if (response.data.success) {
      ElMessage.success('公告已取消置顶')
      currentAnnouncement.value.is_pinned = 0
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消置顶公告失败:', error)
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该公告吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await announcementApi.delete(row.id)
    if (response.data.success) {
      ElMessage.success('公告已删除')
      fetchAnnouncements()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除公告失败:', error)
    }
  }
}

const handleDeleteDetail = async () => {
  if (!currentAnnouncement.value) return
  
  try {
    await ElMessageBox.confirm('确定要删除该公告吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await announcementApi.delete(currentAnnouncement.value.id)
    if (response.data.success) {
      ElMessage.success('公告已删除')
      detailVisible.value = false
      fetchAnnouncements()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除公告失败:', error)
    }
  }
}

const submitForm = async () => {
  if (!announcementForm.title || !announcementForm.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }

  submitting.value = true
  try {
    let response
    if (isEdit.value && currentAnnouncement.value) {
      response = await announcementApi.update(currentAnnouncement.value.id, {
        title: announcementForm.title,
        content: announcementForm.content,
        is_pinned: announcementForm.is_pinned
      })
      ElMessage.success('公告更新成功')
    } else {
      response = await announcementApi.create({
        title: announcementForm.title,
        content: announcementForm.content,
        is_pinned: announcementForm.is_pinned
      })
      ElMessage.success('公告发布成功')
    }
    
    formVisible.value = false
    fetchAnnouncements()
  } catch (error) {
    console.error('提交公告失败:', error)
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.announcements-page {
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

.title-cell {
  display: flex;
  align-items: center;
}

.announcement-content {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
}

.announcement-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: inherit;
  font-size: 14px;
}
</style>
