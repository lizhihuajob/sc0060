<template>
  <div class="profile-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">个人中心</h1>
      </div>

      <div class="tab-nav">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'profile' }"
          @click="activeTab = 'profile'"
        >
          账户信息
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'favorites' }"
          @click="activeTab = 'favorites'"
        >
          我的收藏
        </button>
      </div>

      <div class="profile-grid" v-if="user" v-show="activeTab === 'profile'">
        <div class="profile-card card">
          <div class="profile-header">
            <div class="avatar-wrapper" @click="triggerAvatarUpload">
              <div class="avatar-display">
                <img v-if="user.avatar" :src="`/uploads/${user.avatar}`" alt="头像" class="avatar-img" />
                <el-icon v-else><User /></el-icon>
              </div>
              <div class="avatar-overlay">
                <el-icon><Camera /></el-icon>
                <span>更换头像</span>
              </div>
              <input 
                type="file" 
                ref="avatarInput" 
                @change="handleAvatarChange" 
                accept="image/*"
                style="display: none"
              />
            </div>
            <div class="profile-info">
              <h2 class="username">{{ user.username }}</h2>
              <span class="level-badge" :class="user.level">{{ user.level_name }}</span>
            </div>
          </div>

          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ user.posts_count }}</div>
              <div class="stat-label">已发布</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ user.posts_limit - user.posts_count }}</div>
              <div class="stat-label">剩余额度</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">¥{{ user.balance }}</div>
              <div class="stat-label">账户余额</div>
            </div>
          </div>

          <div class="info-section">
            <h3 class="section-title">账户信息</h3>
            <div class="info-list">
              <div class="info-item">
                <span class="info-label">用户名</span>
                <span class="info-value">{{ user.username }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">邮箱</span>
                <span class="info-value">{{ user.email || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">会员等级</span>
                <span class="info-value">{{ user.level_name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">注册时间</span>
                <span class="info-value">{{ user.created_at }}</span>
              </div>
            </div>
          </div>

          <div class="password-section">
            <h3 class="section-title">修改密码</h3>
            <form class="password-form" @submit.prevent="changePassword">
              <div class="form-group">
                <label class="form-label">原密码</label>
                <input 
                  type="password" 
                  v-model="passwordForm.oldPassword" 
                  class="form-input"
                  placeholder="请输入原密码"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">新密码</label>
                <input 
                  type="password" 
                  v-model="passwordForm.newPassword" 
                  class="form-input"
                  placeholder="请输入新密码（至少6位）"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">确认新密码</label>
                <input 
                  type="password" 
                  v-model="passwordForm.confirmPassword" 
                  class="form-input"
                  placeholder="请再次输入新密码"
                  required
                />
              </div>
              <button type="submit" class="btn-primary" :disabled="changingPassword">
                <span v-if="!changingPassword">确认修改</span>
                <span v-else>修改中...</span>
              </button>
            </form>
          </div>

          <div class="action-buttons">
            <router-link to="/recharge" class="btn-primary">
              <el-icon><Wallet /></el-icon>
              充值
            </router-link>
            <router-link to="/upgrade" class="btn-secondary">
              <el-icon><TrendCharts /></el-icon>
              升级会员
            </router-link>
          </div>
        </div>

        <div class="transactions-card card" v-if="transactions.length > 0">
          <h3 class="section-title">交易记录</h3>
          <div class="transactions-list">
            <div 
              v-for="tx in transactions" 
              :key="tx.id"
              class="transaction-item"
            >
              <div class="tx-info">
                <div class="tx-type" :class="tx.transaction_type">
                  <el-icon v-if="tx.transaction_type === 'recharge'"><Plus /></el-icon>
                  <el-icon v-else><Minus /></el-icon>
                </div>
                <div class="tx-content">
                  <div class="tx-description">{{ tx.description }}</div>
                  <div class="tx-time">{{ tx.created_at }}</div>
                </div>
              </div>
              <div class="tx-amount" :class="tx.transaction_type">
                {{ tx.transaction_type === 'recharge' ? '+' : '' }}¥{{ tx.amount }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="favorites-section" v-show="activeTab === 'favorites'">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon><Star /></el-icon>
            我的收藏
          </h3>
        </div>

        <div class="posts-list" v-if="favorites.length > 0">
          <div 
            v-for="post in favorites" 
            :key="post.id" 
            class="post-item card"
            @click="goToPost(post.id)"
          >
            <div class="post-main">
              <div class="post-header-row">
                <h3 class="post-title">{{ post.title }}</h3>
                <span 
                  class="favorite-btn favorited" 
                  @click.stop="unfavorite(post)"
                  title="取消收藏"
                >
                  <el-icon><Star /></el-icon>
                </span>
              </div>
              <p class="post-excerpt">{{ truncate(post.content, 120) }}</p>
              
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

            <div class="post-footer-row">
              <div class="post-meta-left">
                <span class="author-name">{{ post.author?.username }}</span>
                <span class="stat-item">
                  <el-icon><View /></el-icon>
                  {{ post.views_count }}
                </span>
              </div>
              <span class="post-time">{{ formatTime(post.favorited_at || post.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="empty-state" v-else-if="!loadingFavorites">
          <div class="empty-icon">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" stroke="#86868b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3 class="empty-title">暂无收藏</h3>
          <p class="empty-desc">
            去首页发现感兴趣的公告，点击星星图标即可收藏
          </p>
          <router-link to="/" class="btn-primary">
            <el-icon><ArrowRight /></el-icon>
            去首页
          </router-link>
        </div>

        <div class="loading-state" v-else>
          <div class="loading-spinner">
            <div class="spinner-circle"></div>
          </div>
          <p>加载中...</p>
        </div>

        <div class="load-more" v-if="hasMoreFavorites && !loadingFavorites">
          <button class="load-more-btn" @click="loadMoreFavorites" :disabled="loadingFavorites">
            <span v-if="!loadingFavorites">加载更多</span>
            <span v-else>加载中...</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Wallet, TrendCharts, Plus, Minus, Camera, Star, View, ArrowDown, ArrowRight } from '@element-plus/icons-vue'
import { userApi, postApi } from '../services/api'

const router = useRouter()

const activeTab = ref('profile')
const user = ref(null)
const transactions = ref([])
const avatarInput = ref(null)
const uploadingAvatar = ref(false)
const changingPassword = ref(false)

const favorites = ref([])
const loadingFavorites = ref(false)
const favoritesPage = ref(1)
const hasMoreFavorites = ref(true)

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const loadProfile = async () => {
  try {
    const response = await userApi.getProfile()
    if (response.data.success) {
      user.value = response.data.user
      transactions.value = response.data.transactions
    }
  } catch (error) {
    console.error('加载个人信息失败:', error)
  }
}

const loadFavorites = async (append = false) => {
  if (loadingFavorites.value) return
  loadingFavorites.value = true
  
  try {
    const response = await userApi.getFavorites({
      page: favoritesPage.value,
      per_page: 20
    })
    
    if (response.data.success) {
      const newPosts = response.data.posts
      if (append) {
        favorites.value = [...favorites.value, ...newPosts]
      } else {
        favorites.value = newPosts
      }
      hasMoreFavorites.value = response.data.has_more
    }
  } catch (error) {
    console.error('加载收藏失败:', error)
  } finally {
    loadingFavorites.value = false
  }
}

const loadMoreFavorites = () => {
  favoritesPage.value++
  loadFavorites(true)
}

const unfavorite = async (post) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消收藏这条公告吗？',
      '确认取消',
      {
        confirmButtonText: '确定取消',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await postApi.toggleFavorite(post.id)
    if (response.data.success) {
      ElMessage.success('已取消收藏')
      favorites.value = favorites.value.filter(p => p.id !== post.id)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消收藏失败:', error)
    }
  }
}

const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}

const handleAvatarChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 JPG、PNG、GIF 格式的图片')
    return
  }
  
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }
  
  uploadingAvatar.value = true
  try {
    const formData = new FormData()
    formData.append('avatar', file)
    
    const response = await userApi.uploadAvatar(formData)
    if (response.data.success) {
      ElMessage.success('头像上传成功')
      user.value = response.data.user
    }
  } catch (error) {
    console.error('上传头像失败:', error)
  } finally {
    uploadingAvatar.value = false
    if (avatarInput.value) {
      avatarInput.value.value = ''
    }
  }
}

const changePassword = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    ElMessage.warning('请填写所有字段')
    return
  }
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  
  if (passwordForm.newPassword.length < 6) {
    ElMessage.warning('新密码长度不能少于6位')
    return
  }
  
  changingPassword.value = true
  try {
    const response = await userApi.changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword,
      confirm_password: passwordForm.confirmPassword
    })
    
    if (response.data.success) {
      ElMessage.success('密码修改成功')
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    changingPassword.value = false
  }
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
  loadProfile()
  loadFavorites()
})
</script>

<style scoped>
.profile-page {
  flex: 1;
  padding: 40px 0;
  background: var(--color-background);
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.003em;
  margin: 0;
  color: var(--color-text);
}

.tab-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  padding: 4px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: var(--radius-md);
  width: fit-content;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  color: var(--color-text);
}

.tab-btn.active {
  background: white;
  color: var(--color-text);
  font-weight: var(--font-weight-medium);
  box-shadow: var(--shadow-sm);
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.profile-card {
  padding: 32px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.avatar-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  cursor: pointer;
}

.avatar-display {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, #5856d6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 36px;
  overflow: hidden;
}

.avatar-display .avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.avatar-overlay span {
  font-size: 12px;
  margin-top: 4px;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.profile-info {
  flex: 1;
}

.username {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--color-text);
}

.level-badge {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 20px;
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
  background: var(--gradient-gold);
  color: #1d1d1f;
}

.level-badge.black {
  background: var(--gradient-dark);
  color: white;
}

.level-badge.diamond {
  background: linear-gradient(135deg, #b9f2ff 0%, #64d2ff 100%);
  color: #1d1d1f;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  margin: 0 0 16px;
  color: var(--color-text);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 15px;
  color: var(--color-text-secondary);
}

.info-value {
  font-size: 15px;
  color: var(--color-text);
  font-weight: 500;
}

.password-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.form-input {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  outline: none;
  transition: border-color var(--transition-fast);
}

.form-input:focus {
  border-color: var(--color-primary);
}

.form-input::placeholder {
  color: var(--color-text-tertiary);
}

.password-form .btn-primary {
  align-self: flex-start;
  padding: 12px 32px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.password-form .btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.action-buttons .btn-primary,
.action-buttons .btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: center;
  padding: 12px 24px;
  border-radius: var(--radius-md);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
}

.action-buttons .btn-primary {
  background: var(--color-primary);
  color: white;
}

.action-buttons .btn-primary:hover {
  background: var(--color-primary-hover);
}

.action-buttons .btn-secondary {
  background: rgba(0, 0, 0, 0.04);
  color: var(--color-text);
}

.action-buttons .btn-secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}

.transactions-card {
  padding: 32px;
}

.transactions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.transaction-item:last-child {
  border-bottom: none;
}

.tx-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tx-type {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.tx-type.recharge {
  background: rgba(52, 199, 89, 0.1);
  color: var(--color-success);
}

.tx-type.upgrade {
  background: rgba(255, 59, 48, 0.1);
  color: var(--color-danger);
}

.tx-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tx-description {
  font-size: 15px;
  color: var(--color-text);
}

.tx-time {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.tx-amount {
  font-size: 17px;
  font-weight: 600;
}

.tx-amount.recharge {
  color: var(--color-success);
}

.tx-amount.upgrade {
  color: var(--color-danger);
}

.favorites-section {
  width: 100%;
}

.favorites-section .section-header {
  margin-bottom: 24px;
}

.favorites-section .section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-xl);
}

.favorites-section .section-title .el-icon {
  color: var(--color-danger);
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-item {
  width: 100%;
  padding: 20px 24px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.post-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary);
}

.post-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.post-title {
  flex: 1;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  line-height: 1.4;
  margin: 0;
  color: var(--color-text);
  transition: color var(--transition-fast);
}

.post-item:hover .post-title {
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
  margin-top: 8px;
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

.post-footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-light);
}

.post-meta-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.author-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.post-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.favorite-btn {
  cursor: pointer;
  transition: all var(--transition-fast);
  padding: 4px;
  border-radius: var(--radius-sm);
  color: var(--color-text-tertiary);
}

.favorite-btn:hover {
  background: rgba(255, 59, 48, 0.1);
  color: var(--color-danger);
}

.favorite-btn.favorited {
  color: var(--color-danger);
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

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .post-item {
    padding: 16px;
  }
  
  .post-header-row {
    flex-direction: column;
    gap: 8px;
  }
  
  .post-footer-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .post-meta-left {
    width: 100%;
    justify-content: space-between;
  }
  
  .load-more-btn {
    width: 100%;
  }
}
</style>
