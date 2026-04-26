<template>
  <div class="my-posts-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">我的发布</h1>
        <router-link to="/new-post" class="btn-primary">
          <el-icon><Edit /></el-icon>
          发布新信息
        </router-link>
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
            <div class="post-meta">
              <span class="permission">{{ post.view_permission_name }}</span>
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
            <span class="post-time">{{ post.created_at }}</span>
          </div>
        </div>
      </div>

      <div class="empty-state" v-else-if="!loading">
        <div class="empty-icon">📝</div>
        <h3 class="empty-title">暂无发布</h3>
        <p class="empty-desc">发布您的第一条信息吧</p>
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
          加载更多
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Edit, Loading } from '@element-plus/icons-vue'
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
    const response = await postApi.getMyPosts({
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

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.my-posts-page {
  flex: 1;
  padding: 40px 0;
  background: var(--color-background);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.003em;
  margin: 0;
  color: var(--color-text);
}

.page-header .btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: white;
  font-size: 15px;
  font-weight: 500;
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

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.permission {
  font-size: 13px;
  color: var(--color-text-secondary);
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
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
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
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .posts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
