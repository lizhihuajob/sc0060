<template>
  <div class="profile-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">个人中心</h1>
      </div>

      <div class="profile-grid" v-if="user">
        <div class="profile-card card">
          <div class="profile-header">
            <div class="avatar-placeholder">
              <el-icon><User /></el-icon>
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
import { ref, onMounted } from 'vue'
import { User, Wallet, TrendCharts, Plus, Minus } from '@element-plus/icons-vue'
import { userApi } from '../services/api'

const user = ref(null)
const transactions = ref([])

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

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, #5856d6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 36px;
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
