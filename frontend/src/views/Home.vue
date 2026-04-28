<template>
  <div class="home-page">
    <section class="hero-section" v-if="!searchKeyword && !hasFilters">
      <div class="hero-background">
        <div class="hero-gradient"></div>
        <div class="hero-pattern"></div>
      </div>
      <div class="page-container hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="gradient-text">发现精彩</span>，分享价值
          </h1>
          <p class="hero-subtitle">
            在这里发布公告、分享任务，让信息触达更多人。
            <span class="highlight">置顶推广</span>让您的内容获得更多曝光。
          </p>
          <div class="hero-actions">
            <router-link v-if="user" to="/new-post" class="btn-primary hero-btn">
              <el-icon><Plus /></el-icon>
              立即发布
            </router-link>
            <router-link v-else to="/login" class="btn-outline hero-btn">
              登录发布
            </router-link>
          </div>
        </div>
        <div class="hero-stats" v-if="pinnedPosts.length > 0">
          <div class="stat-card">
            <div class="stat-icon">📌</div>
            <div class="stat-info">
              <div class="stat-number">{{ pinnedPosts.length }}</div>
              <div class="stat-label">置顶消息</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="pinned-section" v-if="pinnedPosts.length > 0">
      <div class="page-container">
        <div class="section-header">
          <div class="section-title-wrap">
            <span class="section-icon">📌</span>
            <h2 class="section-title">置顶精选</h2>
            <span class="pinned-badge">置顶推广</span>
          </div>
          <div class="section-actions">
            <router-link v-if="user" to="/my-posts" class="btn-text">
              我的发布
              <el-icon><ArrowRight /></el-icon>
            </router-link>
          </div>
        </div>
        <div class="pinned-grid">
          <div 
            v-for="(post, index) in pinnedPosts" 
            :key="post.id" 
            class="pinned-card card"
            :style="{ animationDelay: `${index * 0.1}s` }"
            @click="goToPost(post.id)"
          >
            <div class="pinned-card-gradient"></div>
            <div class="pinned-card-content">
              <div class="pinned-card-header">
                <div class="pinned-badge-large">
                  <span class="pinned-icon">📌</span>
                  <span>置顶</span>
                </div>
                <div class="post-type-badge" :class="post.is_task ? 'task' : 'notice'">
                  {{ post.is_task ? '任务' : '公告' }}
                </div>
              </div>
              <h3 class="pinned-card-title">{{ post.title }}</h3>
              <p class="pinned-card-excerpt">{{ truncate(post.content, 80) }}</p>
              <div class="pinned-card-footer">
                <div class="post-author-info">
                  <span class="level-badge" :class="post.author?.level">{{ post.author?.level_name }}</span>
                  <span class="author-name">{{ post.author?.username }}</span>
                </div>
                <div class="post-meta">
                  <span class="meta-item">
                    <el-icon><View /></el-icon>
                    {{ post.views_count }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Clock /></el-icon>
                    {{ formatTime(post.pinned_at || post.created_at) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="pinned-card-glow"></div>
          </div>
        </div>
        <div class="pin-promotion card">
          <div class="promotion-content">
            <div class="promotion-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="promotion-text">
              <h3>让您的内容获得更多曝光</h3>
              <p>
                花费 <span class="price-tag">¥{{ pinConfig?.price || 20 }}</span> 
                即可将您的公告置顶 
                <span class="highlight">{{ pinConfig?.duration_days || 7 }} 天</span>，
                获得首页黄金展示位！
              </p>
            </div>
            <router-link v-if="user" to="/my-posts" class="btn-primary">
              去置顶
            </router-link>
            <router-link v-else to="/login" class="btn-outline">
              登录后发布
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <section class="posts-section">
      <div class="page-container">
        <div class="search-container">
          <div class="search-box card">
            <el-icon class="search-icon"><Search /></el-icon>
            <input 
              type="text" 
              v-model="searchKeyword" 
              @keyup.enter="doSearch"
              placeholder="搜索公告标题或内容..."
              class="search-input"
            />
            <button class="search-btn" @click="doSearch" :disabled="searching">
              <span v-if="!searching">搜索</span>
              <span v-else>搜索中...</span>
            </button>
          </div>
          
          <div class="filter-bar">
            <div class="filter-group">
              <span class="filter-label">类型：</span>
              <div class="filter-buttons">
                <button 
                  v-for="type in typeOptions" 
                  :key="type.value"
                  class="filter-btn"
                  :class="{ active: postType === type.value }"
                  @click="selectType(type.value)"
                >
                  {{ type.label }}
                </button>
              </div>
            </div>
            <div class="filter-group">
              <span class="filter-label">排序：</span>
              <div class="filter-buttons">
                <button 
                  v-for="sort in sortOptions" 
                  :key="sort.value"
                  class="filter-btn"
                  :class="{ active: sortBy === sort.value }"
                  @click="selectSort(sort.value)"
                >
                  {{ sort.label }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="section-header posts-header">
          <div class="section-title-wrap">
            <span class="section-icon">📄</span>
            <h2 class="section-title">{{ sectionTitle }}</h2>
            <span class="count-badge" v-if="posts.length > 0">{{ posts.length }}</span>
          </div>
        </div>

        <div class="posts-list" v-if="posts.length > 0">
          <div 
            v-for="(post, index) in posts" 
            :key="post.id" 
            class="post-card card"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="goToPost(post.id)"
          >
            <div class="post-card-main">
              <div class="post-card-header">
                <div class="post-type-badge" :class="post.is_task ? 'task' : 'notice'">
                  {{ post.is_task ? '任务' : '公告' }}
                </div>
                <div class="post-author-small">
                  <span class="level-badge" :class="post.author?.level">{{ post.author?.level_name }}</span>
                  <span class="author-name">{{ post.author?.username }}</span>
                </div>
              </div>
              <h3 class="post-card-title">{{ post.title }}</h3>
              <p class="post-card-excerpt">{{ truncate(post.content, 120) }}</p>
              
              <div class="post-images" v-if="post.images?.length > 0">
                <div class="image-grid">
                  <img 
                    v-for="(img, imgIndex) in post.images.slice(0, 3)" 
                    :key="imgIndex"
                    :src="`/uploads/${img}`"
                    class="post-image"
                    alt="图片"
                  />
                </div>
              </div>
            </div>
            <div class="post-card-footer">
              <div class="permission-info">
                <el-icon><View /></el-icon>
                <span>{{ post.view_permission_name }}</span>
              </div>
              <div class="post-stats">
                <span class="stat-item">
                  <el-icon><View /></el-icon>
                  {{ post.views_count }}
                </span>
                <span class="stat-item">
                  <el-icon><Clock /></el-icon>
                  {{ formatTime(post.created_at) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="empty-state card" v-else-if="!loading && !searching">
          <div class="empty-icon">{{ searchKeyword ? '🔍' : '📭' }}</div>
          <h3 class="empty-title">{{ searchKeyword ? '未找到相关内容' : '暂无发布' }}</h3>
          <p class="empty-desc">
            {{ searchKeyword ? '请尝试其他关键词' : '平台还没有任何内容，快来发布第一条吧' }}
          </p>
          <router-link v-if="user && !searchKeyword" to="/new-post" class="btn-primary">
            立即发布
          </router-link>
        </div>

        <div class="loading-state" v-else>
          <el-icon class="loading-icon"><Loading /></el-icon>
          <p>加载中...</p>
        </div>

        <div class="load-more" v-if="hasMore && !loading && !searching">
          <button class="btn-secondary" @click="loadMore" :disabled="loading">
            <span v-if="!loading">加载更多</span>
            <span v-else>加载中...</span>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Clock, View, Loading, Search, Plus, ArrowRight, TrendCharts, Fire } from '@element-plus/icons-vue'
import { postApi, configApi } from '../services/api'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const { user } = useUserStore()

const posts = ref([])
const pinnedPosts = ref([])
const pinConfig = ref(null)
const loading = ref(false)
const searching = ref(false)
const page = ref(1)
const hasMore = ref(true)

const searchKeyword = ref('')
const postType = ref('all')
const sortBy = ref('latest')

const typeOptions = [
  { value: 'all', label: '全部' },
  { value: 'notice', label: '公告' },
  { value: 'task', label: '任务' }
]

const sortOptions = [
  { value: 'latest', label: '最新' },
  { value: 'hot', label: '热门' }
]

const hasFilters = computed(() => {
  return postType.value !== 'all' || sortBy.value !== 'latest'
})

const sectionTitle = computed(() => {
  if (searchKeyword.value) {
    return '搜索结果'
  }
  return sortBy.value === 'hot' ? '热门发布' : '最新发布'
})

const loadPinnedPosts = async () => {
  try {
    const response = await postApi.getPinned()
    if (response.data.success) {
      pinnedPosts.value = response.data.posts
      pinConfig.value = response.data.config
    }
  } catch (error) {
    console.error('加载置顶帖子失败:', error)
  }
}

const loadPosts = async (append = false) => {
  if (loading.value) return
  loading.value = true
  
  try {
    const params = {
      page: page.value,
      per_page: 15
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
  searching.value = true
  loadPosts(false).then(() => {
    searching.value = false
  })
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
  loadPinnedPosts()
  loadPosts()
})
</script>

<style scoped>
.home-page {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.hero-section {
  position: relative;
  padding: 64px 0 80px;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, 
    rgba(0, 122, 255, 0.08) 0%, 
    rgba(88, 86, 214, 0.04) 50%,
    transparent 100%
  );
}

.hero-pattern {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(
    circle at 1px 1px,
    rgba(0, 122, 255, 0.05) 1px,
    transparent 0
  );
  background-size: 40px 40px;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 48px;
}

.hero-text {
  flex: 1;
  max-width: 600px;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  line-height: 1.1;
  margin: 0 0 16px;
}

.gradient-text {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-indigo) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 18px;
  line-height: 1.6;
  color: var(--color-text-secondary);
  margin: 0 0 32px;
}

.highlight {
  color: var(--color-primary);
  font-weight: 600;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.hero-stats {
  flex-shrink: 0;
}

.stat-card {
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.08) 0%, rgba(88, 86, 214, 0.04) 100%);
  border: 1px solid rgba(0, 122, 255, 0.1);
  border-radius: var(--radius-xl);
  padding: 24px 32px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 32px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.pinned-section {
  padding: 48px 0;
  background: linear-gradient(180deg, 
    rgba(255, 255, 255, 0.5) 0%, 
    transparent 100%
  );
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  font-size: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

.section-actions {
  display: flex;
  gap: 12px;
}

.btn-text {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--color-primary);
  font-weight: 500;
}

.pinned-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.pinned-card {
  position: relative;
  cursor: pointer;
  overflow: hidden;
  padding: 24px;
  min-height: 220px;
  animation: slideUp 0.5s ease-out forwards;
  opacity: 0;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.pinned-card-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(0, 122, 255, 0.03) 0%, 
    rgba(255, 45, 85, 0.03) 100%
  );
  pointer-events: none;
}

.pinned-card-glow {
  position: absolute;
  inset: -50%;
  background: radial-gradient(
    circle at center,
    rgba(0, 122, 255, 0.08) 0%,
    transparent 60%
  );
  opacity: 0;
  transition: opacity var(--transition-normal);
  pointer-events: none;
}

.pinned-card:hover .pinned-card-glow {
  opacity: 1;
}

.pinned-card-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.pinned-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pinned-badge-large {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--gradient-pinned);
  color: white;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}

.pinned-icon {
  font-size: 14px;
}

.post-type-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: var(--radius-full);
}

.post-type-badge.notice {
  background: rgba(0, 122, 255, 0.12);
  color: var(--color-primary);
}

.post-type-badge.task {
  background: rgba(255, 149, 0, 0.12);
  color: var(--color-warning);
}

.pinned-card-title {
  font-size: 20px;
  font-weight: 600;
  line-height: 1.3;
  margin: 0 0 12px;
  color: var(--color-text);
  transition: color var(--transition-fast);
}

.pinned-card:hover .pinned-card-title {
  color: var(--color-primary);
}

.pinned-card-excerpt {
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-secondary);
  margin: 0 0 16px;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pinned-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--color-border-light);
}

.post-author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-name {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.meta-item .el-icon {
  font-size: 14px;
}

.pin-promotion {
  background: linear-gradient(135deg, 
    rgba(0, 122, 255, 0.04) 0%, 
    rgba(88, 86, 214, 0.02) 100%
  );
  border: 1px solid rgba(0, 122, 255, 0.1);
  padding: 24px 32px;
}

.promotion-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.promotion-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-xl);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-indigo) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.promotion-icon .el-icon {
  font-size: 24px;
  color: white;
}

.promotion-text {
  flex: 1;
}

.promotion-text h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px;
}

.promotion-text p {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

.price-tag {
  color: var(--color-primary);
  font-weight: 700;
  font-size: 16px;
}

.count-badge {
  padding: 4px 10px;
  background: rgba(0, 122, 255, 0.12);
  color: var(--color-primary);
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
}

.posts-section {
  flex: 1;
  padding: 32px 0 64px;
  background: var(--color-background);
}

.search-container {
  margin-bottom: 32px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  margin-bottom: 16px;
}

.search-icon {
  font-size: 20px;
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
  color: var