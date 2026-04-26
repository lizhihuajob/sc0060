<template>
  <div class="home-page">
    <section class="posts-section">
      <div class="page-container">
        <div class="section-header">
          <h2 class="section-title">最新发布</h2>
          <div class="section-stats">
            <span class="stat-item">
              <el-icon><Document /></el-icon>
              公告
            </span>
            <span class="stat-item">
              <el-icon><Clock /></el-icon>
              任务
            </span>
          </div>
        </div>

        <div class="posts-grid" v-if="posts.length > 0">
          <div 
            v-for="post in posts" 
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
                  v-for="(img, index) in post.images.slice(0, 3)" 
                  :key="index"
                  :src="`/uploads/${img}`"
                  class="post-image"
                  alt="图片"
                />
              </div>
            </div>

            <div class="post-footer">
              <div class="permission-info">
                <el-icon><View /></el-icon>
                <span>{{ post.view_permission_name }}</span>
              </div>
              <span class="post-time">{{ formatTime(post.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="empty-state" v-else-if="!loading">
          <div class="empty-icon">📭</div>
          <h3 class="empty-title">暂无发布</h3>
          <p class="empty-desc">平台还没有任何内容，快来发布第一条吧</p>
          <router-link to="/new-post" class="btn-primary">
            立即发布
          </router-link>
        </div>

        <div class="loading-state" v-else>
          <el-icon class="loading-icon"><Loading /></el-icon>
          <p>加载中...</p>
        </div>

        <div class="load-more" v-if="hasMore && !loading">
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Clock, View, Loading } from '@element-plus/icons-vue'
import { postApi } from '../services/api'

const router = useRouter()
const posts = ref([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

const loadPosts = async (append = false) => {
  if (loading.value) return
  loading.value = true
  
  try {
    const response = await postApi.getList({
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
  loadPosts()
})
</script>

<style scoped>
.home-page {
  flex: 1;
}

.posts-section {
  padding: 40px 20px 80px;
  background: var(--color-background);
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.003em;
  margin: 0;
  color: var(--color-text);
}

.section-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--color-text-secondary);
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
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
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

.post-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-name {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.level-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.level-badge.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #a0522d 100%);
  color: white;
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
  color: white;
}

.level-badge.diamond {
  background: linear-gradient(135deg, #b9f2ff 0%, #87ceeb 100%);
  color: #1d1d1f;
}

.post-content {
  margin-bottom: 16px;
}

.post-title {
  font-size: 18px;
  font-weight: 600;
  line-height: 1.3;
  margin: 0 0 8px;
  color: var(--color-text);
}

.post-excerpt {
  font-size: 14px;
  line-height: 1.5;
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
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  background: var(--color-background);
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.permission-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.post-time {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.empty-title {
  font-size: 21px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--color-text);
}

.empty-desc {
  font-size: 17px;
  color: var(--color-text-secondary);
  margin: 0 0 24px;
}

.empty-state .btn-primary {
  display: inline-block;
  padding: 12px 32px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: white;
  font-size: 15px;
  font-weight: 500;
}

.loading-icon {
  font-size: 32px;
  animation: spin 1s linear infinite;
  color: var(--color-text-secondary);
}

.loading-state p {
  font-size: 17px;
  color: var(--color-text-secondary);
  margin: 16px 0 0;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.load-more {
  text-align: center;
  margin-top: 40px;
}

.load-more .btn-secondary {
  padding: 12px 48px;
  font-size: 15px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: white;
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.load-more .btn-secondary:hover:not(:disabled) {
  background: var(--color-background);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.load-more .btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .posts-grid {
    grid-template-columns: 1fr;
  }
  
  .post-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
