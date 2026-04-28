<template>
  <div class="new-post-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title gradient-text">发布信息</h1>
        <p class="page-subtitle">分享你的内容，让更多人看到</p>
      </div>

      <div class="form-layout">
        <main class="form-main">
          <div class="form-card card card-glass">
            <el-form 
              ref="formRef" 
              :model="form" 
              :rules="rules" 
              class="post-form"
              label-position="top"
            >
              <div class="form-section">
                <div class="section-title-wrapper">
                  <div class="section-icon">
                    <el-icon><Document /></el-icon>
                  </div>
                  <h3 class="section-label">基本信息</h3>
                </div>
                
                <el-form-item label="信息标题" prop="title">
                  <el-input 
                    v-model="form.title" 
                    placeholder="请输入一个吸引人的标题" 
                    size="large"
                    maxlength="100"
                    show-word-limit
                    class="form-input-large"
                  />
                </el-form-item>

                <el-form-item label="信息分类" prop="category">
                  <div class="category-grid">
                    <div 
                      v-for="(label, key) in categories" 
                      :key="key"
                      class="category-option"
                      :class="{ active: form.category === key }"
                      @click="form.category = key"
                    >
                      <span class="category-icon">{{ getCategoryIcon(key) }}</span>
                      <span class="category-name">{{ label }}</span>
                    </div>
                  </div>
                </el-form-item>

                <el-form-item label="信息类型" prop="isTask">
                  <div class="type-options">
                    <div 
                      class="type-option"
                      :class="{ active: form.isTask === 0 }"
                      @click="form.isTask = 0"
                    >
                      <div class="type-icon notice">
                        <el-icon><Bell /></el-icon>
                      </div>
                      <div class="type-info">
                        <span class="type-name">公告通知</span>
                        <span class="type-desc">发布重要公告、通知消息</span>
                      </div>
                    </div>
                    <div 
                      class="type-option"
                      :class="{ active: form.isTask === 1 }"
                      @click="form.isTask = 1"
                    >
                      <div class="type-icon task">
                        <el-icon><Target /></el-icon>
                      </div>
                      <div class="type-info">
                        <span class="type-name">任务招募</span>
                        <span class="type-desc">发布任务需求、招募信息</span>
                      </div>
                    </div>
                  </div>
                </el-form-item>

                <el-form-item label="详细内容" prop="content">
                  <el-input 
                    v-model="form.content" 
                    type="textarea" 
                    placeholder="请输入详细内容，清晰地描述你的信息..." 
                    :rows="8"
                    class="form-textarea"
                  />
                </el-form-item>
              </div>

              <div class="form-section">
                <div class="section-title-wrapper">
                  <div class="section-icon">
                    <el-icon><Picture /></el-icon>
                  </div>
                  <h3 class="section-label">图片附件</h3>
                </div>
                
                <el-form-item label="上传图片 (可选)">
                  <el-upload
                    v-model:file-list="fileList"
                    action="#"
                    multiple
                    :limit="5"
                    :on-exceed="handleExceed"
                    :auto-upload="false"
                    list-type="picture-card"
                    class="upload-area"
                  >
                    <div class="upload-prompt">
                      <el-icon class="upload-icon"><Plus /></el-icon>
                      <span class="upload-text">上传图片</span>
                      <span class="upload-hint">支持 jpg/png/gif，最多5张</span>
                    </div>
                  </el-upload>
                </el-form-item>
              </div>

              <div class="form-section">
                <div class="section-title-wrapper">
                  <div class="section-icon">
                    <el-icon><Lock /></el-icon>
                  </div>
                  <h3 class="section-label">权限设置</h3>
                </div>
                
                <el-form-item label="可见范围" prop="viewPermission">
                  <div class="permission-options">
                    <div 
                      v-for="option in permissionOptions" 
                      :key="option.value"
                      class="permission-option"
                      :class="{ active: form.viewPermission === option.value }"
                      @click="form.viewPermission = option.value"
                    >
                      <div class="permission-icon" :class="option.value">
                        <el-icon><component :is="option.icon" /></el-icon>
                      </div>
                      <div class="permission-info">
                        <span class="permission-name">{{ option.label }}</span>
                        <span class="permission-desc">{{ option.desc }}</span>
                      </div>
                    </div>
                  </div>
                </el-form-item>
              </div>

              <el-form-item class="submit-section">
                <div class="submit-actions">
                  <el-button 
                    type="primary" 
                    size="large" 
                    class="submit-btn"
                    :loading="loading"
                    @click="handleSubmit"
                  >
                    <el-icon v-if="!loading"><Check /></el-icon>
                    {{ loading ? '发布中...' : '立即发布' }}
                  </el-button>
                  <el-button 
                    size="large" 
                    class="cancel-btn"
                    @click="router.back()"
                  >
                    取消
                  </el-button>
                </div>
                <p class="form-hint">
                  <el-icon><InfoFilled /></el-icon>
                  发布后可以在"我的发布"中管理，付费可享受置顶推广
                </p>
              </el-form-item>
            </el-form>
          </div>
        </main>

        <aside class="form-sidebar">
          <div class="sidebar-card card card-glass">
            <div class="sidebar-header">
              <el-icon><User /></el-icon>
              <span>发布信息</span>
            </div>
            
            <div class="user-info-box">
              <div class="user-level">
                <span class="level-badge" :class="user?.level">{{ user?.level_name }}</span>
              </div>
              <div class="user-stats">
                <div class="stat-item">
                  <span class="stat-value">{{ user?.posts_count || 0 }}/{{ user?.posts_limit || 0 }}</span>
                  <span class="stat-label">剩余发布</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">¥{{ (user?.balance || 0).toFixed(2) }}</span>
                  <span class="stat-label">账户余额</span>
                </div>
              </div>
            </div>

            <div class="divider"></div>

            <div class="pinned-info">
              <div class="info-header">
                <el-icon class="pinned-icon"><Star /></el-icon>
                <span class="info-title">置顶推广</span>
              </div>
              <p class="info-desc">
                让你的信息在首页置顶展示，获得更多曝光！
              </p>
              <div class="pinned-features">
                <div class="feature-item">
                  <el-icon class="check-icon"><Check /></el-icon>
                  <span>首页置顶展示区</span>
                </div>
                <div class="feature-item">
                  <el-icon class="check-icon"><Check /></el-icon>
                  <span>特殊高亮标识</span>
                </div>
                <div class="feature-item">
                  <el-icon class="check-icon"><Check /></el-icon>
                  <span>持续{{ pinnedConfig.duration_days || 7 }}天</span>
                </div>
              </div>
              <div class="pinned-price">
                <span class="price-label">置顶费用</span>
                <span class="price-value">¥{{ pinnedConfig.price || 10 }}</span>
              </div>
              <router-link to="/my-posts" class="pinned-btn">
                <el-icon><TrendCharts /></el-icon>
                发布后去置顶
              </router-link>
            </div>
          </div>

          <div class="sidebar-card card card-glass mt-4">
            <div class="sidebar-header">
              <el-icon><InfoFilled /></el-icon>
              <span>温馨提示</span>
            </div>
            <ul class="tips-list">
              <li class="tip-item">
                <el-icon class="tip-icon"><CircleCheck /></el-icon>
                请确保内容真实有效
              </li>
              <li class="tip-item">
                <el-icon class="tip-icon"><CircleCheck /></el-icon>
                标题简洁明了更吸引眼球
              </li>
              <li class="tip-item">
                <el-icon class="tip-icon"><CircleCheck /></el-icon>
                配图清晰获得更多关注
              </li>
              <li class="tip-item">
                <el-icon class="tip-icon"><CircleCheck /></el-icon>
                禁止发布违法违规内容
              </li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Plus, Check, Document, Lock, Bell, Target, 
  Picture, User, Star, TrendCharts, InfoFilled,
  CircleCheck, View, Connection
} from '@element-plus/icons-vue'
import { postApi, configApi } from '../services/api'
import { useUserStore } from '../stores/userStore'

const router = useRouter()
const { user } = useUserStore()
const formRef = ref(null)
const fileList = ref([])
const loading = ref(false)
const categories = ref({})
const pinnedConfig = ref({ price: 10, duration_days: 7 })

const form = reactive({
  title: '',
  content: '',
  viewPermission: 'all',
  isTask: 0,
  category: 'notice'
})

const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入内容', trigger: 'blur' },
    { min: 10, message: '内容至少10个字符', trigger: 'blur' }
  ]
}

const permissionOptions = [
  { value: 'all', label: '所有用户', desc: '所有人可见，包括未登录用户', icon: View },
  { value: 'registered', label: '注册用户', desc: '仅登录用户可见', icon: User },
  { value: 'silver_above', label: '白银及以上', desc: '白银会员及以上等级可见', icon: Connection },
  { value: 'gold_above', label: '黄金及以上', desc: '黄金会员及以上等级可见', icon: Star }
]

const getCategoryIcon = (category) => {
  const icons = {
    notice: '📢',
    activity: '🎉',
    task: '🎯',
    job: '💼',
    trade: '💰',
    other: '📋'
  }
  return icons[category] || '📋'
}

const fetchConfig = async () => {
  try {
    const response = await configApi.getMembership()
    if (response.data.success) {
      categories.value = response.data.categories || {}
      pinnedConfig.value = response.data.pinned_config || pinnedConfig.value
      if (Object.keys(categories.value).length > 0) {
        form.category = Object.keys(categories.value)[0]
      }
    }
  } catch (error) {
    console.error('获取配置失败:', error)
  }
}

const handleExceed = (files, fileList) => {
  ElMessage.warning('最多只能上传 5 张图片')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  if (!user.value) {
    ElMessage.warning('请先登录后再发布信息')
    router.push('/login')
    return
  }
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const formData = new FormData()
        formData.append('title', form.title)
        formData.append('content', form.content)
        formData.append('view_permission', form.viewPermission)
        formData.append('is_task', form.isTask)
        formData.append('category', form.category)
        
        fileList.value.forEach(file => {
          if (file.raw) {
            formData.append('images', file.raw)
          }
        })
        
        const response = await postApi.create(formData)
        if (response.data.success) {
          ElMessage.success(response.data.message)
          router.push('/my-posts')
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '发布失败')
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.new-post-page {
  flex: 1;
  padding: 40px 0;
  background: var(--color-background);
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 8px;
}

.page-subtitle {
  font-size: 17px;
  color: var(--color-text-secondary);
  margin: 0;
}

.form-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.form-main {
  display: flex;
  flex-direction: column;
}

.form-card {
  padding: 32px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.section-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-indigo) 100%);
  color: white;
  border-radius: var(--radius-md);
  font-size: 18px;
}

.section-label {
  font-size: 17px;
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}

:deep(.el-form-item__label) {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

:deep(.el-input__wrapper) {
  padding: 14px 16px;
  border-radius: var(--radius-md);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.08) inset;
  transition: all var(--transition-fast);
  background: rgba(255, 255, 255, 0.9);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--color-primary) inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--color-primary) inset, 0 0 0 4px rgba(0, 113, 227, 0.12);
}

:deep(.el-textarea__inner) {
  padding: 14px 16px;
  border-radius: var(--radius-md);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.08) inset;
  border: none;
  transition: all var(--transition-fast);
  font-size: 15px;
  line-height: 1.6;
}

:deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px var(--color-primary) inset;
}

:deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px var(--color-primary) inset, 0 0 0 4px rgba(0, 113, 227, 0.12);
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.category-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.category-option:hover {
  border-color: rgba(0, 113, 227, 0.3);
  background: white;
}

.category-option.active {
  border-color: var(--color-primary);
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.08) 0%, rgba(94, 92, 230, 0.04) 100%);
}

.category-option .category-icon {
  font-size: 28px;
}

.category-option .category-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.type-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.type-option {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.type-option:hover {
  border-color: rgba(0, 113, 227, 0.3);
  background: white;
}

.type-option.active {
  border-color: var(--color-primary);
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.08) 0%, rgba(94, 92, 230, 0.04) 100%);
}

.type-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  font-size: 22px;
}

.type-icon.notice {
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.15) 0%, rgba(0, 113, 227, 0.05) 100%);
  color: var(--color-primary);
}

.type-icon.task {
  background: linear-gradient(135deg, rgba(255, 149, 0, 0.15) 0%, rgba(255, 149, 0, 0.05) 100%);
  color: var(--color-warning);
}

.type-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.type-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.type-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.permission-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.permission-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.permission-option:hover {
  border-color: rgba(0, 113, 227, 0.3);
  background: white;
}

.permission-option.active {
  border-color: var(--color-primary);
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.08) 0%, rgba(94, 92, 230, 0.04) 100%);
}

.permission-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  font-size: 18px;
  background: rgba(0, 0, 0, 0.04);
  color: var(--color-text-secondary);
}

.permission-option.active .permission-icon {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-indigo) 100%);
  color: white;
}

.permission-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.permission-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.permission-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.upload-area {
  width: 100%;
}

.upload-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 20px;
}

.upload-icon {
  font-size: 28px;
  color: var(--color-text-secondary);
}

.upload-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.upload-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
}

:deep(.el-upload--picture-card) {
  width: 100px;
  height: 100px;
  border-radius: var(--radius-md);
  border: 2px dashed rgba(0, 0, 0, 0.1);
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 100px;
  height: 100px;
  border-radius: var(--radius-md);
}

.submit-section {
  margin-bottom: 0 !important;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.submit-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.submit-btn {
  min-width: 160px;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-indigo) 100%);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 113, 227, 0.35);
}

.cancel-btn {
  min-width: 120px;
  height: 48px;
  font-size: 16px;
  border-radius: var(--radius-md);
  border: 2px solid rgba(0, 0, 0, 0.08);
  background: white;
}

.cancel-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.form-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
}

.form-sidebar {
  position: sticky;
  top: 76px;
  height: fit-content;
}

.sidebar-card {
  padding: 20px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.user-info-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-level {
  text-align: center;
}

.user-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.user-stats .stat-item {
  text-align: center;
  padding: 12px 8px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: var(--radius-sm);
}

.user-stats .stat-value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.user-stats .stat-label {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.1), transparent);
  margin: 20px 0;
}

.pinned-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pinned-icon {
  color: var(--color-warning);
  font-size: 18px;
}

.info-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.info-desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--color-text-secondary);
  margin: 0;
}

.pinned-features {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text);
}

.check-icon {
  color: var(--color-success);
  font-size: 16px;
}

.pinned-price {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(255, 149, 0, 0.08) 0%, rgba(255, 204, 0, 0.04) 100%);
  border-radius: var(--radius-md);
}

.price-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.price-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-warning);
}

.pinned-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, var(--color-warning) 0%, var(--color-pink) 100%);
  color: white;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.pinned-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(255, 149, 0, 0.35);
  color: white;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text);
  line-height: 1.4;
}

.tip-icon {
  color: var(--color-success);
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 1px;
}

@media (max-width: 1024px) {
  .form-layout {
    grid-template-columns: 1fr;
  }
  
  .form-sidebar {
    position: static;
    order: -1;
  }
  
  .category-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .page-title {
    font-size: 28px;
  }
  
  .form-card {
    padding: 20px;
  }
  
  .category-grid {
    grid-template-columns: 1fr;
  }
  
  .type-options {
    grid-template-columns: 1fr;
  }
  
  .permission-options {
    grid-template-columns: 1fr;
  }
  
  .submit-actions {
    flex-direction: column;
  }
  
  .submit-btn,
  .cancel-btn {
    width: 100%;
    min-width: auto;
  }
}
</style>
