<template>
  <div class="profile-page">
    <el-card>
      <template #header>
        <span>个人设置</span>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-form
            :model="basicForm"
            :rules="basicRules"
            ref="basicFormRef"
            label-width="100px"
            style="max-width: 500px;"
          >
            <el-form-item label="用户名">
              <el-input v-model="basicForm.username" disabled />
              <div class="form-tip">用户名不可修改</div>
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="basicForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="角色">
              <el-tag size="large">{{ getRoleName(adminStore.role) }}</el-tag>
            </el-form-item>
            <el-form-item label="状态">
              <el-tag type="success" size="large">正常</el-tag>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="handleSaveBasic">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="修改密码" name="password">
          <el-form
            :model="passwordForm"
            :rules="passwordRules"
            ref="passwordFormRef"
            label-width="100px"
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
                placeholder="请输入新密码"
                show-password
              />
              <div class="form-tip">密码长度不能少于6位</div>
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
              <el-button type="primary" :loading="saving" @click="handleChangePassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useAdminStore } from '../stores/adminStore'
import { adminApi } from '../services/api'
import { ElMessage } from 'element-plus'

const adminStore = useAdminStore()

const activeTab = ref('basic')
const saving = ref(false)
const basicFormRef = ref(null)
const passwordFormRef = ref(null)

const basicForm = reactive({
  username: '',
  email: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const basicRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
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
  const roleNames = {
    'super_admin': '超级管理员',
    'admin': '管理员'
  }
  return roleNames[role] || role
}

const loadAdminData = () => {
  if (adminStore.admin) {
    basicForm.username = adminStore.admin.username || ''
    basicForm.email = adminStore.admin.email || ''
  }
}

const handleSaveBasic = async () => {
  if (!basicFormRef.value) return

  await basicFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        const response = await adminApi.updateProfile({
          email: basicForm.email
        })
        if (response.data.success) {
          ElMessage.success('保存成功')
          adminStore.admin.email = basicForm.email
        }
      } catch (error) {
        console.error('保存失败:', error)
        ElMessage.error('保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
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
        }
      } catch (error) {
        console.error('密码修改失败:', error)
        ElMessage.error('原密码错误')
      } finally {
        saving.value = false
      }
    }
  })
}

onMounted(() => {
  loadAdminData()
})
</script>

<style scoped>
.profile-page {
  padding: 10px;
}

.form-tip {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}
</style>
