<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card card">
        <div class="auth-header">
          <h1 class="auth-title">登录</h1>
          <p class="auth-subtitle">欢迎回来，请登录您的账户</p>
        </div>

        <el-form 
          ref="formRef" 
          :model="form" 
          :rules="rules" 
          class="auth-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input 
              v-model="form.username" 
              placeholder="用户名" 
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              v-model="form.password" 
              type="password" 
              placeholder="密码" 
              size="large"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              class="submit-btn" 
              :loading="loading"
              @click="handleLogin"
              size="large"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="auth-footer">
          <p>还没有账户？</p>
          <router-link to="/register">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '../services/api'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const route = useRoute()
const formRef = ref(null)
const loading = ref(false)
const { setUser } = useUserStore()

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await authApi.login(form)
        if (response.data.success) {
          setUser(response.data.user)
          ElMessage.success(response.data.message)
          const redirect = route.query.redirect || '/'
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
.auth-page {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--color-background);
}

.auth-container {
  width: 100%;
  max-width: 400px;
}

.auth-card {
  padding: 40px;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-title {
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.003em;
  margin: 0 0 8px;
  color: var(--color-text);
}

.auth-subtitle {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0;
}

.auth-form {
  margin-bottom: 24px;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-input__wrapper) {
  padding: 12px 16px;
  border-radius: var(--radius-md);
  box-shadow: 0 0 0 1px var(--color-border) inset;
  transition: box-shadow var(--transition-fast);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--color-primary) inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--color-primary) inset, 0 0 0 4px rgba(0, 113, 227, 0.15);
}

.submit-btn {
  width: 100%;
  border-radius: var(--radius-md);
  padding: 12px;
  font-size: 17px;
  font-weight: 500;
}

.auth-footer {
  text-align: center;
  font-size: 15px;
  color: var(--color-text-secondary);
}

.auth-footer p {
  margin: 0 0 8px;
}

.auth-footer a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>
