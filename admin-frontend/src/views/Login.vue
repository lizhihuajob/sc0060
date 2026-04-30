<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <el-icon><Setting /></el-icon>
        </div>
        <h1 class="login-title">后台管理系统</h1>
        <p class="login-subtitle">信息发布平台管理后台</p>
      </div>
      
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        class="login-form"
      >
        <el-form-item prop="username" class="login-form-item">
          <el-input 
            v-model="form.username" 
            placeholder="请输入用户名" 
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password" class="login-form-item">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码" 
            size="large"
            prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item class="login-form-item">
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading" 
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-tip">
        <p>默认账号：admin</p>
        <p>默认密码：admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Setting, User, Lock } from '@element-plus/icons-vue'
import { adminApi } from '../services/api'

const router = useRouter()
const route = useRoute()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await adminApi.login({
          username: form.username.trim(),
          password: form.password
        })
        
        if (response.data.success) {
          localStorage.setItem('admin_auth', 'true')
          localStorage.setItem('admin', JSON.stringify(response.data.admin))
          ElMessage.success(response.data.message)
          
          const redirect = route.query.redirect || '/dashboard'
          router.push(redirect)
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '登录失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-logo .el-icon {
  font-size: 48px;
  color: var(--color-primary);
}

.login-tip {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--color-border);
  text-align: center;
}

.login-tip p {
  margin: 4px 0;
  font-size: 12px;
  color: var(--color-text-secondary);
}
</style>
