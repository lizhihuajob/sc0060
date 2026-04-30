<template>
  <div class="dashboard">
    <el-card class="welcome-card">
      <div class="welcome-content">
        <el-icon size="48" class="welcome-icon"><TrendCharts /></el-icon>
        <div>
          <h2>欢迎回来，{{ adminStore.username }}！</h2>
          <p>这是公告平台后台管理系统</p>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" class="stat-icon user-icon"><UserFilled /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ dashboard.total_users }}</div>
              <div class="stat-label">注册用户总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" class="stat-icon post-icon"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ dashboard.total_posts }}</div>
              <div class="stat-label">公告总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" class="stat-icon active-icon"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ dashboard.active_posts }}</div>
              <div class="stat-label">正常公告</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" class="stat-icon money-icon"><Wallet /></el-icon>
            <div class="stat-info">
              <div class="stat-value">¥{{ dashboard.total_recharge || 0 }}</div>
              <div class="stat-label">总充值金额</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>用户等级分布</span>
            </div>
          </template>
          <div class="level-stats">
            <div
              v-for="(data, level) in dashboard.level_distribution"
              :key="level"
              class="level-item"
            >
              <div class="level-info">
                <span class="level-name">{{ data.name }}</span>
                <span class="level-count">{{ data.count }} 人</span>
              </div>
              <el-progress
                :percentage="calculatePercentage(data.count, dashboard.total_users)"
                :stroke-width="18"
              />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>公告状态统计</span>
            </div>
          </template>
          <div class="post-stats">
            <div class="post-stat-item">
              <el-icon size="24" class="success-icon"><CircleCheck /></el-icon>
              <div>
                <div class="post-stat-value">{{ dashboard.active_posts }}</div>
                <div class="post-stat-label">正常公告</div>
              </div>
            </div>
            <div class="post-stat-item">
              <el-icon size="24" class="warning-icon"><Warning /></el-icon>
              <div>
                <div class="post-stat-value">{{ dashboard.hidden_posts }}</div>
                <div class="post-stat-label">已下架公告</div>
              </div>
            </div>
            <div class="post-stat-item">
              <el-icon size="24" class="info-icon"><Document /></el-icon>
              <div>
                <div class="post-stat-value">{{ dashboard.total_posts }}</div>
                <div class="post-stat-label">公告总数</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../stores/adminStore'
import { dashboardApi } from '../services/api'
import { ElMessage } from 'element-plus'

const adminStore = useAdminStore()

const dashboard = ref({
  total_users: 0,
  total_posts: 0,
  active_posts: 0,
  hidden_posts: 0,
  total_recharge: 0,
  level_distribution: {}
})

const loading = ref(false)

const fetchDashboard = async () => {
  loading.value = true
  try {
    const response = await dashboardApi.getDashboard()
    if (response.data.success) {
      dashboard.value = response.data.dashboard
    }
  } catch (error) {
    console.error('获取仪表板数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const calculatePercentage = (count, total) => {
  if (!total) return 0
  return Math.round((count / total) * 100)
}

onMounted(() => {
  fetchDashboard()
})
</script>

<style scoped>
.dashboard {
  padding: 10px;
}

.welcome-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.welcome-content {
  display: flex;
  align-items: center;
  gap: 20px;
  color: #fff;
}

.welcome-icon {
  opacity: 0.9;
}

.welcome-content h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
}

.welcome-content p {
  margin: 0;
  opacity: 0.9;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  padding: 15px;
  border-radius: 12px;
}

.user-icon {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.post-icon {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.active-icon {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.money-icon {
  background: rgba(230, 162, 60, 0.1);
  color: #E6A23C;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.section-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.level-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.level-item {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.level-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.level-name {
  font-weight: bold;
  color: #303133;
}

.level-count {
  color: #909399;
  font-size: 14px;
}

.post-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.post-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.success-icon {
  color: #67C23A;
}

.warning-icon {
  color: #F56C6C;
}

.info-icon {
  color: #409EFF;
}

.post-stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.post-stat-label {
  font-size: 14px;
  color: #909399;
}
</style>
