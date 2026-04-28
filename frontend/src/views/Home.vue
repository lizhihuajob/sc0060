<template>
  <div class="home-page">
    <section class="hero-section" v-if="!hasSearched">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="gradient-text">发现</span>更多价值信息
          </h1>
          <p class="hero-desc">
            发布公告、分享任务，让信息触达更多人
          </p>
        </div>
        <div class="hero-search">
          <div class="search-box hero-search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <input 
              type="text" 
              v-model="searchKeyword" 
              @keyup.enter="doSearch"
              placeholder="搜索公告标题或内容..."
              class="search-input"
            />
            <button class="search-btn" @click="doSearch">
              <el-icon><Search /></el-icon>
              <span>搜索</span>
            </button>
          </div>
        </div>
      </div>
      <div class="hero-decoration">
        <div class="decoration-circle circle-1"></div>
        <div class="decoration-circle circle-2"></div>
        <div class="decoration-circle circle-3"></div>
      </div>
    </section>

    <section class="main-section">
      <div class="main-container">
        <div class="content-area">
          <div v-if="pinnedPosts.length > 0" class="pinned-section">
            <div class="section-header">
              <div class="section-title-wrapper">
                <span class="section-icon">📌</span>
                <h2 class="section-title">精选置顶</h2>
                <span class="pinned-badge">{{ pinnedPosts.length }}/{{ pinConfig.max_count }}</span>
              </div>
              <div class="section-action">
                <span class="pin-info">
                  <el-icon><Star /></el-icon>
                  置顶推广 ¥{{ pinConfig.price }}/{{ pinConfig.duration_days }}天
                </span>
              </div>
            </div>
            <div class="pinned-grid">
              <div 
                v-for="(post, index) in pinnedPosts" 
                :key="post.id" 
                class="pinned-card"
                :style="{ animationDelay: `${index * 0.1}s` }"
                @click="goToPost(post.id)"
              >
                <div class="pinned-header">
                  <div class="pinned-rank">{{ index + 1 }}</div>
                  <div class="pinned-meta">
                    <span class="pinned-tag">置顶</span>
                    <span class="type-badge" :class="post.is_task ? 'task' : 'notice'">
                      {{ post.is_task ? '任务' : '公告' }}
                    </span>
                  </div>
                </div>
                <div class="pinned-content">
                  <h3 class="pinned-title">{{ post.title }}</h3>
                  <p class="pinned-excerpt">{{ truncate(post.content, 80) }}</p>
                </div>
                <div class="pinned-footer">
                  <div class="pinned-author">
                    <span class="level-badge" :class="post.author?.level">{{ post.author?.level_name }}</span>
                    <span class="author-name">{{ post.author?.username }}</span>
                  </div>
                  <div class="pinned-stats">
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
                <div class="pinned-glow"></div>
              </div>
            </div>
          </div>

          <div class="posts-section">
            <div class="section-header">
              <div class="section-title-wrapper">
                <span class="section-icon">📄</span>
                <h2 class="section-title">
                  {{ hasSearched ? '搜索结果' : (sortBy === 'hot' ? '热门发布' : '最新发布') }}
                </h2>
                <span v-if="hasSearched && searchKeyword" class="search-keyword">
                  关键词: "{{ searchKeyword }}"
                  <button class="clear-search" @click="clearSearch">
                    <el-icon><Close /></el-icon>
                  </button>
                </span>
              </div>
              <div class="section-controls">
                <div v-if="!hasSearched" class="filter-tabs">
                  <button 
                    v-for="type in typeOptions" 
                    :key="type.value"
                    class="filter-tab"
                    :class="{ active: postType === type.value }"
                    @click="selectType(type.value)"
                  >
                    {{ type.label }}
                  </button>
                </div>
                <div class="sort-dropdown">
                  <el-dropdown @command="selectSort">
                    <span class="sort-trigger">
                      <el-icon><Sort /></el-icon>
                      {{ currentSortLabel }}
                      <el-icon class="caret"><CaretBottom /></el-icon>
                    </span>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item 
                          v-for="sort in sortOptions" 
                          :key="sort.value"
                          :command="sort.value"
                          :class="{ active: sortBy === sort.value }"
                        >
                          {{ sort.label }}
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
            </div>

            <div v-if="!hasSearched" class="mobile-search">
              <div class="search-box compact-search-box">
                <el-icon class="search-icon"><Search /></el-icon>
                <input 
                  type="text" 
                  v-model="searchKeyword" 
                  @keyup.enter="doSearch"
                  placeholder="搜索公告..."
                  class="search-input"
                />
                <button class="search-btn-icon" @click="doSearch">
                  <el-icon><Search /></el-icon>
                </button>
              </div>
            </div>

            <div class="posts-grid" v-if="posts.length > 0">
              <div 
                v-for="(post, index) in posts" 
                :key="post.id" 
                class="post-card card"
                :style="{ animationDelay: `${index * 0.05}s` }"
                @click="goToPost(post.id)"
              >
                <div class="post-header">
                  <div class="post-type">
                    <span class="type-badge" :class="post.is_task ? 'task' : 'notice'">
                      {{ post.is_task ? '任务' : '公告' }}
                    </span>
                  </div>
                  <div class="post-author">
                    <span class="level-badge" :class="post.author?.level">{{ post.author?.level_name }}</span>
                    <span class="author-name">{{ post.author?.username }}</span>
                  </div>
                </div>
                
                <div class="post-content">
                  <h3 class="post-title">{{ post.title }}</h3>
                  <p class="post-excerpt">{{ truncate(post.content, 120) }}</p>
                </div>

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

                <div class="post-footer">
                  <div class="post-stats">
                    <span class="stat-item">
                      <el-icon><View /></el-icon>
                      {{ post.views_count }}
                    </span>
                    <span class="stat-item">
                      <el-icon><Lock /></el-icon>
                      {{ post.view_permission_name }}
                    </span>
                  </div>
                  <span class="post-time">{{ formatTime(post.created_at) }}</span>
                </div>
              </div>
            </div>

            <div class="empty-state" v-else-if="!loading">
              <div class="empty-icon">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3Z" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M9 10H15" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M9 14H15" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <h3 class="empty-title">暂无发布</h3>
              <p class="empty-desc">
                {{ hasSearched ? '没有找到相关内容，请尝试其他关键词' : '平台还没有任何内容，快来发布第一条吧' }}
              </p>
              <template v-if="!hasSearched">
                <router-link to="/new-post" class="btn-primary">
                  <el-icon><Plus /></el-icon>
                  立即发布
                </router-link>
              </template>
            </div>

            <div class="loading-state" v-else>
              <div class="loading-spinner">
                <div class="spinner-circle"></div>
              </div>
              <p>加载中...</p>
            </div>

            <div class="load-more" v-if="hasMore && !loading">
              <button class="load-more-btn" @click="loadMore" :disabled="loading">
                <span v-if="!loading">加载更多</span>
                <span v-else>加载中...</span>
                <el-icon class="arrow-icon"><ArrowDown /></el-icon>
              </button>
            </div>
          </div>
        </div>

        <div class="sidebar">
          <div class="sidebar-card card">
            <div class="sidebar-header">
              <span class="sidebar-icon">💎</span>
              <h3 class="sidebar-title">升级会员</h3>
            </div>
            <p class="sidebar-desc">解锁更多发布额度和专属特权</p>
            <router-link to="/upgrade" class="btn-primary sidebar-btn">
              立即升级
            </router-link>
          </div>

          <div class="sidebar-card card">
            <div class="sidebar-header">
              <span class="sidebar-icon">📌</span>
              <h3 class="sidebar-title">置顶推广</h3>
            </div>
            <div class="pin-stats">
              <div class="pin-stat-item">
                <span class="pin-stat-value">¥{{ pinConfig.price }}</span>
                <span class="pin-stat-label">价格</span>
              </div>
              <div class="pin-stat-item">
                <span class="pin-stat-value">{{ pinConfig.duration_days }}天</span>
                <span class="pin-stat-label">有效期</span>
              </div>
              <div class="pin-stat-item">
                <span class="pin-stat-value">{{ pinConfig.max_count }}位</span>
                <span class="pin-stat-label">坑位</span>
              </div>
            </div>
            <p class="sidebar-hint">让你的信息获得更多曝光</p>
          </div>

          <div class="sidebar-card card quick-actions">
            <div class="sidebar-header">
              <span class="sidebar-icon">⚡</span>
              <h3 class="sidebar-title">快捷操作</h3>
            </div>
            <div class="action-list">
              <router-link to="/new-post" class="action-item">
                <div class="action-icon publish-icon">
                  <el-icon><Edit /></el-icon>
                </div>
                <span>发布公告</span>
              </router-link>
              <router-link to="/my-posts" class="action-item" v-if="user">
                <div class="action-icon my-posts-icon">
                  <el-icon><Document /></el-icon>
                </div>
                <span>我的发布</span>
              </router-link>
              <router-link to="/recharge" class="action-item" v-if="user">
                <div class="action-icon recharge-icon">
                  <el-icon><Wallet /></el-icon>
                </div>
                <span>账户充值</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Document, Clock, View, Loading, Search, Fire, 
  Star, Plus, ArrowDown, Close, Edit, Wallet,
  Lock, CaretBottom, Sort
} from '@element-plus/icons-vue'
import { postApi } from '../services/api'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const { user } = useUserStore()

const posts = ref([])
const pinnedPosts = ref([])
const pinConfig = ref({
  price: 20,
  duration_days: 7,
  max_count: 3
})
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)
const hasSearched = ref(false)

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

const currentSortLabel = computed(() => {
  const sort = sortOptions.find(s => s.value === sortBy.value)
  return sort ? sort.label : '最新'
})

const loadPinnedPosts = async () => {
  try {
    const response = await postApi.getPinned()
    if (response.data.success) {
      pinnedPosts.value = response.data.posts
      if (response.data.config) {
        pinConfig.value = response.data.config
      }
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
      per_page: 12
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
  hasSearched.value = !!searchKeyword.value
  page.value = 1
  posts.value = []
  loadPosts(false)
}

const clearSearch = () => {
  searchKeyword.value = ''
  hasSearched.value = false
  page.value = 1
  posts.value = []
  loadPosts(false)
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
  min-height: 100vh;
  background: var(--color-background);
}

.hero-section {
  position: relative;
  padding: 80px 0 60px;
  background: linear-gradient(180deg, #ffffff 0%, var(--color-background) 100%);
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
}

.hero-text {
  margin-bottom: 40px;
}

.hero-title {
  font-size: clamp(36px, 6vw, 56px);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 16px;
  line-height: 1.1;
}

.gradient-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  margin: 0;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.hero-search {
  max-width: 600px;
  margin: 0 auto;
}

.hero-search-box {
  padding: 8px;
  border-radius: var(--radius-xl);
  background: white;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border-light);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  transition: all var(--transition-fast);
}

.search-box:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
}

.search-icon {
  font-size: 20px;
  color: var(--color-text-tertiary);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: var(--font-size-base);
  color: var(--color-text);
  background: transparent;
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}

.search-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
}

.search-btn-icon {
  padding: 10px;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.hero-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
  filter: blur(60px);
  animation: float 8s ease-in-out infinite;
}

.circle-1 {
  width: 300px;
  height: 300px;
  background: var(--gradient-primary);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #FF2D55 0%, #FF3B30 100%);
  top: 20%;
  right: 15%;
  animation-delay: 2s;
}

.circle-3 {
  width: 200px;
  height: 200px;
  background: var(--gradient-gold);
  bottom: 10%;
  left: 30%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-30px) scale(1.05); }
}

.main-section {
  position: relative;
  z-index: 3;
  padding: 40px 0;
}

.main-container {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 40px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.content-area {
  min-width: 0;
}

.sidebar {
  width: 320px;
  flex-shrink: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.section-icon {
  font-size: 24px;
}

.section-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  margin: 0;
  color: var(--color-text);
}

.pinned-badge {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  background: rgba(0, 0, 0, 0.04);
  padding: 4px 10px;
  border-radius: var(--radius-full);
}

.section-action {
  display: flex;
  align-items: center;
}

.pin-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.section-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filter-tabs {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: var(--radius-md);
}

.filter-tab {
  padding: 8px 16px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-tab:hover {
  color: var(--color-text);
}

.filter-tab.active {
  background: white;
  color: var(--color-text);
  font-weight: var(--font-weight-medium);
  box-shadow: var(--shadow-sm);
}

.sort-dropdown {
  position: relative;
}

.sort-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sort-trigger:hover {
  border-color: var(--color-border);
}

.caret {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.search-keyword {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  background: rgba(0, 122, 255, 0.08);
  padding: 6px 12px;
  border-radius: var(--radius-full);
}

.clear-search {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.clear-search:hover {
  background: rgba(0, 0, 0, 0.08);
  color: var(--color-text);
}

.mobile-search {
  display: none;
  margin-bottom: 24px;
}

.compact-search-box {
  padding: 10px 12px;
}

.pinned-section {
  margin-bottom: 48px;
}

.pinned-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.pinned-card {
  position: relative;
  background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
  border-radius: var(--radius-xl);
  padding: 24px;
  cursor: pointer;
  transition: all var(--transition-normal);
  border: 1px solid var(--color-border-light);
  overflow: hidden;
  animation: slideUp 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

@keyframes slideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.pinned-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
  border-color: var(--color-primary);
}

.pinned-card:hover .pinned-glow {
  opacity: 1;
}

.pinned-glow {
  position: absolute;
  inset: -50%;
  background: radial-gradient(circle at center, rgba(0, 122, 255, 0.08) 0%, transparent 70%);
  opacity: 0;
  transition: opacity var(--transition-slow);
  pointer-events: none;
}

.pinned-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pinned-rank {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary);
  color: white;
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-lg);
}

.pinned-card:first-child .pinned-rank {
  background: var(--gradient-gold);
}

.pinned-card:nth-child(2) .pinned-rank {
  background: linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%);
}

.pinned-card:nth-child(3) .pinned-rank {
  background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%);
}

.pinned-meta {
  display: flex;
  gap: 8px;
}

.pinned-tag {
  padding: 4px 10px;
  background: var(--gradient-pinned);
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.type-badge {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  padding: 4px 10px;
  border-radius: var(--radius-full);
}

.type-badge.notice {
  background: rgba(0, 122, 255, 0.12);
  color: var(--color-primary);
}

.type-badge.task {
  background: rgba(255, 149, 0, 0.12);
  color: var(--color-warning);
}

.pinned-content {
  margin-bottom: 16px;
}

.pinned-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 8px;
  color: var(--color-text);
  line-height: 1.4;
}

.pinned-excerpt {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pinned-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--color-border-light);
}

.pinned-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.pinned-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.posts-section {
  position: relative;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.post-card {
  padding: 24px;
  cursor: pointer;
  animation: fadeInUp 0.4s ease forwards;
  opacity: 0;
  transform: translateY(10px);
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.post-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.post-content {
  margin-bottom: 16px;
}

.post-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  line-height: 1.4;
  margin: 0 0 8px;
  color: var(--color-text);
  transition: color var(--transition-fast);
}

.post-card:hover .post-title {
  color: var(--color-primary);
}

.post-excerpt {
  font-size: var(--font-size-sm);
  line-height: 1.6;
  color: var(--color-text-secondary);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-images {
  margin-bottom: 16px;
}

.image-grid {
  display: flex;
  gap: 8px;
  overflow: hidden;
}

.post-image {
  width: 72px;
  height: 72px;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: var(--color-background);
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-light);
}

.post-stats {
  display: flex;
  gap: 16px;
}

.post-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

.empty-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 8px;
  color: var(--color-text);
}

.empty-desc {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0 0 24px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.spinner-circle {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border-light);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.load-more {
  text-align: center;
  margin-top: 48px;
}

.load-more-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 40px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  font-size: var(--font-size-base);
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.load-more-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.arrow-icon {
  transition: transform var(--transition-fast);
}

.load-more-btn:hover .arrow-icon {
  transform: translateY(2px);
}

.sidebar-card {
  padding: 24px;
  margin-bottom: 20px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.sidebar-icon {
  font-size: 24px;
}

.sidebar-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0;
  color: var(--color-text);
}

.sidebar-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 20px;
  line-height: 1.5;
}

.sidebar-btn {
  width: 100%;
  justify-content: center;
}

.pin-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.pin-stat-item {
  text-align: center;
  padding: 12px 8px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: var(--radius-md);
}

.pin-stat-value {
  display: block;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.pin-stat-label {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.sidebar-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin: 0;
  text-align: center;
}

.quick-actions {
  background: white;
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  color: var(--color-text);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.action-item:hover {
  background: rgba(0, 0, 0, 0.04);
  transform: translateX(4px);
}

.action-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
}

.publish-icon {
  background: rgba(0, 122, 255, 0.12);
  color: var(--color-primary);
}

.my-posts-icon {
  background: rgba(52, 199, 89, 0.12);
  color: var(--color-success);
}

.recharge-icon {
  background: rgba(255, 149, 0, 0.12);
  color: var(--color-warning);
}

@media (max-width: 1200px) {
  .main-container {
    grid-template-columns: 1fr 280px;
    gap: 24px;
    padding: 0 24px;
  }
  
  .sidebar {
    width: 280px;
  }
  
  .pinned-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 992px) {
  .hero-section {
    padding: 48px 0 40px;
  }
  
  .main-container {
    grid-template-columns: 1fr;
    padding: 0 20px;
  }
  
  .sidebar {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 40px;
  }
  
  .sidebar-card {
    margin-bottom: 0;
  }
  
  .pinned-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 32px 0;
  }
  
  .decoration-circle {
    opacity: 0.3;
  }
  
  .hero-desc {
    font-size: var(--font-size-base);
  }
  
  .hero-search-box {
    padding: 6px;
    border-radius: var(--radius-lg);
  }
  
  .search-btn span {
    display: none;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .section-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .filter-tabs {
    flex-wrap: wrap;
  }
  
  .mobile-search {
    display: block;
  }
  
  .sidebar {
    grid-template-columns: 1fr;
  }
  
  .posts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .post-card {
    padding: 20px;
  }
  
  .load-more-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .main-container {
    padding: 0 16px;
  }
  
  .section-title-wrapper {
    flex-wrap: wrap;
  }
  
  .filter-tabs {
    display: none;
  }
  
  .sort-trigger {
    padding: 8px 12px;
  }
  
  .pinned-card {
    padding: 20px;
  }
  
  .pinned-rank {
    width: 32px;
    height: 32px;
    font-size: var(--font-size-base);
  }
  
  .pinned-header {
    margin-bottom: 12px;
  }
  
  .pinned-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .pinned-stats {
    width: 100%;
    justify-content: space-between;
  }
}

:deep(.el-dropdown-menu__item) {
  font-size: var(--font-size-sm);
}

:deep(.el-dropdown-menu__item.active) {
  color: var(--color-primary);
  font-weight: var(--font-weight-medium);
}
</style>
