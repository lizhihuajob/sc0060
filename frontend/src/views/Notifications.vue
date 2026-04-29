<template>
  <div class="notifications-page">
    <div class="page-container">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">通知消息</h1>
          <span class="unread-info" v-if="unreadCount > 0">
            {{ unreadCount }} 条未读
          </span>
        </div>
        <div class="header-right">
          <button 
            class="action-btn" 
            @click="markAllRead" 
            :disabled="unreadCount === 0"
          >
            <el-icon><Check /></el-icon>
            全部已读
          </button>
        </div>
      </div>

      <div class="notifications-list" v-if="notifications.length > 0">
        <div 
          v-for="notification in notifications" 
          :key="notification.id" 
          class="notification-item"
          :class="{ unread: !notification.is_read }"
          @click="handleNotificationClick(notification)"
        >
          <div class="notification-icon" :class="notification.type">
            <el-icon>
              <UserFilled v-if="notification.type === 'follow'" />
              <Promotion v-else-if="notification.type === 'pin' || notification.type === 'pin_expiring'" />
              <Bell v-else-if="notification.type === 'membership_expiring'" />
              <Document v-else />
            </el-icon>
          </div>
          <div class="notification-content">
            <div class="notification-title">
              {{ notification.title }}
              <span class="unread-dot" v-if="!notification.is_read"></span>
            </div>
            <p class="notification-text">{{ notification.content }}</p>
            <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
          </div>
          <div class="notification-action" v-if="!notification.is_read">
            <button class="read-btn" @click.stop="markAsRead(notification)">
              标记已读
            </button>
          </div>
        </div>
      </div>

      <div class="empty-state" v-else-if="!loading">
        <div class="empty-icon">
          <el-icon><Bell /></el-icon>
        </div>
        <h3 class="empty-title">暂无通知</h3>
        <p class="empty-desc">当有人关注您、点赞您的公告或您关注的用户发布新公告时，您会收到通知</p>
      </div>

      <div class="loading-state" v-else>
        <el-icon class="loading-icon"><Loading /></el-icon>
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Bell, UserFilled, Promotion, Document, Check, Loading } from '@element-plus/icons-vue'
import { notificationApi } from '../services/api'

const router = useRouter()

const notifications = ref([])
const unreadCount = ref(0)
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

const loadNotifications = async (append = false) => {
  if (loading.value) return
  loading.value = true
  
  try {
    const params = {
      page: page.value,
      per_page: 20
    }
    
    const response = await notificationApi.getList(params)
    if (response.data.success) {
      const newNotifications = response.data.notifications
      if (append) {
        notifications.value = [...notifications.value, ...newNotifications]
      } else {
        notifications.value = newNotifications
      }
      unreadCount.value = response.data.unread_count || 0
      hasMore.value = response.data.has_more
    }
  } catch (error) {
    console.error('加载通知失败:', error)
  } finally {
    loading.value = false
  }
}

const markAsRead = async (notification) => {
  try {
    const response = await notificationApi.markAsRead(notification.id)
    if (response.data.success) {
      notification.is_read = 1
      unreadCount.value--
      ElMessage.success('已标记为已读')
    }
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

const markAllRead = async () => {
  try {
    const response = await notificationApi.markAllAsRead()
    if (response.data.success) {
      notifications.value.forEach(n => {
        n.is_read = 1
      })
      unreadCount.value = 0
      ElMessage.success('全部已标记为已读')
    }
  } catch (error) {
    console.error('标记全部已读失败:', error)
  }
}

const handleNotificationClick = (notification) => {
  if (!notification.is_read) {
    markAsRead(notification)
  }
  
  const data = notification.data
  if (data && data.post_id) {
    router.push(`/post/${data.post_id}`)
  } else if (data && data.follower_id) {
    ElMessage.info('点击用户关注通知')
  }
}

const loadMore = () => {
  page.value++
  loadNotifications(true)
}

const formatTime = (time) => {
  if (!time) return ''
  return time.replace(' GMT', '')
}

onMounted(() => {
  loadNotifications()
})
</script>

<style scoped>
.notifications-page {
  flex: 1;
  padding: 40px 0;
  background: var(--color-background);
}

.page-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}

.unread-info {
  font-size: 14px;
  color: var(--color-danger);
  background: rgba(255, 59, 48, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 500;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--color-border-light);
  background: white;
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.notification-item:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.notification-item.unread {
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.03) 0%, white 100%);
  border-left: 3px solid var(--color-primary);
}

.notification-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 20px;
  flex-shrink: 0;
}

.notification-icon.follow {
  background: rgba(88, 86, 214, 0.1);
  color: #5856d6;
}

.notification-icon.pin,
.notification-icon.pin_expiring {
  background: rgba(255, 149, 0, 0.1);
  color: var(--color-warning);
}

.notification-icon.membership_expiring {
  background: rgba(255, 59, 48, 0.1);
  color: var(--color-danger);
}

.notification-icon.new_post {
  background: rgba(0, 122, 255, 0.1);
  color: var(--color-primary);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 4px;
}

.unread-dot {
  width: 6px;
  height: 6px;
  background: var(--color-danger);
  border-radius: 50%;
  flex-shrink: 0;
}

.notification-text {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0 0 8px;
  line-height: 1.5;
}

.notification-time {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.notification-action {
  flex-shrink: 0;
}

.read-btn {
  padding: 6px 12px;
  border: 1px solid var(--color-border-light);
  background: white;
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.read-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-state .empty-icon {
  font-size: 48px;
  color: var(--color-text-tertiary);
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--color-text);
}

.empty-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.loading-icon {
  font-size: 32px;
  animation: spin 1s linear infinite;
  color: var(--color-text-secondary);
}

.loading-state p {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 16px 0 0;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.load-more {
  text-align: center;
  margin-top: 32px;
}

.load-more-btn {
  padding: 12px 32px;
  border: 1px solid var(--color-border);
  background: white;
  border-radius: var(--radius-lg);
  font-size: 14px;
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.load-more-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .notifications-page {
    padding: 24px 0;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .notification-item {
    padding: 12px;
  }
  
  .notification-icon {
    width: 40px;
    height: 40px;
    font-size: 18px;
  }
}
</style>
