<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="gradient-text">发现精彩</span>，连接每一刻
          </h1>
          <p class="hero-subtitle">
            发布公告、分享任务，让信息触达更多人
          </p>
          <div class="hero-actions" v-if="!user">
            <router-link to="/register" class="btn-primary hero-btn">
              立即加入
            </router-link>
            <router-link to="/login" class="btn-secondary hero-btn">
              登录账号
            </router-link>
          </div>
          <router-link to="/new-post" class="btn-primary hero-btn" v-else>
            <el-icon><Edit /></el-icon>
            发布信息
          </router-link>
        </div>
        <div class="hero-visual">
          <div class="floating-card card-glass" style="--delay: 0s; --x: -20px; --y: -30px">
            <div class="card-icon announcement">📢</div>
            <div class="card-text">公告通知</div>
          </div>
          <div class="floating-card card-glass" style="--delay: 0.5s; --x: 30px; --y: -10px">
            <div class="card-icon task">🎯</div>
            <div class="card-text">任务招募</div>
          </div>
          <div class="floating-card card-glass" style="--delay: 1s; --x: -10px; --y: 20px">
            <div class="card-icon trade">💼</div>
            <div class="card-text">交易信息</div>
          </div>
        </div>
      </div>
    </section>

    <section class="pinned-section" v-if="pinnedPosts.length > 0">
      <div class="section-header">
        <div class="section-title-wrapper">
          <div class="section-icon pinned-icon">
            <el-icon><Star /></el-icon>
          </div>
          <h2 class="section-title gradient-text-warm">置顶推荐</h2>
        </div>
        <div class="section-badge badge badge-warning">
          <el-icon><Coin /></el-icon>
          付费置顶
        </div>
      </div>
      <div class="pinned-grid">
        <TransitionGroup name="slide-up" tag="div" class="pinned-grid">
          <div 
            v-for="(post, index) in pinnedPosts" 
            :key="post.id" 
            class="pinned-card card card-glass"
            :style="{ '--index': index }"
            @click="goToPost(post.id)"
          >
            <div class="pinned-badge">
              <el-icon><Fire /></el-icon>
              置顶
            </div>
            <div class="pinned-header">
              <span class="category-badge" :class="post.category">
                {{ post.category_name }}
              </span>
              <div class="post-author-mini">
                <span class="author-dot"></span>
                <span class="author-name-mini">{{ post.author?.username }}</span>
              </div>
            </div>
            <h3 class="pinned-title">{{ post.title }}</h3>
            <p class="pinned-excerpt">{{ truncate(post.content, 80) }}</p>
            <div class="pinned-footer">
              <span class="post-time-mini">{{ formatTime(post.created_at) }}</span>
              <div class="post-stats-mini">
                <span class="stat-item">
                  <el-icon><View /></el-icon>
                  {{ post.views_count }}
                </span>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </section>

    <section class="main-content-section">
      <div class="content-layout">
        <aside class="sidebar-left">
          <div class="sidebar-card card card-glass">
            <div class="sidebar-header">
              <el-icon><Grid /></el-icon>
              <span>分类浏览</span>
            </div>
            <div class="category-list">
              <button 
                class="category-item"
                :class="{ active: selectedCategory === 'all' }"
                @click="selectCategory('all')"
              >
                <span class="category-icon all">📋</span>
                <span class="category-name">全部信息</span>
              </button>
              <button 
                v-for="(label, key) in categories" 
                :key="key"
                class="category-item"
                :class="{ active: selectedCategory === key }"
                @click="selectCategory(key)"
              >
                <span class="category-icon" :class="key">{{ getCategoryIcon(key) }}</span>
                <span class="category-name">{{ label }}</span>
              </button>
            </div>
          </div>

          <div class="sidebar-card card card-glass mt-4">
            <div class="sidebar-header">
              <el-icon><TrendCharts /></el-icon>
              <span>快捷入口</span>
            </div>
            <div class="quick-actions">
              <router-link to="/new-post" class="quick-action primary">
                <el-icon><Edit /></el-icon>
                <span>发布信息</span>
              </router-link>
              <router-link to="/my-posts" class="quick-action" v-if="user">
                <el-icon><Document /></el-icon>
                <span>我的发布</span>
              </router-link>
              <router-link to="/upgrade" class="quick-action">
                <el-icon><Star /></el-icon>
                <span>升级会员</span>
              </router-link>
            </div>
          </div>
        </aside>

        <main class="main-feed">
          <div class="feed-header card card-glass">
            <div class="search-bar-wrapper">
              <div class="search-box">
                <el-icon><Search /></el-icon>
                <input 
                  type="text" 
                  v-model="searchKeyword" 
                  @keyup.enter="doSearch"
                  placeholder="搜索标题或内容..."
                  class="search-input"
                />
                <button class="search-btn" @click="doSearch">
                  <el-icon><Search /></el-icon>
                </button>
              </div>
            </div>
            <div class="filter-toolbar">
              <div class="type-filter">
                <button 
                  v-for="type in typeOptions" 
                  :key="type.value"
                  class="filter-pill"
                  :class="{ active: postType === type.value }"
                  @click="selectType(type.value)"
                >
                  {{ type.label }}
                </button>
              </div>
              <div class="sort-filter">
                <span class="sort-label">排序：</span>
                <button 
                  v-for="sort in sortOptions" 
                  :key="sort.value"
                  class="sort-btn"
                  :class="{ active: sortBy === sort.value }"
                  @click="selectSort(sort.value)"
                >
                  <el-icon v-if="sort.icon"><component :is="sort.icon" /></el-icon>
                  {{ sort.label }}
                </button>
              </div>
            </div>
          </div>

          <div class="posts-feed" v-if="posts.length > 0">
            <TransitionGroup name="slide-up" tag="div">
              <article 
                v-for="post in posts" 
                :key="post.id" 
                class="post-item card"
                @click="goToPost(post.id)"
              >
                <div class="post-main">
                  <div class="post-meta">
                    <span class="category-badge" :class="post.category">
                      {{ getCategoryIcon(post.category) }}
                      {{ post.category_name }}
                    </span>
                    <span class="type-badge" :class="post.is_task ? 'task' : 'notice'">
                      {{ post.is_task ? '任务' : '公告' }}
                    </span>
                    <div class="post-author-info">
                      <span class="level-badge-mini" :class="post.author?.level">
                        {{ post.author?.level_name }}
                      </span>
                      <span class="author-name">{{ post.author?.username }}</span>
                    </div>
                    <span class="post-time">{{ formatTime(post.created_at) }}</span>
                  </div>
                  <h3 class="post-title">{{ post.title }}</h3>
                  <p class="post-excerpt">{{ truncate(post.content, 150) }}</p>
                  <div class="post-images" v-if="post.images?.length > 0">
                    <div class="image-grid">
                      <img 
                        v-for="(img, index) in post.images.slice(0, 3)" 
                        :key="index"
                        :src="`/uploads/${img}`"
                        class="post-image"
                        alt="图片"
                      />
                    </div>
                  </div>
                  <div class="post-footer">
                    <div class="post-stats">
                      <span class="stat-item">
                        <el-icon><View /></el-icon>
                        <span>{{ post.views_count }} 浏览</span>
                      </span>
                      <span class="permission-info">
                        <el-icon><Lock /></el-icon>
                        <span>{{ post.view_permission_name }}</span>
                      </span>
                    </div>
                    <router-link 
                      :to="`/post/${post.id}`" 
                      class="read-more"
                      @click.stop
                    >
                      阅读全文
                      <el-icon><ArrowRight /></el-icon>
                    </router-link>
                  </div>
                </div>
              </article>
            </TransitionGroup>
          </div>

          <div class="empty-state card card-glass" v-else-if="!loading">
            <div class="empty-icon-wrapper">
              <div class="empty-icon">📭</div>
            </div>
            <h3 class="empty-title">暂无内容</h3>
            <p class="empty-desc">
              {{ searchKeyword ? '没有找到匹配的内容，换个关键词试试' : '该分类下还没有任何内容' }}
            </p>
            <router-link to="/new-post" class="btn-primary" v-if="user">
              发布第一条
            </router-link>
          </div>

          <div class="loading-state" v-else>
            <div class="loading-spinner">
              <el-icon class="loading-icon"><Loading /></el-icon>
            </div>
            <p>加载中...</p>
          </div>

          <div class="load-more-wrapper" v-if="hasMore && !loading">
            <button class="load-more-btn btn-secondary" @click="loadMore" :disabled="loading">
              <span v-if="!loading">加载更多</span>
              <span v-else>加载中...</span>
            </button>
          </div>
        </main>

        <aside class="sidebar-right">
          <div class="sidebar-card card card-glass">
            <div class="sidebar-header">
              <el-icon><TrendCharts /></el-icon>
              <span>热门排行</span>
            </div>
            <div class="hot-list">
              <div 
                v-for="(post, index) in hotPosts.slice(0, 5)" 
                :key="post.id" 
                class="hot-item"
                @click="goToPost(post.id)"
              >
                <span class="hot-rank" :class="{ 'top-three': index < 3 }">
                  {{ index + 1 }}
                </span>
                <div class="hot-content">
                  <p class="hot-title">{{ truncate(post.title, 20) }}</p>
                  <span class="hot-views">
                    <el-icon><View /></el-icon>
                    {{ post.views_count }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="sidebar-card card card-glass mt-4" v-if="user">
            <div class="sidebar-header">
              <el-icon><User /></el-icon>
              <span>我的账户</span>
            </div>
            <div class="user-summary">
              <div class="user-info-mini">
                <span class="level-badge" :class="user.level">{{ user.level_name }}</span>
                <span class="username">{{ user.username }}</span>
              </div>
              <div class="user-stats">
                <div class="stat-box">
                  <div class="stat-value">{{ user.balance | toFixed(2) }}</div>
                  <div class="stat-label">余额(元)</div>
                </div>
                <div class="stat-box">
                  <div class="stat-value">{{ user.posts_count }}/{{ user.posts_limit }}</div>
                  <div class="stat-label">发布数</div>
                </div>
              </div>
              <div class="user-actions">
                <router-link to="/recharge" class="mini-btn primary">
                  充值
                </router-link>
                <router-link to="/upgrade" class="mini-btn">
                  升级
                </router-link>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Document, Clock, View, Loading, Search, Fire, Star, 
  Grid, Edit, TrendCharts, User, Coin, ArrowRight, Lock
} from '@element-plus/icons-vue'
import { postApi, configApi } from '../services/api'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const { user } = useUserStore()

const posts = ref([])
const pinnedPosts = ref([])
const hotPosts = ref([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

const searchKeyword = ref('')
const postType = ref('all')
const sortBy = ref('latest')
const selectedCategory = ref('all')
const categories = ref({})
const pinnedConfig = ref({ price: 10, duration_days: 7, max_count: 3 })

const typeOptions = [
  { value: 'all', label: '全部类型' },
  { value: 'notice', label: '公告' },
  { value: 'task', label: '任务' }
]

const sortOptions = [
  { value: 'latest', label: '最新', icon: Clock },
  { value: 'hot', label: '热门', icon: Fire }
]

const getCategoryIcon = (category) => {
  const icons = {
    notice: '📢',
    activity: '🎉',
    task: '🎯',
    job: '💼',
    trade: '💰',
    other: '📋'
  }
  return icons[category] || '📋'
}

const fetchConfig = async () => {
  try {
    const response = await configApi.getMembership()
    if (response.data.success) {
      categories.value = response.data.categories || {}
      pinnedConfig.value = response.data.pinned_config || pinnedConfig.value
    }
  } catch (error) {
    console.error('获取配置失败:', error)
  }
}

const loadPinnedPosts = async () => {
  try {
    const response = await postApi.getList({ is_pinned: 1 })
    if (response.config?.url?.includes('pinned')) {
      if (response.data.success) {
        pinnedPosts.value = response.data.posts
      }
    } else {
      const pinnedResponse = await fetch('/api/posts/pinned', { credentials: 'include' })
      const pinnedData = await pinnedResponse.json()
      if (pinnedData.success) {
        pinnedPosts.value = pinnedData.posts
      }
    }
  } catch (error) {
    try {
      const pinnedResponse = await fetch('/api/posts/pinned', { credentials: 'include' })
      const pinnedData = await pinnedResponse.json()
      if (pinnedData.success) {
        pinnedPosts.value = pinnedData.posts
      }
    } catch (e) {
      console.error('获取置顶帖子失败:', e)
    }
  }
}

const loadHotPosts = async () => {
  try {
    const response = await postApi.getList({ sort: 'hot', per_page: 5, category: selectedCategory.value })
    if (response.data.success) {
      hotPosts.value = response.data.posts
    }
  } catch (error) {
    console.error('获取热门帖子失败:', error)
  }
}

const loadPosts = async (append = false) => {
  if (loading.value) return
  loading.value = true
  
  try {
    const params = {
      page: page.value,
      per_page: 10
    }
    
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    if (postType.value !== 'all') {
      params.type = postType.value
    }
    if (sortBy.value !== 'latest') {
      params.sort = sortBy.value
    }
    if (selectedCategory.value !== 'all') {
      params.category = selectedCategory.value
    }
    
    const response = await postApi.getList(params)
    
    if (response.data.success) {
      const newPosts = response.data.posts
      if (append) {
        posts.value = [...posts.value, ...newPosts]
      } else {
        posts.value = newPosts
      }
      hasMore.value = response.data.has_more
    }
  } catch (error) {
    console.error('加载帖子失败:', error)
  } finally {
    loading.value = false
  }
}

const doSearch = () => {
  page.value = 1
  posts.value = []
  loadPosts(false)
  loadHotPosts()
}

const selectType = (type) => {
  postType.value = type
  page.value = 1
  posts.value = []
  loadPosts(false)
}

const selectSort = (sort) => {
  sortBy.value = sort
  page.value = 1
  posts.value = []
  loadPosts(false)
}

const selectCategory = (category) => {
  selectedCategory.value = category
  page.value = 1
  posts.value = []
  loadPosts(false)
  loadHotPosts()
}

const loadMore = () => {
  page.value++
  loadPosts(true)
}

const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}

const truncate = (text, length) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.slice(0, length) + '...'
}

const formatTime = (time) => {
  if (!time) return ''
  return time.replace(' GMT', '')
}

onMounted(() => {
  fetchConfig()
  loadPinnedPosts()
  loadPosts()
  loadHotPosts()
})
</script>

<style scoped>
.home-page {
  flex: 1;
  min-height: 100vh;
}

.hero-section {
  padding: 60px 0;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(0, 113, 227, 0.03) 0%, transparent 100%);
  pointer-events: none;
}

.hero-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 40px;
}

.hero-text {
  flex: 1;
  max-width: 50%;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin: 0 0 16px;
  color: var(--color-text);
}

.hero-subtitle {
  font-size: 21px;
  line-height: 1.5;
  color: var(--color-text-secondary);
  margin: 0 0 32px;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  font-size: 17px;
}

.hero-visual {
  flex: 1;
  max-width: 45%;
  height: 300px;
  position: relative;
}

.floating-card {
  position: absolute;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  animation: float 3s ease-in-out infinite;
  animation-delay: var(--delay);
  transform: translate(var(--x), var(--y));
}

@keyframes float {
  0%, 100% { transform: translate(var(--x), var(--y)) translateY(0); }
  50% { transform: translate(var(--x), var(--y)) translateY(-10px); }
}

.card-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
}

.card-icon.announcement {
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.15) 0%, rgba(0, 113, 227, 0.05) 100%);
}

.card-icon.task {
  background: linear-gradient(135deg, rgba(255, 149, 0, 0.15) 0%, rgba(255, 149, 0, 0.05) 100%);
}

.card-icon.trade {
  background: linear-gradient(135deg, rgba(52, 199, 89, 0.15) 0%, rgba(52, 199, 89, 0.05) 100%);
}

.card-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.pinned-section {
  padding: 40px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  font-size: 20px;
}

.pinned-icon {
  background: linear-gradient(135deg, var(--color-warning) 0%, var(--color-pink) 100%);
  color: white;
}

.section-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0;
}

.pinned-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.pinned-card {
  position: relative;
  padding: 24px;
  cursor: pointer;
  border: 1px solid rgba(255, 149, 0, 0.15);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 250, 240, 0.8) 100%);
}

.pinned-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--color-warning) 0%, var(--color-pink) 50%, var(--color-purple) 100%);
}

.pinned-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: linear-gradient(135deg, var(--color-warning) 0%, var(--color-pink) 100%);
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: var(--radius-full);
}

.pinned-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.category-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  border-radius: var(--radius-full);
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
}

.category-badge.notice {
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
}

.category-badge.activity {
  background: rgba(191, 90, 242, 0.1);
  color: var(--color-purple);
}

.category-badge.task {
  background: rgba(255, 149, 0, 0.1);
  color: var(--color-warning);
}

.category-badge.job {
  background: rgba(94, 92, 230, 0.1);
  color: var(--color-indigo);
}

.category-badge.trade {
  background: rgba(52, 199, 89, 0.1);
  color: var(--color-success);
}

.category-badge.other {
  background: rgba(134, 134, 139, 0.1);
  color: var(--color-text-secondary);
}

.post-author-mini {
  display: flex;
  align-items: center;
  gap: 6px;
}

.author-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--color-border);
}

.author-name-mini {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.pinned-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--color-text);
  line-height: 1.4;
}

.pinned-excerpt {
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text-secondary);
  margin: 0 0 16px;
}

.pinned-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-time-mini {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.post-stats-mini {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.main-content-section {
  padding: 24px 0 60px;
}

.content-layout {
  display: grid;
  grid-template-columns: 240px 1fr 280px;
  gap: 24px;
}

.sidebar-left,
.sidebar-right {
  position: sticky;
  top: 76px;
  height: fit-content;
}

.sidebar-card {
  padding: 20px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
}

.category-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.category-item.active {
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.12) 0%, rgba(0, 113, 227, 0.06) 100%);
}

.category-item.active .category-name {
  color: var(--color-primary);
  font-weight: 500;
}

.category-icon {
  font-size: 18px;
}

.category-name {
  font-size: 14px;
  color: var(--color-text);
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-action {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--color-text);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.quick-action:hover {
  background: rgba(0, 113, 227, 0.08);
  color: var(--color-primary);
}

.quick-action.primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, #0077ed 100%);
  color: white;
}

.quick-action.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
}

.main-feed {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feed-header {
  padding: 20px;
}

.search-bar-wrapper {
  margin-bottom: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}

.search-box:focus-within {
  background: white;
  box-shadow: 0 0 0 2px var(--color-primary), 0 4px 12px rgba(0, 113, 227, 0.15);
}

.search-box .el-icon {
  font-size: 18px;
  color: var(--color-text-secondary);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 15px;
  color: var(--color-text);
  background: transparent;
}

.search-input::placeholder {
  color: var(--color-text-secondary);
}

.search-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.search-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.4);
}

.filter-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.type-filter {
  display: flex;
  gap: 8px;
}

.filter-pill {
  padding: 6px 16px;
  border: none;
  background: rgba(0, 0, 0, 0.04);
  border-radius: var(--radius-full);
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-pill:hover {
  color: var(--color-text);
  background: rgba(0, 0, 0, 0.08);
}

.filter-pill.active {
  background: var(--color-primary);
  color: white;
}

.sort-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.sort-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sort-btn:hover {
  color: var(--color-text);
}

.sort-btn.active {
  color: var(--color-primary);
  background: rgba(0, 113, 227, 0.1);
}

.posts-feed {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-item {
  padding: 24px;
  cursor: pointer;
}

.post-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.type-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: var(--radius-full);
}

.type-badge.notice {
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
}

.type-badge.task {
  background: rgba(255, 149, 0, 0.1);
  color: var(--color-warning);
}

.post-author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.level-badge-mini {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.level-badge-mini.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #a0522d 100%);
  color: white;
}

.level-badge-mini.silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #a9a9a9 100%);
  color: #1d1d1f;
}

.level-badge-mini.gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  color: #1d1d1f;
}

.level-badge-mini.black {
  background: linear-gradient(135deg, #2f2f2f 0%, #1a1a1a 100%);
  color: white;
}

.level-badge-mini.diamond {
  background: linear-gradient(135deg, #b9f2ff 0%, #87ceeb 100%);
  color: #1d1d1f;
}

.author-name {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.post-time {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.post-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
  line-height: 1.4;
  transition: color var(--transition-fast);
}

.post-item:hover .post-title {
  color: var(--color-primary);
}

.post-excerpt {
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-text-secondary);
  margin: 0;
}

.post-images {
  margin-top: 4px;
}

.image-grid {
  display: flex;
  gap: 8px;
}

.post-image {
  width: 120px;
  height: 90px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  background: var(--color-background);
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  margin-top: 4px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.post-stats {
  display: flex;
  align-items: center;
  gap: 20px;
}

.post-stats .stat-item {
  font-size: 13px;
}

.permission-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.read-more {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--color-primary);
  text-decoration: none;
  transition: gap var(--transition-fast);
}

.read-more:hover {
  gap: 8px;
}

.empty-state {
  padding: 60px 40px;
  text-align: center;
}

.empty-icon-wrapper {
  margin-bottom: 20px;
}

.empty-icon {
  font-size: 64px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--color-text);
}

.empty-desc {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0 0 24px;
}

.loading-state {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  margin-bottom: 16px;
}

.loading-icon {
  font-size: 32px;
  animation: spin 1s linear infinite;
  color: var(--color-primary);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.load-more-wrapper {
  text-align: center;
  padding: 20px;
}

.load-more-btn {
  padding: 14px 48px;
  font-size: 15px;
}

.hot-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hot-item {
  display: flex;
  gap: 12px;
  padding: 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.hot-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.hot-rank {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}

.hot-rank.top-three {
  background: linear-gradient(135deg, var(--color-warning) 0%, var(--color-pink) 100%);
  color: white;
}

.hot-content {
  flex: 1;
  min-width: 0;
}

.hot-title {
  font-size: 14px;
  margin: 0 0 4px;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hot-views {
  font-size: 12px;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-summary {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.user-info-mini {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-box {
  text-align: center;
  padding: 12px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: var(--radius-sm);
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.user-actions {
  display: flex;
  gap: 8px;
}

.mini-btn {
  flex: 1;
  padding: 8px 16px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: white;
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--color-text);
  text-decoration: none;
  text-align: center;
  transition: all var(--transition-fast);
}

.mini-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.mini-btn.primary {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.mini-btn.primary:hover {
  background: var(--color-primary-hover);
}

@media (max-width: 1200px) {
  .content-layout {
    grid-template-columns: 200px 1fr;
  }
  
  .sidebar-right {
    display: none;
  }
  
  .hero-title {
    font-size: 44px;
  }
}

@media (max-width: 900px) {
  .hero-content {
    flex-direction: column;
    text-align: center;
  }
  
  .hero-text {
    max-width: 100%;
  }
  
  .hero-visual {
    display: none;
  }
  
  .pinned-grid {
    grid-template-columns: 1fr;
  }
  
  .content-layout {
    grid-template-columns: 1fr;
  }
  
  .sidebar-left {
    position: static;
    order: 2;
  }
  
  .main-feed {
    order: 1;
  }
  
  .filter-toolbar {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 600px) {
  .hero-title {
    font-size: 32px;
  }
  
  .hero-subtitle {
    font-size: 17px;
  }
  
  .section-title {
    font-size: 22px;
  }
  
  .post-title {
    font-size: 18px;
  }
}
</style>
