<template>
  <div class="dashboard-page">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">仪表盘</h1>
        <p class="page-subtitle">系统运行概览</p>
      </div>
      <div class="header-right">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="onDateRangeChange"
          style="width: 280px"
        />
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="stats-grid" v-loading="loading">
      <div class="stat-card">
        <div class="stat-icon primary">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <p class="stat-value">{{ formatNumber(stats.total_users || 0) }}</p>
          <p class="stat-label">总用户数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <p class="stat-value">{{ formatNumber(stats.total_posts || 0) }}</p>
          <p class="stat-label">总内容数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon info">
          <el-icon><View /></el-icon>
        </div>
        <div class="stat-info">
          <p class="stat-value">{{ formatNumber(stats.total_views || 0) }}</p>
          <p class="stat-label">总浏览量</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon warning">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="stat-info">
          <p class="stat-value">{{ formatNumber(stats.total_comments || 0) }}</p>
          <p class="stat-label">总留言数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <p class="stat-value">{{ formatNumber(stats.active_posts || 0) }}</p>
          <p class="stat-label">正常内容</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon danger">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <p class="stat-value">{{ formatNumber(stats.hidden_posts || 0) }}</p>
          <p class="stat-label">已下架</p>
        </div>
      </div>
    </div>
    
    <div class="charts-section">
      <div class="charts-grid">
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <el-icon><TrendCharts /></el-icon>
              内容发布趋势
            </h3>
          </div>
          <div class="chart-container">
            <v-chart class="chart" :option="postsChartOption" autoresize />
          </div>
        </div>
        
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <el-icon><User /></el-icon>
              用户注册趋势
            </h3>
          </div>
          <div class="chart-container">
            <v-chart class="chart" :option="registrationChartOption" autoresize />
          </div>
        </div>
        
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <el-icon><ChatDotRound /></el-icon>
              留言趋势
            </h3>
          </div>
          <div class="chart-container">
            <v-chart class="chart" :option="commentsChartOption" autoresize />
          </div>
        </div>
        
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <el-icon><Megaphone /></el-icon>
              公告发布趋势
            </h3>
          </div>
          <div class="chart-container">
            <v-chart class="chart" :option="announcementsChartOption" autoresize />
          </div>
        </div>
      </div>
    </div>
    
    <div class="content-grid">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <el-icon><Trophy /></el-icon>
            最受欢迎的帖子排行
          </h3>
        </div>
        <el-table :data="popularPosts" v-loading="loading" style="width: 100%">
          <el-table-column label="排名" width="80" align="center">
            <template #default="{ $index }">
              <span class="rank-badge" :class="'rank-' + ($index + 1)">
                {{ $index + 1 }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="250" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="post-title-link" @click="goToPostDetail(row.id)">
                {{ row.title }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="author" label="发布者" width="120">
            <template #default="{ row }">
              <span>{{ row.author?.username }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="views_count" label="浏览量" width="100" align="center">
            <template #default="{ row }">
              <span class="views-count">{{ formatNumber(row.views_count) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_task" label="类型" width="80">
            <template #default="{ row }">
              <span class="type-badge" :class="row.is_task ? 'task' : 'notice'">
                {{ row.is_task ? '任务' : '公告' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="tags" label="标签" min-width="150">
            <template #default="{ row }">
              <div class="tags-container">
                <el-tag 
                  v-for="tag in row.tags" 
                  :key="tag.id" 
                  size="small"
                  :style="{ backgroundColor: tag.color + '20', color: tag.color, borderColor: tag.color + '40' }"
                >
                  {{ tag.name }}
                </el-tag>
                <span v-if="!row.tags || row.tags.length === 0" class="no-tags">-</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="发布时间" width="160">
            <template #default="{ row }">
              <span>{{ formatTime(row.created_at) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, Document, CircleCheck, Warning, View, ChatDotRound, 
  Refresh, TrendCharts, Trophy, Megaphone
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import VChart from 'vue-echarts'
import { adminApi } from '../services/api'

const router = useRouter()
const loading = ref(true)
const dateRange = ref([])

const stats = reactive({
  total_users: 0,
  total_posts: 0,
  active_posts: 0,
  hidden_posts: 0,
  total_views: 0,
  total_comments: 0
})

const recentUsers = ref([])
const recentPosts = ref([])
const popularPosts = ref([])
const trendsData = ref({
  registration: [],
  posts: [],
  comments: [],
  announcements: []
})

const userLevels = {
  bronze: '青铜会员',
  silver: '白银会员',
  gold: '黄金会员',
  black: '黑卡会员',
  diamond: '钻石会员'
}

const defaultChartColors = {
  posts: '#409EFF',
  registration: '#67C23A',
  comments: '#E6A23C',
  announcements: '#909399'
}

const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num?.toLocaleString() || '0'
}

const getLevelName = (level) => {
  return userLevels[level] || level
}

const formatTime = (time) => {
  if (!time) return '-'
  return time.replace(' GMT', '')
}

const goToPostDetail = (postId) => {
  router.push(`/posts/${postId}`)
}

const generateChartOption = (data, title, color) => {
  const dates = data.map(item => item.date)
  const values = data.map(item => item.count)
  
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: {
        color: '#303133'
      },
      formatter: (params) => {
        const date = params[0].axisValue
        const value = params[0].value
        return `<div style="font-weight: 600; margin-bottom: 4px;">${date}</div>
                <div style="display: flex; align-items: center;">
                  <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: ${color}; margin-right: 8px;"></span>
                  <span>${title}: ${value}</span>
                </div>`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: {
        lineStyle: {
          color: '#e4e7ed'
        }
      },
      axisLabel: {
        color: '#909399',
        fontSize: 11,
        interval: Math.floor(dates.length / 5)
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: '#f5f7fa',
          type: 'dashed'
        }
      },
      axisLabel: {
        color: '#909399',
        fontSize: 11
      }
    },
    series: [
      {
        name: title,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        data: values,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: color + '30' },
            { offset: 1, color: color + '05' }
          ])
        },
        lineStyle: {
          color: color,
          width: 2
        },
        itemStyle: {
          color: color,
          borderWidth: 2,
          borderColor: '#fff'
        },
        emphasis: {
          itemStyle: {
            scale: 1.2
          }
        }
      }
    ]
  }
}

const postsChartOption = computed(() => {
  return generateChartOption(
    trendsData.value.posts, 
    '内容发布数', 
    defaultChartColors.posts
  )
})

const registrationChartOption = computed(() => {
  return generateChartOption(
    trendsData.value.registration, 
    '注册用户数', 
    defaultChartColors.registration
  )
})

const commentsChartOption = computed(() => {
  return generateChartOption(
    trendsData.value.comments, 
    '留言数', 
    defaultChartColors.comments
  )
})

const announcementsChartOption = computed(() => {
  return generateChartOption(
    trendsData.value.announcements, 
    '公告发布数', 
    defaultChartColors.announcements
  )
})

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
      stats.total_views = data.total_views || 0
      stats.total_comments = data.total_comments || 0
      recentUsers.value = data.recent_users || []
      recentPosts.value = data.recent_posts || []
      popularPosts.value = data.popular_posts || []
    }
  } catch (error) {
    ElMessage.error('加载仪表盘数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadTrendsData = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await adminApi.getTrendsStats(params)
    if (response.data.success) {
      const data = response.data.trends
      trendsData.value.registration = data.registration || []
      trendsData.value.posts = data.posts || []
      trendsData.value.comments = data.comments || []
      trendsData.value.announcements = data.announcements || []
    }
  } catch (error) {
    ElMessage.error('加载趋势数据失败')
    console.error(error)
  }
}

const onDateRangeChange = () => {
  loadTrendsData()
}

const refreshData = () => {
  loadDashboard()
  loadTrendsData()
}

onMounted(() => {
  loadDashboard()
  loadTrendsData()
})
</script>

<style scoped>
.dashboard-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.primary {
  background: linear-gradient(135deg, #409EFF 0%, #1890FF 100%);
  color: white;
}

.stat-icon.success {
  background: linear-gradient(135deg, #67C23A 0%, #52C41A 100%);
  color: white;
}

.stat-icon.info {
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  color: white;
}

.stat-icon.warning {
  background: linear-gradient(135deg, #E6A23C 0%, #FA8C16 100%);
  color: white;
}

.stat-icon.danger {
  background: linear-gradient(135deg, #F56C6C 0%, #FF4D4F 100%);
  color: white;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
}

.charts-section {
  margin-bottom: 24px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  padding: 20px;
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
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}

.chart-container {
  height: 280px;
}

.chart {
  width: 100%;
  height: 100%;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.card {
  background: var(--color-bg-card);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  padding: 20px;
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

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 700;
  background: #f5f7fa;
  color: #909399;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #a9a9a9 100%);
  color: #fff;
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #a0522d 100%);
  color: #fff;
}

.post-title-link {
  color: var(--color-primary);
  cursor: pointer;
  transition: color 0.2s;
}

.post-title-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.views-count {
  font-weight: 600;
  color: var(--color-primary);
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.no-tags {
  color: #c0c4cc;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-value {
    font-size: 22px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
