<template>
  <div class="my-posts-page">
    <div class="page-container">
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">我的发布</h1>
          <p class="page-subtitle">管理您发布的所有公告和任务</p>
        </div>
        <router-link to="/new-post" class="btn-primary publish-btn">
          <el-icon><Edit /></el-icon>
          <span>发布新信息</span>
        </router-link>
      </div>

      <div v-if="pinnedPosts.length > 0" class="pinned-section">
        <div class="section-header">
          <div class="section-title-wrapper">
            <span class="section-icon">📌</span>
            <h2 class="section-title">我的置顶</h2>
          </div>
          <div class="section-info">
            <span class="info-text">
              <el-icon><Star /></el-icon>
              置顶推广 ¥{{ pinConfig.price }}/{{ pinConfig.duration_days }}天
            </span>
          </div>
        </div>
        <div class="pinned-grid">
          <div 
            v-for="(post, index) in pinnedPosts" 
            :key="post.id" 
            class="pinned-card card"
            @click="goToPost(post.id)"
          >
            <div class="pinned-header">
              <div class="pinned-badge">
                <span class="pinned-icon">📌</span>
                <span>已置顶</span>
              </div>
              <span class="type-badge" :class="post.is_task ? 'task' : 'notice'">
                {{ post.is_task ? '任务' : '公告' }}
              </span>
            </div>
            <div class="pinned-content">
              <h3 class="pinned-title">{{ post.title }}</h3>
              <p class="pinned-excerpt">{{ truncate(post.content, 100) }}</p>
            </div>
            <div class="pinned-footer">
              <div class="pin-time-info">
                <span class="time-label">置顶时间:</span>
                <span class="time-value">{{ formatTime(post.pinned_at) }}</span>
              </div>
              <div class="action-buttons">
                <span class="expire-badge">
                  有效期 {{ pinConfig.duration_days }} 天
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
            <h2 class="section-title">全部发布</h2>
            <span class="post-count">{{ posts.length }} 条</span>
          </div>
        </div>

        <div class="posts-grid" v-if="normalPosts.length > 0">
          <div 
            v-for="post in normalPosts" 
            :key="post.id" 
            class="post-card card"
            @click="goToPost(post.id)"
          >
            <div class="post-header">
              <div class="post-type">
                <span class="type-badge" :class="post.is_task ? 'task' : 'notice'">
                  {{ post.is_task ? '任务' : '公告' }}
                </span>
              </div>
              <div class="post-meta">
                <span class="permission">{{ post.view_permission_name }}</span>
                <span class="view-count">
                  <el-icon><View /></el-icon>
                  {{ post.views_count }}
                </span>
              </div>
            </div>
            
            <div class="post-content">
              <h3 class="post-title">{{ post.title }}</h3>
              <p class="post-excerpt">{{ truncate(post.content, 120) }}</p>
            </div>

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
              <div class="footer-left">
                <span class="post-time">{{ formatTime(post.created_at) }}</span>
              </div>
              <div class="footer-right">
                <button 
                  class="action-btn pin-btn" 
                  @click="pinPost(post, $event)" 
                  title="置顶"
                  :disabled="pinningPostId === post.id"
                >
                  <el-icon v-if="pinningPostId !== post.id"><Promotion /></el-icon>
                  <el-icon v-else class="loading"><Loading /></el-icon>
                  <span>置顶</span>
                </button>
                <button 
                  class="action-btn edit-btn" 
                  @click="editPost(post, $event)" 
                  title="编辑"
                >
                  <el-icon><Edit /></el-icon>
                  <span>编辑</span>
                </button>
                <button class="action-btn delete-btn" @click="deletePost(post, $event)" title="删除">
                  <el-icon><Delete /></el-icon>
                  <span>删除</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="empty-state" v-else-if="!loading && posts.length === 0">
          <div class="empty-icon-wrapper">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3Z" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 10H15" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 14H15" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3 class="empty-title">暂无发布</h3>
          <p class="empty-desc">发布您的第一条信息，让更多人看到</p>
          <router-link to="/new-post" class="btn-primary">
            <el-icon><Edit /></el-icon>
            立即发布
          </router-link>
        </div>

        <div class="empty-state" v-else-if="!loading && normalPosts.length === 0 && pinnedPosts.length > 0">
          <p class="empty-desc">您的所有内容已置顶</p>
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
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Edit, Loading, Delete, View, Promotion } from '@element-plus/icons-vue'
import { postApi } from '../services/api'
import { configApi } from '../services/api'

const router = useRouter()
const posts = ref([])
const pinningPostId = ref(null)
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)
const pinConfig = ref({
  price: 20,
  duration_days: 7,
  max_count: 3
})

const pinnedPosts = computed(() => {
  return posts.value.filter(post => post.is_pinned)
})

const normalPosts = computed(() => {
  return posts.value.filter(post => !post.is_pinned)
})

const loadConfig = async () => {
  try {
    const response = await configApi.getMembership()
    if (response.data.success && response.data.pin_config) {
      pinConfig.value = response.data.pin_config
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

const loadPosts = async (append = false) => {
  if (loading.value) return
  loading.value = true
  
  try {
    const response = await postApi.getMy({
      page: page.value,
      per_page: 10
    })
    
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

const loadMore = () => {
  page.value++
  loadPosts(true)
}

const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}

const pinPost = async (post, event) => {
  event.stopPropagation()
  
  if (pinningPostId.value) return
  
  try {
    await ElMessageBox.confirm(
      `置顶此公告需要 ¥${pinConfig.value.price}，有效期 ${pinConfig.value.duration_days} 天。确定要置顶吗？`,
      '确认置顶',
      {
        confirmButtonText: '确定置顶',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    pinningPostId.value = post.id
    const response = await postApi.pin(post.id)
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
      post.is_pinned = 1
      post.pinned_at = new Date().toISOString()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '置顶失败')
    }
  } finally {
    pinningPostId.value = null
  }
}

const deletePost = async (post, event) => {
  event.stopPropagation()
  
  try {
    await ElMessageBox.confirm(
      '确定要删除这条公告吗？删除后无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await postApi.delete(post.id)
    if (response.data.success) {
      ElMessage.success('删除成功')
      posts.value = posts.value.filter(p => p.id !== post.id)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const editPost = (post, event) => {
  event.stopPropagation()
  router.push(`/edit-post/${post.id}`)
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
  loadConfig()
  loadPosts()
})
</script>

<style scoped>
.my-posts-page {
  flex: 1;
  padding: 40px 0;
  background: var(--color-background);
  min-height: 100vh;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
  gap: 24px;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  letter-spacing: -0.015em;
  margin: 0 0 8px;
  color: var(--color-text);
}

.page-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.publish-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border-radius: var(--radius-xl);
  text-decoration: none;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
}

.pinned-section {
  margin-bottom: 48px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  font-size: 24px;
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin: 0;
  color: var(--color-text);
}

.post-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  background: rgba(0, 0, 0, 0.04);
  padding: 4px 12px;
  border-radius: var(--radius-full);
}

.section-info {
  display: flex;
  align-items: center;
}

.info-text {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.pinned-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.pinned-card {
  position: relative;
  padding: 24px;
  cursor: pointer;
  overflow: hidden;
  background: linear-gradient(135deg, #fffaf0 0%, #ffffff 100%);
  border: 1px solid rgba(255, 159, 10, 0.15);
}

.pinned-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}

.pinned-card:hover .pinned-glow {
  opacity: 1;
}

.pinned-glow {
  position: absolute;
  inset: -50%;
  background: radial-gradient(circle at center, rgba(255, 159, 10, 0.1) 0%, transparent 70%);
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

.pinned-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--gradient-pinned);
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.pinned-icon {
  font-size: 14px;
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
  line-height: 1.6;
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
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.pin-time-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.time-value {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.expire-badge {
  font-size: var(--font-size-xs);
  color: var(--color-warning);
  background: rgba(255, 149, 0, 0.1);
  padding: 4px 10px;
  border-radius: var(--radius-full);
}

.posts-section {
  position: relative;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
}

.post-card {
  padding: 24px;
  cursor: pointer;
  transition: all var(--transition-normal);
  border: 1px solid transparent;
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

.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.permission {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  background: rgba(0, 0, 0, 0.04);
  padding: 4px 10px;
  border-radius: var(--radius-full);
}

.view-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
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
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: var(--color-background);
}

.post-footer {
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  display: flex;
  align-items: center;
}

.post-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.footer-right {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: var(--font-size-xs);
}

.pin-btn {
  color: var(--color-warning);
}

.pin-btn:hover:not(:disabled) {
  background: rgba(255, 149, 0, 0.1);
}

.pin-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pin-btn .loading {
  animation: spin 1s linear infinite;
}

.edit-btn {
  color: var(--color-primary);
}

.edit-btn:hover {
  background: rgba(0, 113, 227, 0.1);
}

.delete-btn {
  color: var(--color-danger);
}

.delete-btn:hover {
  background: rgba(255, 59, 48, 0.1);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon-wrapper {
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

.loading-state {
  text-align: center;
  padding: 60px 20px;
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
  padding: 14px 48px;
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

@media (max-width: 768px) {
  .my-posts-page {
    padding: 24px 0;
  }
  
  .page-container {
    padding: 0 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .page-title {
    font-size: var(--font-size-2xl);
  }
  
  .publish-btn {
    width: 100%;
    justify-content: center;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .pinned-grid {
    grid-template-columns: 1fr;
  }
  
  .posts-grid {
    grid-template-columns: 1fr;
  }
  
  .post-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .footer-right {
    justify-content: flex-end;
  }
  
  .load-more-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .post-card {
    padding: 20px;
  }
  
  .pinned-card {
    padding: 20px;
  }
  
  .pinned-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: flex-end;
  }
}
</style>
