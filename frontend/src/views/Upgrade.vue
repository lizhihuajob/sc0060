<template>
  <div class="upgrade-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">升级会员</h1>
        <div class="current-status">
          <span class="status-label">当前等级</span>
          <span class="level-badge" :class="user?.level">{{ user?.level_name }}</span>
        </div>
      </div>

      <div class="level-cards">
        <div 
          v-for="(level, key) in userLevels" 
          :key="key"
          class="level-card card"
          :class="{ 
            'current': key === user?.level,
            'available': isAvailable(key),
            'locked': isLocked(key)
          }"
        >
          <div class="level-header">
            <span class="level-name">{{ level.name }}</span>
            <span class="level-tag" v-if="key === user?.level">当前</span>
            <span class="level-tag locked-tag" v-else-if="isLocked(key)">锁定</span>
          </div>

          <div class="level-price">
            <template v-if="level.price === 0">
              <span class="free">免费</span>
            </template>
            <template v-else>
              <span class="price-symbol">¥</span>
              <span class="price-value">{{ level.price }}</span>
            </template>
          </div>

          <div class="level-benefits">
            <div class="benefit-item">
              <el-icon><Check /></el-icon>
              <span>发布额度：{{ level.posts_limit }} 条</span>
            </div>
            <div class="benefit-item">
              <el-icon><Check /></el-icon>
              <span>查看权限：白银及以上可见</span>
            </div>
            <div class="benefit-item" v-if="key !== 'bronze'">
              <el-icon><Check /></el-icon>
              <span>解锁更多高级功能</span>
            </div>
          </div>

          <div class="level-action">
            <template v-if="key === user?.level">
              <el-button type="primary" size="large" disabled class="action-btn">
                当前等级
              </el-button>
            </template>
            <template v-else-if="isAvailable(key)">
              <el-button 
                type="primary" 
                size="large" 
                class="action-btn upgrade-btn"
                :loading="loadingLevel === key"
                @click="handleUpgrade(key, level)"
              >
                立即升级
              </el-button>
            </template>
            <template v-else>
              <el-button size="large" disabled class="action-btn">
                需依次升级
              </el-button>
            </template>
          </div>
        </div>
      </div>

      <div class="info-card card">
        <h3 class="section-title">升级说明</h3>
        <div class="info-grid">
          <div class="info-item">
            <div class="info-icon-wrap">
              <el-icon class="info-icon"><TrendCharts /></el-icon>
            </div>
            <h4 class="info-title">依次升级</h4>
            <p class="info-desc">会员等级需要依次升级，不可越级。请先升级到下一等级</p>
          </div>
          <div class="info-item">
            <div class="info-icon-wrap">
              <el-icon class="info-icon"><Document /></el-icon>
            </div>
            <h4 class="info-title">发布额度</h4>
            <p class="info-desc">会员等级越高，每月可发布的信息数量越多，曝光机会更大</p>
          </div>
          <div class="info-item">
            <div class="info-icon-wrap">
              <el-icon class="info-icon"><View /></el-icon>
            </div>
            <h4 class="info-title">查看权限</h4>
            <p class="info-desc">高等级会员可查看更多限定信息，获取更多优质内容</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, TrendCharts, Document, View } from '@element-plus/icons-vue'
import { userApi, configApi } from '../services/api'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const { user } = useUserStore()

const userLevels = ref({})
const loadingLevel = ref(null)

const levelOrder = computed(() => ['bronze', 'silver', 'gold', 'black', 'diamond'])

const loadConfig = async () => {
  try {
    const response = await configApi.getMembership()
    if (response.data.success) {
      userLevels.value = response.data.user_levels
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

const isAvailable = (levelKey) => {
  if (!user.value) return false
  const userIndex = levelOrder.value.indexOf(user.value.level)
  const targetIndex = levelOrder.value.indexOf(levelKey)
  return targetIndex === userIndex + 1
}

const isLocked = (levelKey) => {
  if (!user.value) return false
  const userIndex = levelOrder.value.indexOf(user.value.level)
  const targetIndex = levelOrder.value.indexOf(levelKey)
  return targetIndex > userIndex + 1
}

const handleUpgrade = async (levelKey, level) => {
  if (!user.value) return
  
  if (user.value.balance < level.price) {
    ElMessageBox.confirm(
      `余额不足，升级${level.name}需要 ¥${level.price}，当前余额 ¥${user.value.balance}。是否前往充值？`,
      '余额不足',
      {
        confirmButtonText: '前往充值',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      router.push('/recharge')
    }).catch(() => {})
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要花费 ¥${level.price} 升级到${level.name}吗？`,
      '确认升级',
      {
        confirmButtonText: '确定升级',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
  } catch {
    return
  }
  
  loadingLevel.value = levelKey
  try {
    const response = await userApi.upgrade(levelKey)
    if (response.data.success) {
      ElMessage.success(response.data.message)
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '升级失败')
  } finally {
    loadingLevel.value = null
  }
}

loadConfig()
</script>

<style scoped>
.upgrade-page {
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

.current-status {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.status-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.level-badge {
  font-size: 15px;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
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

.level-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.level-card {
  padding: 24px;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.level-card.current {
  border: 2px solid var(--color-primary);
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.02) 0%, rgba(88, 86, 214, 0.02) 100%);
}

.level-card.available {
  cursor: pointer;
}

.level-card.available:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.level-card.locked {
  opacity: 0.6;
}

.level-card.locked::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.5);
  pointer-events: none;
}

.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.level-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.level-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-primary);
  font-weight: 500;
}

.level-tag.locked-tag {
  background: rgba(134, 134, 139, 0.1);
  color: var(--color-secondary);
}

.level-price {
  margin-bottom: 20px;
}

.free {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-success);
}

.price-symbol {
  font-size: 16px;
  color: var(--color-text);
  font-weight: 500;
}

.price-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text);
}

.level-benefits {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 24px;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.benefit-item .el-icon {
  color: var(--color-success);
  font-size: 14px;
}

.level-action {
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.action-btn {
  width: 100%;
  border-radius: var(--radius-md);
}

.upgrade-btn {
  background: var(--color-primary);
  border: none;
}

.upgrade-btn:hover {
  background: var(--color-primary-hover);
}

.info-card {
  padding: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 24px;
  color: var(--color-text);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.info-item {
  text-align: center;
}

.info-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(0, 113, 227, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.info-icon {
  font-size: 24px;
  color: var(--color-primary);
}

.info-item h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--color-text);
}

.info-item p {
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .level-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .level-cards {
    grid-template-columns: 1fr;
  }
}
</style>
