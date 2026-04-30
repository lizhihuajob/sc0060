<template>
  <div class="posts-page">
    <div class="page-header">
      <h1 class="page-title">内容管理</h1>
      <p class="page-subtitle">管理用户发布的公告和任务</p>
    </div>
    
    <div class="card">
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索标题或内容"
          prefix-icon="Search"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
          style="width: 200px;"
        />
        <el-select
          v-model="filterStatus"
          placeholder="状态筛选"
          clearable
          @change="handleSearch"
          style="width: 150px;"
        >
          <el-option label="正常" value="active" />
          <el-option label="已下架" value="hidden" />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetSearch">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
      
      <el-table
        :data="posts"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="author" label="发布者" width="120">
          <template #default="{ row }">
            <span>{{ row.author?.username || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_task" label="类型" width="80">
          <template #default="{ row }">
            <span class="type-badge" :class="row.is_task ? 'task' : 'notice'">
              {{ row.is_task ? '任务' : '公告' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="views_count" label="浏览量" width="80" align="center">
          <template #default="{ row }">
            <span>{{ row.views_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="row.is_hidden ? 'hidden' : 'active'">
              {{ row.is_hidden ? '已下架' : '正常' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发布时间" width="180">
          <template #default="{ row }">
            <span>{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button 
                v-if="!row.is_hidden"
                type="warning" 
                link 
                size="small"
                @click="handleHide(row)"
              >
                下架
              </el-button>
              <el-button 
                v-else
                type="success" 
                link 
                size="small"
                @click="handleUnhide(row)"
              >
                恢复
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
    
    <el-dialog
      v-model="hideDialogVisible"
      title="下架内容"
      width="400px"
    >
      <el-form label-width="80px">
        <el-form-item label="下架原因">
          <el-input
            v-model="hideReason"
            type="textarea"
            :rows="3"
            placeholder="请输入下架原因（可选）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="hideDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="processing" @click="confirmHide">
            确认下架
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { adminApi } from '../services/api'

const loading = ref(false)
const processing = ref(false)
const posts = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const filterStatus = ref('')
const hideDialogVisible = ref(false)
const currentPost = ref(null)
const hideReason = ref('')

const formatTime = (time) => {
  if (!time) return '-'
  return time.replace(' GMT', '')
}

const loadPosts = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }
    
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    
    const response = await adminApi.getPosts(params)
    if (response.data.success) {
      posts.value = response.data.posts || []
      total.value = response.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载内容列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadPosts()
}

const resetSearch = () => {
  searchKeyword.value = ''
  filterStatus.value = ''
  currentPage.value = 1
  loadPosts()
}

const handlePageChange = () => {
  loadPosts()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadPosts()
}

const handleHide = (row) => {
  currentPost.value = row
  hideReason.value = ''
  hideDialogVisible.value = true
}

const confirmHide = async () => {
  if (!currentPost.value) return
  
  processing.value = true
  try {
    const response = await adminApi.hidePost(currentPost.value.id, {
      reason: hideReason.value.trim() || null
    })
    if (response.data.success) {
      ElMessage.success('已下架')
      hideDialogVisible.value = false
      loadPosts()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    processing.value = false
  }
}

const handleUnhide = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要恢复内容「${row.title}」吗？`,
      '确认恢复',
      {
        confirmButtonText: '确定恢复',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    const response = await adminApi.unhidePost(row.id)
    if (response.data.success) {
      ElMessage.success('已恢复')
      loadPosts()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '操作失败')
    }
  }
}

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.posts-page {
  padding: 0;
}

.type-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
}

.type-badge.notice {
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
}

.type-badge.task {
  background: rgba(255, 149, 0, 0.1);
  color: var(--color-warning);
}

.status-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
}

.status-badge.active {
  background: rgba(103, 194, 58, 0.1);
  color: var(--color-success);
}

.status-badge.hidden {
  background: rgba(255, 59, 48, 0.1);
  color: var(--color-danger);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
