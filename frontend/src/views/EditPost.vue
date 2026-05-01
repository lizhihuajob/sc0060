<template>
  <div class="edit-post-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">编辑信息</h1>
      </div>

      <div class="form-card card" v-loading="loading">
        <el-form 
          ref="formRef" 
          :model="form" 
          :rules="rules" 
          class="post-form"
          label-position="top"
        >
          <el-form-item label="信息类型" prop="isTask">
            <el-radio-group v-model="form.isTask">
              <el-radio :label="0">公告</el-radio>
              <el-radio :label="1">任务</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="标题" prop="title">
            <el-input 
              v-model="form.title" 
              placeholder="请输入标题" 
              size="large"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="内容" prop="content">
            <MarkdownEditor 
              v-model="form.content" 
              placeholder="请输入内容，支持 Markdown 格式（点击帮助按钮查看语法）"
              :rows="10"
            />
          </el-form-item>

          <el-form-item label="可见范围" prop="viewPermission">
            <el-select v-model="form.viewPermission" placeholder="选择可见范围" size="large" style="width: 100%;">
              <el-option label="所有用户" value="all" />
              <el-option label="仅注册用户" value="registered" />
              <el-option label="白银及以上" value="silver_above" />
              <el-option label="黄金及以上" value="gold_above" />
            </el-select>
            <div class="permission-hint">
              <p class="hint-text">
                <strong>所有用户：</strong>所有人可见，包括未登录用户
              </p>
              <p class="hint-text">
                <strong>仅注册用户：</strong>仅登录用户可见
              </p>
              <p class="hint-text">
                <strong>白银及以上：</strong>白银会员及以上等级可见
              </p>
              <p class="hint-text">
                <strong>黄金及以上：</strong>黄金会员及以上等级可见
              </p>
            </div>
          </el-form-item>

          <el-form-item label="当前图片">
            <div class="current-images" v-if="currentImages.length > 0">
              <div 
                v-for="(img, index) in currentImages" 
                :key="index"
                class="current-image-item"
              >
                <img :src="`/uploads/${img}`" class="current-image" />
              </div>
            </div>
            <el-empty v-else description="暂无图片" :image-size="60" />
          </el-form-item>

          <el-form-item label="上传新图片 (可选，将替换原有图片)">
            <el-upload
              v-model:file-list="fileList"
              action="#"
              multiple
              :limit="5"
              :on-exceed="handleExceed"
              :auto-upload="false"
              list-type="picture-card"
            >
              <el-icon><Plus /></el-icon>
              <template #tip>
                <div class="el-upload__tip">
                  支持 jpg/png/gif 格式，最多上传 5 张图片
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <el-form-item label="修改原因 (可选)">
            <el-input 
              v-model="form.editReason" 
              type="textarea" 
              placeholder="请输入修改原因（可选）" 
              :rows="3"
              size="large"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              class="submit-btn"
              :loading="submitting"
              @click="handleSubmit"
            >
              保存修改
            </el-button>
            <el-button 
              size="large" 
              @click="router.back()"
            >
              取消
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { postApi } from '../services/api'
import { useUserStore } from '../stores/userStore'
import MarkdownEditor from '../components/MarkdownEditor.vue'

const router = useRouter()
const route = useRoute()
const { user } = useUserStore()
const formRef = ref(null)
const fileList = ref([])
const loading = ref(true)
const submitting = ref(false)
const postData = ref(null)

const form = reactive({
  title: '',
  content: '',
  viewPermission: 'all',
  isTask: 0,
  editReason: ''
})

const currentImages = computed(() => {
  return postData.value?.images || []
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

const loadPost = async () => {
  const postId = route.params.id
  if (!postId) {
    ElMessage.error('无效的帖子ID')
    router.push('/my-posts')
    return
  }

  try {
    const response = await postApi.getById(postId)
    if (response.data.success) {
      postData.value = response.data.post
      form.title = postData.value.title
      form.content = postData.value.content
      form.viewPermission = postData.value.view_permission
      form.isTask = postData.value.is_task
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '加载帖子失败')
    router.push('/my-posts')
  } finally {
    loading.value = false
  }
}

const handleExceed = (files, fileList) => {
  ElMessage.warning('最多只能上传 5 张图片')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  if (!user.value) {
    ElMessage.warning('请先登录后再编辑信息')
    router.push('/login')
    return
  }
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const formData = new FormData()
        formData.append('title', form.title)
        formData.append('content', form.content)
        formData.append('view_permission', form.viewPermission)
        formData.append('is_task', form.isTask)
        
        if (form.editReason) {
          formData.append('edit_reason', form.editReason)
        }
        
        fileList.value.forEach(file => {
          if (file.raw) {
            formData.append('images', file.raw)
          }
        })
        
        const response = await postApi.update(postData.value.id, formData)
        if (response.data.success) {
          ElMessage.success(response.data.message)
          router.push('/my-posts')
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '更新失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  loadPost()
})
</script>

<style scoped>
.edit-post-page {
  flex: 1;
  padding: 40px 0;
  background: var(--color-background);
}

.page-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 24px;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.003em;
  margin: 0;
  color: var(--color-text);
}

.form-card {
  padding: 32px;
}

:deep(.el-form-item__label) {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
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

:deep(.el-textarea__inner) {
  padding: 12px 16px;
  border-radius: var(--radius-md);
  box-shadow: 0 0 0 1px var(--color-border) inset;
  border: none;
  transition: box-shadow var(--transition-fast);
  font-size: 15px;
}

:deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px var(--color-primary) inset;
}

:deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px var(--color-primary) inset, 0 0 0 4px rgba(0, 113, 227, 0.15);
}

:deep(.el-select .el-input__wrapper) {
  padding: 4px 12px;
}

.permission-hint {
  margin-top: 12px;
}

.hint-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 4px 0;
}

.hint-text strong {
  color: var(--color-text);
  font-weight: 500;
}

.current-images {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.current-image-item {
  position: relative;
}

.current-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.submit-btn {
  min-width: 120px;
  border-radius: var(--radius-md);
}

:deep(.el-upload--picture-card) {
  width: 100px;
  height: 100px;
  border-radius: var(--radius-md);
  border: 1px dashed var(--color-border);
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 100px;
  height: 100px;
  border-radius: var(--radius-md);
}

@media (max-width: 768px) {
  .edit-post-page {
    padding: 24px 0;
  }
  
  .page-container {
    padding: 0 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .form-card {
    padding: 20px;
  }
}
</style>
