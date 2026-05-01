<template>
  <header class="app-header">
    <div class="header-container">
      <router-link to="/" class="logo">
        <span class="logo-icon">📢</span>
        <span class="logo-text">信息发布平台</span>
      </router-link>
      
      <nav class="nav-main">
        <router-link to="/" class="nav-link" active-class="active">首页</router-link>
        <router-link to="/my-posts" class="nav-link" active-class="active" v-if="user">我的发布</router-link>
      </nav>
      
      <div class="nav-actions">
        <button class="theme-toggle-btn" @click="toggleTheme" :title="theme === 'dark' ? '切换到亮色模式' : '切换到暗黑模式'">
          <el-icon v-if="theme === 'dark'"><Sunny /></el-icon>
          <el-icon v-else><Moon /></el-icon>
        </button>
        
        <template v-if="user">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
            <span class="level-badge" :class="user.level">{{ user.level_name }}</span>
              <span class="username">{{ user.username }}</span>
              <el-icon class="caret"><CaretBottom /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="recharge">
                  <el-icon><Wallet /></el-icon>
                  充值
                </el-dropdown-item>
                <el-dropdown-item command="upgrade">
                  <el-icon><TrendCharts /></el-icon>
                  升级会员
                </el-dropdown-item>
                <el-dropdown-item divided command="logout" class="danger">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <router-link to="/login" class="auth-link">登录</router-link>
          <router-link to="/register" class="auth-link register-btn">注册</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CaretBottom, User, Wallet, TrendCharts, SwitchButton, Sunny, Moon } from '@element-plus/icons-vue'
import { useThemeStore } from '../stores/themeStore'

const props = defineProps({
  user: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['logout'])

const router = useRouter()
const { theme, toggleTheme, initTheme } = useThemeStore()

onMounted(() => {
  initTheme()
})

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'recharge':
      router.push('/recharge')
      break
    case 'upgrade':
      router.push('/upgrade')
      break
    case 'logout':
      emit('logout')
      break
  }
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--color-navbar);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--color-border-light);
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--color-text);
  font-weight: 600;
  font-size: 18px;
  letter-spacing: -0.015em;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  background: linear-gradient(135deg, var(--color-text) 0%, #6e6e73 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  padding: 8px 16px;
  font-size: 15px;
  color: var(--color-text-secondary);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-text);
  background: rgba(0, 0, 0, 0.04);
}

.nav-link.active {
  color: var(--color-text);
  font-weight: 500;
}

.nav-link.publish-btn {
  background: var(--color-primary);
  color: white;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-weight: 500;
}

.nav-link.publish-btn:hover {
  background: var(--color-primary-hover);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  font-size: 18px;
}

.theme-toggle-btn:hover {
  color: var(--color-text);
  background: rgba(0, 0, 0, 0.04);
}

html.dark .theme-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.auth-link {
  padding: 8px 16px;
  font-size: 15px;
  color: var(--color-text-secondary);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.auth-link:hover {
  color: var(--color-text);
  background: rgba(0, 0, 0, 0.04);
}

.auth-link.register-btn {
  background: var(--color-primary);
  color: white;
  font-weight: 500;
}

.auth-link.register-btn:hover {
  background: var(--color-primary-hover);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.user-info:hover {
  background: rgba(0, 0, 0, 0.04);
}

.username {
  font-size: 15px;
  color: var(--color-text);
  font-weight: 500;
}

.caret {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.level-badge {
  font-size: 12px;
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

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
}

:deep(.el-dropdown-menu__item.danger) {
  color: var(--color-danger);
}
</style>
