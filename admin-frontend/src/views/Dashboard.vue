<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1 class="page-title">仪表盘</h1>
      <p class="page-subtitle">系统运行概览</p>
    </div>
    
    <div class="stats-grid" v-loading="loading">
      <div class="stat-card">
        <div class="stat-icon primary">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <p class="stat-value">{{ stats.total_users || 0 }}</p>
          <p class="stat-label">总用户数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <p class="stat-value">{{ stats.total_posts || 0 }}</p>
          <p class="stat-label">总内容数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon warning">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <p class="stat-value">{{ stats.active_posts || 0 }}</p>
          <p class="stat-label">正常内容</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon danger">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <p class="stat-value">{{ stats.hidden_posts || 0 }}</p>
          <p class="stat-label">已下架</p>
        </div>
      </div>
    </div>
    
    <div class="content-grid">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <el-icon><User /></el-icon>
            最近注册用户
          </h3>
        </div>
        <el-table :data="recentUsers" v-loading="loading" style="width: 100%">
          <el-table-column prop="username" label="用户名" min-width="120">
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-avatar-small">{{ row.username?.charAt(0).toUpperCase() }}</div>
                <span>{{ row.username }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="level" label="会员等级" width="120">
            <template #default="{ row }">
              <span class="level-badge" :class="row.level">{{ getLevelName(row.level) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="posts_count" label="发布数" width="80">
            <template #default="{ row }">
              <span>{{ row.posts_count || 0 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间" min-width="180">
            <template #default="{ row }">
              <span>{{ formatTime(row.created_at) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <el-icon><Document /></el-icon>
            最近发布内容
          </h3>
        </div>
        <el-table :data="recentPosts" v-loading="loading" style="width: 100%">
          <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="author" label="发布者" width="120">
            <template #default="{ row }">
              <span>{{ row.author?.username }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_task" label="类型" width="80">
            <template #default="{ row }">
              <span class="type-badge" :class="row.is_task ? 'task' : 'notice'">
                {{ row.is_task ? '任务' : '公告' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <span class="status-badge" :class="row.is_hidden ? 'hidden' : 'active'">
                {{ row.is_hidden ? '已下架' : '正常' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="发布时间" min-width="160">
            <template #default="{ row }">
              <span>{{ formatTime(row.created_at) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  User, Document, CircleCheck, Warning 
} from '@element-plus/icons-vue'
import { adminApi } from '../services/api'

const loading = ref(true)
const stats = reactive({
  total_users: 0,
  total_posts: 0,
  active_posts: 0,
  hidden_posts: 0
})
const recentUsers = ref([])
const recentPosts = ref([])

const userLevels = {
  bronze: '青铜会员',
  silver: '白银会员',
  gold: '黄金会员',
  black: '黑卡会员',
  diamond: '钻石会员'
}

const getLevelName = (level) => {
  return userLevels[level] || level
}

const formatTime = (time) => {
  if (!time) return '-'
  return time.replace(' GMT', '')
}

const loadDashboard = async () => {
  loading.value = true
  try {
    const response = await adminApi.getDashboard()
    if (response.data.success) {
      const data = response.data.dashboard
      stats.total_users = data.total_users || 0
      stats.total_posts = data.total_posts || 0
      stats.active_posts = data.active_posts || 0
      stats.hidden_posts = data.hidden_posts || 0
      recentUsers.value = data.recent_users || []
      recentPosts.value = data.recent_posts || []
    }
  } catch (error) {
    ElMessage.error('加载仪表盘数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard-page {
  padding: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 12px;
}

.level-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  color: white;
}

.level-badge.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #a0522d 100%);
}

.level-badge.silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #a9a9a9 100%);
  color: #1d1d1f;
}

.level-badge.gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  color: #1d1d1f;
}

.level-badge.black {
  background: linear-gradient(135deg, #2f2f2f 0%, #1a1a1a 100%);
}

.level-badge.diamond {
  background: linear-gradient(135deg, #b9f2ff 0%, #87ceeb 100%);
  color: #1d1d1f;
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

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}
</style>
