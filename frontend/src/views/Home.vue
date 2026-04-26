<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">信息发布平台</h1>
        <p class="hero-subtitle">发布公告、发布任务，让信息触达更多人</p>
        <div class="hero-actions">
          <router-link to="/new-post" class="btn-primary" v-if="user">
            <el-icon><Edit /></el-icon>
            发布信息
          </router-link>
        </div>
      </div>
    </section>

    <section class="posts-section">
      <div class="page-container">
        <div class="section-header">
          <h2 class="section-title">最新发布</h2>
          <p class="section-subtitle" v-if="!user">(仅显示公开信息)</p>
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
              <p class="post-excerpt">{{ truncate(post.content, 150) }}</p>
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
              <span class="more-images" v-if="post.images.length > 3">
                +{{ post.images.length - 3 }} 张图片
              </span>
            </div>

            <div class="post-footer">
              <span class="post-permission">
                <el-icon><View /></el-icon>
                {{ post.view_permission_name }}
              </span>
              <span class="post-time">{{ post.created_at }}</span>
            </div>
          </div>
        </div>

        <div class="empty-state" v-else-if="!loading">
          <div class="empty-icon">📭</div>
          <h3 class="empty-title">暂无发布的信息</h3>
          <p class="empty-desc">成为第一个发布信息的人吧！</p>
          <router-link to="/new-post" class="btn-primary" v-if="user">
            立即发布
          </router-link>
        </div>

        <div class="loading-state" v-else>
          <el-icon class="loading-icon"><Loading /></el-icon>
          <p>加载中...</p>
        </div>

        <div class="load-more" v-if="hasMore && !loading">
          <button class="btn-secondary" @click="loadMore" :disabled="loading">
            加载更多
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Edit, View, Loading } from '@element-plus/icons-vue'
import { postApi } from '../services/api'
import { useUserStore } from '../stores/userStore'

const { user } = useUserStore()

const router = useRouter()
const posts = ref([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

const truncate = (text, length) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.slice(0, length) + '...'
}

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

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.home-page {
  flex: 1;
}

.hero-section {
  background: linear-gradient(180deg, #ffffff 0%, #f5f5f7 100%);
  padding: 80px 20px 60px;
  text-align: center;
}

.hero-content {
  max-width: 600px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 600;
  letter-spacing: -0.015em;
  line-height: 1.15;
  margin: 0 0 16px;
  background: linear-gradient(135deg, #1d1d1f 0%, #6e6e73 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 21px;
  line-height: 1.47059;
  font-weight: 400;
  letter-spacing: -0.01em;
  color: var(--color-text-secondary);
  margin: 0 0 32px;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.hero-actions .btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  font-size: 17px;
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: white;
}

.posts-section {
  padding: 60px 0 80px;
  background: var(--color-background);
}

.section-header {
  margin-bottom: 32px;
}

.section-title {
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.003em;
  margin: 0 0 8px;
  color: var(--color-text);
}

.section-subtitle {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0;
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
  font-size: 20px;
  font-weight: 600;
  line-height: 1.3;
  margin: 0 0 8px;
  color: var(--color-text);
}

.post-excerpt {
  font-size: 15px;
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
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: var(--color-background);
}

.more-images {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: 8px;
  display: inline-block;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.post-permission {
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

.empty-state {
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

.loading-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-text-secondary);
}

.loading-icon {
  font-size: 24px;
  animation: spin 1s linear infinite;
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
  padding: 12px 32px;
  font-size: 15px;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 36px;
  }
  
  .hero-subtitle {
    font-size: 19px;
  }
  
  .posts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
