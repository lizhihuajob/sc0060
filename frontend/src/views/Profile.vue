<template>
  <div class="profile-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">个人中心</h1>
      </div>

      <div class="profile-grid" v-if="user">
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
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Wallet, TrendCharts, Plus, Minus, Camera } from '@element-plus/icons-vue'
import { userApi } from '../services/api'

const user = ref(null)
const transactions = ref([])
const avatarInput = ref(null)
const uploadingAvatar = ref(false)
const changingPassword = ref(false)

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

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  flex: 1;
  padding: 40px 0;
  background: var(--color-background);
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.003em;
  margin: 0;
  color: var(--color-text);
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
  color: var(--color-text-secondary);
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
}
</style>
