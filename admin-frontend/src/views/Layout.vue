<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="admin-sidebar-header">
        <div class="admin-logo">
          <el-icon class="logo-icon"><Setting /></el-icon>
          <span>后台管理</span>
        </div>
      </div>
      <nav class="admin-menu">
        <router-link to="/dashboard" class="admin-menu-item">
          <el-icon class="menu-icon"><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </router-link>
        <router-link to="/users" class="admin-menu-item">
          <el-icon class="menu-icon"><User /></el-icon>
          <span>用户管理</span>
        </router-link>
        <router-link to="/posts" class="admin-menu-item">
          <el-icon class="menu-icon"><Document /></el-icon>
          <span>内容管理</span>
        </router-link>
        <router-link to="/tags" class="admin-menu-item">
          <el-icon class="menu-icon"><Collection /></el-icon>
          <span>标签管理</span>
        </router-link>
        <router-link to="/settings" class="admin-menu-item">
          <el-icon class="menu-icon"><Tools /></el-icon>
          <span>系统设置</span>
        </router-link>
      </nav>
    </aside>
    
    <main class="admin-main">
      <header class="admin-header">
        <div class="admin-header-right">
          <div class="admin-user-info">
            <div class="admin-avatar">{{ adminInitial }}</div>
            <span class="admin-username">{{ admin?.username || '管理员' }}</span>
          </div>
          <el-button type="text" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </header>
      
      <div class="admin-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Setting, DataAnalysis, User, Document, Collection, Tools, SwitchButton 
} from '@element-plus/icons-vue'
import { adminApi } from '../services/api'

const router = useRouter()
const admin = ref(null)

const adminInitial = computed(() => {
  if (admin.value?.username) {
    return admin.value.username.charAt(0).toUpperCase()
  }
  return 'A'
})

const loadAdminInfo = async () => {
  try {
    const response = await adminApi.getMe()
    if (response.data.success) {
      admin.value = response.data.admin
      localStorage.setItem('admin', JSON.stringify(response.data.admin))
    }
  } catch (error) {
    console.error('获取管理员信息失败:', error)
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '确认退出',
      {
        confirmButtonText: '确定退出',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await adminApi.logout()
    localStorage.removeItem('admin_auth')
    localStorage.removeItem('admin')
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    if (error !== 'cancel') {
      localStorage.removeItem('admin_auth')
      localStorage.removeItem('admin')
      router.push('/login')
    }
  }
}

onMounted(() => {
  const savedAdmin = localStorage.getItem('admin')
  if (savedAdmin) {
    admin.value = JSON.parse(savedAdmin)
  }
  loadAdminInfo()
})
</script>
