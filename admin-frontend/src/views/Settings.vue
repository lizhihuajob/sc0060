<template>
  <div class="settings-page">
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-subtitle">管理管理员账户和系统配置</p>
    </div>
    
    <div class="content-grid">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <el-icon><User /></el-icon>
            个人信息
          </h3>
        </div>
        
        <el-form
          ref="profileFormRef"
          :model="profileForm"
          :rules="profileRules"
          label-width="120px"
          style="max-width: 500px;"
        >
          <el-form-item label="用户名">
            <el-input :value="admin?.username" disabled />
          </el-form-item>
          <el-form-item label="角色">
            <el-input :value="getRoleName(admin?.role)" disabled />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="profileLoading" @click="updateProfile">
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <el-icon><Lock /></el-icon>
            修改密码
          </h3>
        </div>
        
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="120px"
          style="max-width: 500px;"
        >
          <el-form-item label="原密码" prop="oldPassword">
            <el-input 
              v-model="passwordForm.oldPassword" 
              type="password" 
              placeholder="请输入原密码"
              show-password
            />
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input 
              v-model="passwordForm.newPassword" 
              type="password" 
              placeholder="请输入新密码（至少6位）"
              show-password
            />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input 
              v-model="passwordForm.confirmPassword" 
              type="password" 
              placeholder="请再次输入新密码"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="passwordLoading" @click="changePassword">
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            <el-icon><InfoFilled /></el-icon>
            系统信息
          </h3>
        </div>
        
        <el-descriptions :column="1" border>
          <el-descriptions-item label="后台版本">
            <span>1.0.0</span>
          </el-descriptions-item>
          <el-descriptions-item label="API 地址">
            <span>/api/admin</span>
          </el-descriptions-item>
          <el-descriptions-item label="最后登录时间">
            <span>{{ formatTime(admin?.last_login_at) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="默认管理员账号">
            <span>admin / admin123</span>
            <el-tag type="warning" size="small" style="margin-left: 8px;">首次登录后请修改密码</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock, InfoFilled } from '@element-plus/icons-vue'
import { adminApi } from '../services/api'

const profileFormRef = ref(null)
const passwordFormRef = ref(null)
const admin = ref(null)
const profileLoading = ref(false)
const passwordLoading = ref(false)

const profileForm = reactive({
  email: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const profileRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const getRoleName = (role) => {
  const roles = {
    super_admin: '超级管理员',
    admin: '管理员'
  }
  return roles[role] || role
}

const formatTime = (time) => {
  if (!time) return '-'
  return time.replace(' GMT', '')
}

const loadAdminInfo = async () => {
  try {
    const response = await adminApi.getMe()
    if (response.data.success) {
      admin.value = response.data.admin
      profileForm.email = admin.value.email || ''
    }
  } catch (error) {
    console.error('获取管理员信息失败:', error)
  }
}

const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      profileLoading.value = true
      try {
        const response = await adminApi.updateProfile({
          email: profileForm.email || null
        })
        if (response.data.success) {
          ElMessage.success('更新成功')
          loadAdminInfo()
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '更新失败')
      } finally {
        profileLoading.value = false
      }
    }
  })
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      passwordLoading.value = true
      try {
        const response = await adminApi.changePassword({
          old_password: passwordForm.oldPassword,
          new_password: passwordForm.newPassword,
          confirm_password: passwordForm.confirmPassword
        })
        if (response.data.success) {
          ElMessage.success('密码修改成功')
          passwordForm.oldPassword = ''
          passwordForm.newPassword = ''
          passwordForm.confirmPassword = ''
          passwordFormRef.value.resetFields()
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '密码修改失败')
      } finally {
        passwordLoading.value = false
      }
    }
  })
}

onMounted(() => {
  const savedAdmin = localStorage.getItem('admin')
  if (savedAdmin) {
    admin.value = JSON.parse(savedAdmin)
    profileForm.email = admin.value.email || ''
  }
  loadAdminInfo()
})
</script>

<style scoped>
.settings-page {
  padding: 0;
}

.content-grid {
  display: grid;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}
</style>
