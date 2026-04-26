<template>
  <div class="recharge-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">账户充值</h1>
        <div class="current-balance">
          <span class="balance-label">当前余额</span>
          <span class="balance-value">¥{{ user?.balance || 0 }}</span>
        </div>
      </div>

      <div class="content-grid">
        <div class="form-card card">
          <h3 class="section-title">选择充值金额</h3>
          
          <div class="amount-options">
            <div 
              v-for="amount in amountOptions" 
              :key="amount"
              class="amount-option"
              :class="{ active: selectedAmount === amount }"
              @click="selectedAmount = amount"
            >
              <span class="amount-value">¥{{ amount }}</span>
            </div>
            <div class="amount-option custom-option" :class="{ active: isCustomAmount }">
              <el-input 
                v-model="customAmount" 
                type="number" 
                placeholder="自定义金额"
                :min="1"
                @focus="isCustomAmount = true; selectedAmount = null"
                class="custom-input"
              />
            </div>
          </div>

          <el-form-item class="form-item">
            <el-button 
              type="primary" 
              size="large" 
              class="submit-btn"
              :loading="loading"
              @click="handleRecharge"
              :disabled="!currentAmount"
            >
              立即充值
            </el-button>
          </el-form-item>
        </div>

        <div class="info-card card">
          <h3 class="section-title">充值说明</h3>
          <div class="info-list">
            <div class="info-item">
              <el-icon class="info-icon"><Coin /></el-icon>
              <div class="info-content">
                <h4 class="info-title">余额用途</h4>
                <p class="info-desc">充值余额可用于升级会员等级，解锁更多发布权限</p>
              </div>
            </div>
            <div class="info-item">
              <el-icon class="info-icon"><Lock /></el-icon>
              <div class="info-content">
                <h4 class="info-title">安全支付</h4>
                <p class="info-desc">当前为演示模式，充值后余额将直接到账</p>
              </div>
            </div>
            <div class="info-item">
              <el-icon class="info-icon"><Clock /></el-icon>
              <div class="info-content">
                <h4 class="info-title">即时到账</h4>
                <p class="info-desc">充值成功后，余额立即更新，可在个人中心查看</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Coin, Lock, Clock } from '@element-plus/icons-vue'
import { userApi } from '../services/api'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const { user } = useUserStore()

const loading = ref(false)
const selectedAmount = ref(null)
const customAmount = ref('')
const isCustomAmount = ref(false)

const amountOptions = [10, 30, 50, 100, 200, 500]

const currentAmount = computed(() => {
  if (isCustomAmount.value && customAmount.value) {
    const amount = parseFloat(customAmount.value)
    return amount > 0 ? amount : null
  }
  return selectedAmount.value
})

const handleRecharge = async () => {
  if (!currentAmount.value) return
  
  loading.value = true
  try {
    const response = await userApi.recharge(currentAmount.value)
    if (response.data.success) {
      ElMessage.success(response.data.message)
      customAmount.value = ''
      selectedAmount.value = null
      isCustomAmount.value = false
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '充值失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.recharge-page {
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

.current-balance {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.balance-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.balance-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-primary);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.form-card,
.info-card {
  padding: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 24px;
  color: var(--color-text);
}

.amount-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 32px;
}

.amount-option {
  padding: 20px 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.amount-option:hover {
  border-color: var(--color-primary);
  background: rgba(0, 113, 227, 0.02);
}

.amount-option.active {
  border-color: var(--color-primary);
  background: rgba(0, 113, 227, 0.08);
}

.amount-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.amount-option.active .amount-value {
  color: var(--color-primary);
}

.custom-option {
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-option.active {
  background: white;
}

.custom-input {
  width: 100%;
}

:deep(.custom-input .el-input__wrapper) {
  border-radius: calc(var(--radius-md) - 2px);
  box-shadow: none;
  padding: 16px 12px;
}

:deep(.custom-input .el-input__inner) {
  text-align: center;
  font-size: 16px;
  font-weight: 600;
}

.submit-btn {
  width: 100%;
  border-radius: var(--radius-md);
  padding: 14px;
  font-size: 17px;
  font-weight: 500;
}

.form-item {
  margin-bottom: 0;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-item {
  display: flex;
  gap: 16px;
}

.info-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.info-content {
  flex: 1;
}

.info-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--color-text);
}

.info-desc {
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .amount-options {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
