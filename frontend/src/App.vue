<template>
  <div class="app-wrapper">
    <AppHeader :user="user" @logout="handleLogout" />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import { useUserStore } from './stores/userStore'

const router = useRouter()
const { user, fetchUser, clearUser } = useUserStore()

const handleLogout = async () => {
  try {
    await fetchUser()
    clearUser()
    ElMessage.success('已退出登录')
    router.push('/')
  } catch (error) {
    ElMessage.error('退出失败')
  }
}

const handleAuthLogout = () => {
  clearUser()
  ElMessage.warning('请先登录')
  router.push('/login')
}

onMounted(() => {
  fetchUser()
  window.addEventListener('auth:logout', handleAuthLogout)
})

onUnmounted(() => {
  window.removeEventListener('auth:logout', handleAuthLogout)
})
</script>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
