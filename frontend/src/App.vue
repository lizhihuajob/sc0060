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
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from './components/AppHeader.vue'
import { useUserStore } from './stores/userStore'
import { authApi } from './services/api'

const router = useRouter()
const { user, fetchUser, clearUser } = useUserStore()

const handleLogout = async () => {
  try {
    await authApi.logout()
    clearUser()
    ElMessage.success('已退出登录')
    router.push('/')
  } catch (error) {
    ElMessage.error('退出失败')
  }
}

onMounted(() => {
  fetchUser()
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
