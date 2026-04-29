<template>
  <div class="post-detail-page">
    <div class="page-container">
      <div class="back-link" @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </div>

      <div class="post-card card" v-if="post">
        <div class="post-header">
          <div class="post-type">
            <span class="type-badge" :class="post.is_task ? 'task' : 'notice'">
              {{ post.is_task ? '任务' : '公告' }}
            </span>
          </div>
          <div class="post-author">
            <span class="level-badge" :class="post.author?.level">{{ post.author?.level_name }}</span>
            <span class="author-name">{{ post.author?.username }}</span>
            <span class="post-time">{{ post.created_at }}</span>
          </div>
        </div>

        <h1 class="post-title">{{ post.title }}</h1>

        <div class="post-content">
          <p>{{ post.content }}</p>
        </div>

        <div class="post-images" v-if="post.images?.length > 0">
          <div class="image-grid">
            <img 
              v-for="(img, index) in post.images" 
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
            <span>可见范围：{{ post.view_permission_name }}</span>
          </div>
          <div class="view-info">
            <el-icon><View /></el-icon>
            <span>{{ post.views_count }} 次浏览</span>
          </div>
        </div>
      </div>

      <div class="comments-section card" v-if="post">
        <div class="comments-header">
          <h3 class="comments-title">
            <el-icon><ChatDotRound /></el-icon>
            留言互动 ({{ commentsCount }})
          </h3>
        </div>

        <div class="comment-form" v-if="currentUser">
          <div class="form-header">
            <div class="user-avatar-small">
              <img v-if="currentUser.avatar" :src="`/uploads/${currentUser.avatar}`" alt="头像" class="avatar-img" />
              <el-icon v-else><User /></el-icon>
            </div>
            <span class="user-name">{{ currentUser.username }}</span>
          </div>
          <textarea 
            v-model="newComment" 
            placeholder="说点什么..." 
            class="comment-textarea"
            rows="3"
          ></textarea>
          <div class="form-actions">
            <span class="char-count">{{ newComment.length }}/500</span>
            <button class="btn-primary" @click="submitComment" :disabled="!newComment.trim() || submitting">
              <span v-if="!submitting">发布留言</span>
              <span v-else>发布中...</span>
            </button>
          </div>
        </div>

        <div class="login-prompt" v-else>
          <p>登录后即可参与留言互动</p>
          <router-link to="/login" class="btn-primary">立即登录</router-link>
        </div>

        <div class="comments-list" v-if="comments.length > 0">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <div class="comment-avatar">
                <img v-if="comment.author?.avatar" :src="`/uploads/${comment.author?.avatar}`" alt="头像" class="avatar-img" />
                <el-icon v-else><User /></el-icon>
              </div>
              <div class="comment-info">
                <div class="comment-author">
                  <span class="author-name">{{ comment.author?.username }}</span>
                  <span class="level-badge" :class="comment.author?.level">{{ comment.author?.level_name }}</span>
                </div>
                <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
              </div>
              <button 
                v-if="currentUser && comment.user_id === currentUser.id"
                class="delete-comment-btn" 
                @click="deleteComment(comment)"
                title="删除留言"
              >
                <el-icon><Delete /></el-icon>
              </button>
            </div>
            <div class="comment-content">
              <p>{{ comment.content }}</p>
            </div>
          </div>
        </div>

        <div class="empty-comments" v-else-if="!loadingComments">
          <div class="empty-icon">💬</div>
          <p>暂无留言，快来抢沙发吧！</p>
        </div>

        <div class="loading-comments" v-else>
          <el-icon class="loading-icon"><Loading /></el-icon>
        </div>
      </div>

      <div class="loading-state" v-else-if="loading">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>加载中...</p>
      </div>

      <div class="error-state" v-else>
        <div class="error-icon">😕</div>
        <h3 class="error-title">内容不存在</h3>
        <p class="error-desc">该内容可能已被删除或您没有权限查看</p>
        <router-link to="/" class="btn-primary">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, View, Loading, ChatDotRound, User, Delete } from '@element-plus/icons-vue'
import { postApi, authApi } from '../services/api'

const router = useRouter()
const route = useRoute()
const post = ref(null)
const loading = ref(true)
const currentUser = ref(null)
const comments = ref([])
const commentsCount = ref(0)
const loadingComments = ref(false)
const newComment = ref('')
const submitting = ref(false)

const loadPost = async () => {
  loading.value = true
  try {
    const response = await postApi.getById(route.params.id)
    if (response.data.success) {
      post.value = response.data.post
      comments.value = response.data.comments || []
      commentsCount.value = response.data.comments_count || 0
    }
  } catch (error) {
    console.error('加载帖子失败:', error)
  } finally {
    loading.value = false
  }
}

const loadCurrentUser = async () => {
  try {
    const response = await authApi.me()
    if (response.data.success) {
      currentUser.value = response.data.user
    }
  } catch {
    currentUser.value = null
  }
}

const submitComment = async () => {
  if (!newComment.value.trim() || submitting.value) return
  
  submitting.value = true
  try {
    const response = await postApi.createComment(route.params.id, {
      content: newComment.value.trim()
    })
    
    if (response.data.success) {
      ElMessage.success('留言成功')
      newComment.value = ''
      comments.value = [response.data.comment, ...comments.value]
      commentsCount.value++
    }
  } catch (error) {
    console.error('提交留言失败:', error)
  } finally {
    submitting.value = false
  }
}

const deleteComment = async (comment) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条留言吗？',
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await postApi.deleteComment(route.params.id, comment.id)
    if (response.data.success) {
      ElMessage.success('删除成功')
      comments.value = comments.value.filter(c => c.id !== comment.id)
      commentsCount.value--
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除留言失败:', error)
    }
  }
}

const formatTime = (time) => {
  if (!time) return ''
  return time.replace(' GMT', '')
}

onMounted(() => {
  loadPost()
  loadCurrentUser()
})
</script>

<style scoped>
.post-detail-page {
  flex: 1;
  padding: 40px 0;
  background: var(--color-background);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  color: var(--color-text-secondary);
  cursor: pointer;
  margin-bottom: 24px;
  transition: color var(--transition-fast);
  width: 70%;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.back-link:hover {
  color: var(--color-primary);
}

.post-card {
  padding: 40px;
  width: 70%;
  max-width: 800px;
  margin: 0 auto;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.post-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-badge {
  font-size: 13px;
  font-weight: 500;
  padding: 6px 14px;
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
  gap: 12px;
}

.author-name {
  font-size: 15px;
  color: var(--color-text);
  font-weight: 500;
}

.post-time {
  font-size: 13px;
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

.post-title {
  font-size: 28px;
  font-weight: 600;
  line-height: 1.3;
  margin: 0 0 24px;
  color: var(--color-text);
}

.post-content {
  margin-bottom: 32px;
}

.post-content p {
  font-size: 17px;
  line-height: 1.8;
  color: var(--color-text);
  margin: 0;
  white-space: pre-wrap;
}

.post-images {
  margin-bottom: 32px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.post-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: var(--color-background);
}

.post-footer {
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.permission-info,
.view-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.comments-section {
  margin-top: 24px;
  padding: 32px;
  width: 70%;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.comments-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.comments-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}

.comment-form {
  margin-bottom: 32px;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.user-avatar-small,
.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, #5856d6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.comment-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  outline: none;
  transition: border-color var(--transition-fast);
}

.comment-textarea:focus {
  border-color: var(--color-primary);
}

.comment-textarea::placeholder {
  color: var(--color-text-secondary);
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.char-count {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.login-prompt {
  text-align: center;
  padding: 32px;
  background: var(--color-background);
  border-radius: var(--radius-md);
  margin-bottom: 32px;
}

.login-prompt p {
  margin: 0 0 16px 0;
  color: var(--color-text-secondary);
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.comment-item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.comment-info {
  flex: 1;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.comment-time {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.delete-comment-btn {
  padding: 4px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.delete-comment-btn:hover {
  color: var(--color-danger);
  background: rgba(255, 59, 48, 0.1);
}

.comment-content {
  margin-left: 52px;
}

.comment-content p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text);
  white-space: pre-wrap;
}

.empty-comments,
.loading-comments {
  text-align: center;
  padding: 40px 20px;
}

.empty-comments .empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-comments p {
  margin: 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.loading-state,
.error-state {
  text-align: center;
  padding: 80px 20px;
}

.loading-icon {
  font-size: 32px;
  animation: spin 1s linear infinite;
  color: var(--color-text-secondary);
}

.loading-state p,
.error-desc {
  font-size: 17px;
  color: var(--color-text-secondary);
  margin: 16px 0 0;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.error-title {
  font-size: 21px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--color-text);
}

.error-state .btn-primary {
  display: inline-block;
  margin-top: 24px;
  padding: 12px 32px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: white;
  font-size: 15px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .back-link,
  .post-card,
  .comments-section {
    width: 100%;
    padding: 24px;
  }
  
  .post-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .post-title {
    font-size: 24px;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
  
  .post-image {
    height: 120px;
  }
}
</style>
