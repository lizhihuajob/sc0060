<template>
  <div class="posts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>公告管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索标题/内容"
              clearable
              style="width: 200px; margin-right: 10px;"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="searchForm.status"
              placeholder="选择状态"
              clearable
              style="width: 120px; margin-right: 10px;"
              @change="handleSearch"
            >
              <el-option label="全部" value="" />
              <el-option label="正常" value="active" />
              <el-option label="已下架" value="hidden" />
            </el-select>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="posts" style="width: 100%" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="author" label="发布者" width="100">
          <template #default="scope">
            {{ scope.row.author?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="view_permission_name" label="查看权限" width="100">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.view_permission_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_task" label="类型" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_task ? 'success' : 'primary'" size="small">
              {{ scope.row.is_task ? '任务' : '公告' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="views_count" label="浏览量" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_hidden ? 'danger' : 'success'" size="small">
              {{ scope.row.is_hidden ? '已下架' : '正常' }}
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
            <el-button
              v-if="!scope.row.is_hidden"
              type="danger"
              text
              @click="handleHide(scope.row)"
            >
              下架
            </el-button>
            <el-button
              v-else
              type="success"
              text
              @click="handleUnhide(scope.row)"
            >
              恢复
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
          @size-change="fetchPosts"
          @current-change="fetchPosts"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailVisible" title="公告详情" width="700px">
      <el-descriptions :column="2" border v-if="currentPost">
        <el-descriptions-item label="公告ID">{{ currentPost.id }}</el-descriptions-item>
        <el-descriptions-item label="标题" :span="1">{{ currentPost.title }}</el-descriptions-item>
        <el-descriptions-item label="发布者">
          {{ currentPost.author?.username || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="currentPost.is_task ? 'success' : 'primary'" size="small">
            {{ currentPost.is_task ? '任务' : '公告' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="查看权限">
          <el-tag size="small">{{ currentPost.view_permission_name }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="浏览量">{{ currentPost.views_count }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentPost.is_hidden ? 'danger' : 'success'" size="small">
            {{ currentPost.is_hidden ? '已下架' : '正常' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="是否置顶">
          <el-tag :type="currentPost.is_pinned ? 'warning' : 'info'" size="small">
            {{ currentPost.is_pinned ? '已置顶' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布时间" :span="2">
          {{ formatDate(currentPost.created_at) }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">公告内容</el-divider>
      <div class="post-content" v-if="currentPost">
        {{ currentPost.content }}
      </div>

      <el-divider content-position="left">图片</el-divider>
      <div class="post-images" v-if="currentPost?.images?.length">
        <el-image
          v-for="(img, index) in currentPost.images"
          :key="index"
          :src="img"
          :preview-src-list="currentPost.images"
          fit="cover"
          style="width: 100px; height: 100px; margin-right: 10px;"
        />
      </div>
      <el-empty v-else description="无图片" />

      <template #footer>
        <div v-if="currentPost">
          <el-button
            v-if="!currentPost.is_pinned"
            type="warning"
            @click="handlePinDetail"
          >
            置顶公告
          </el-button>
          <el-button
            v-else
            type="info"
            @click="handleUnpinDetail"
          >
            取消置顶
          </el-button>
          <el-button
            v-if="!currentPost.is_hidden"
            type="danger"
            @click="handleHideDetail"
          >
            下架公告
          </el-button>
          <el-button
            v-else
            type="success"
            @click="handleUnhideDetail"
          >
            恢复公告
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="pinVisible" title="置顶设置" width="400px">
      <el-form :model="pinForm" label-width="100px">
        <el-form-item label="置顶天数">
          <el-input-number
            v-model="pinForm.duration_days"
            :min="1"
            :max="365"
            :step="1"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pinVisible = false">取消</el-button>
        <el-button type="warning" @click="confirmPin">确认置顶</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="hideReasonVisible" title="下架原因" width="500px">
      <el-form :model="hideForm" label-width="80px">
        <el-form-item label="下架原因">
          <el-input
            v-model="hideForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入下架原因（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="hideReasonVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmHide">确认下架</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { postApi } from '../services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const posts = ref([])
const detailVisible = ref(false)
const currentPost = ref(null)
const hideReasonVisible = ref(false)
const pendingHidePost = ref(null)
const pinVisible = ref(false)
const pendingPinPost = ref(null)

const hideForm = reactive({
  reason: ''
})

const pinForm = reactive({
  duration_days: 30
})

const searchForm = reactive({
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  perPage: 20,
  total: 0
})

const fetchPosts = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage
    }
    
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }

    const response = await postApi.getList(params)
    if (response.data.success) {
      posts.value = response.data.posts
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('获取公告列表失败:', error)
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchPosts()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const viewDetail = async (row) => {
  try {
    const response = await postApi.getById(row.id)
    if (response.data.success) {
      currentPost.value = response.data.post
      detailVisible.value = true
    }
  } catch (error) {
    console.error('获取公告详情失败:', error)
    ElMessage.error('获取公告详情失败')
  }
}

const handleHide = (row) => {
  pendingHidePost.value = row
  hideForm.reason = ''
  hideReasonVisible.value = true
}

const handleUnhide = async (row) => {
  try {
    await ElMessageBox.confirm('确定要恢复该公告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await postApi.unhide(row.id)
    if (response.data.success) {
      ElMessage.success('公告已恢复')
      fetchPosts()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('恢复公告失败:', error)
    }
  }
}

const confirmHide = async () => {
  if (!pendingHidePost.value) return

  try {
    const response = await postApi.hide(pendingHidePost.value.id, hideForm.reason)
    if (response.data.success) {
      ElMessage.success('公告已下架')
      hideReasonVisible.value = false
      fetchPosts()
    }
  } catch (error) {
    console.error('下架公告失败:', error)
  }
}

const handleHideDetail = () => {
  pendingHidePost.value = currentPost.value
  hideForm.reason = ''
  detailVisible.value = false
  hideReasonVisible.value = true
}

const handleUnhideDetail = async () => {
  if (!currentPost.value) return

  try {
    await ElMessageBox.confirm('确定要恢复该公告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await postApi.unhide(currentPost.value.id)
    if (response.data.success) {
      ElMessage.success('公告已恢复')
      detailVisible.value = false
      fetchPosts()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('恢复公告失败:', error)
    }
  }
}

const handlePin = (row) => {
  pendingPinPost.value = row
  pinForm.duration_days = 30
  pinVisible.value = true
}

const handleUnpin = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消置顶该公告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await postApi.unpin(row.id)
    if (response.data.success) {
      ElMessage.success('公告已取消置顶')
      fetchPosts()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消置顶公告失败:', error)
    }
  }
}

const confirmPin = async () => {
  if (!pendingPinPost.value) return

  try {
    const response = await postApi.pin(pendingPinPost.value.id, pinForm.duration_days)
    if (response.data.success) {
      ElMessage.success(`公告已置顶，有效期${pinForm.duration_days}天`)
      pinVisible.value = false
      fetchPosts()
    }
  } catch (error) {
    console.error('置顶公告失败:', error)
  }
}

const handlePinDetail = () => {
  if (!currentPost.value) return
  pendingPinPost.value = currentPost.value
  pinForm.duration_days = 30
  detailVisible.value = false
  pinVisible.value = true
}

const handleUnpinDetail = async () => {
  if (!currentPost.value) return
  
  try {
    await ElMessageBox.confirm('确定要取消置顶该公告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await postApi.unpin(currentPost.value.id)
    if (response.data.success) {
      ElMessage.success('公告已取消置顶')
      currentPost.value.is_pinned = 0
      fetchPosts()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消置顶公告失败:', error)
    }
  }
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.posts-page {
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

.post-content {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
}

.post-images {
  display: flex;
  flex-wrap: wrap;
}
</style>
