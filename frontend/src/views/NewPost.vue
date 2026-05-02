<template>
  <div class="new-post-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">发布信息</h1>
      </div>

      <div class="form-card card">
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

          <el-form-item label="标签">
            <el-select
              v-model="selectedTagIds"
              multiple
              placeholder="请选择标签（可选）"
              size="large"
              style="width: 100%;"
              collapse-tags
            >
              <el-option
                v-for="tag in tagsList"
                :key="tag.id"
                :label="tag.name"
                :value="tag.id"
              >
                <div class="tag-option">
                  <span 
                    class="tag-color-dot" 
                    :style="{ backgroundColor: tag.color || '#0071e3' }"
                  ></span>
                  <span class="tag-name">{{ tag.name }}</span>
                </div>
              </el-option>
            </el-select>
            <div class="form-tip">
              <span class="tip-text">选择合适的标签可以让更多用户发现您的内容</span>
            </div>
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

          <el-form-item label="上传图片 (可选)">
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

          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              class="submit-btn"
              :loading="loading"
              @click="handleSubmit"
            >
              发布信息
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { postApi, tagApi } from '../services/api'
import { useUserStore } from '../stores/userStore'
import MarkdownEditor from '../components/MarkdownEditor.vue'

const router = useRouter()
const { user } = useUserStore()
const formRef = ref(null)
const fileList = ref([])
const loading = ref(false)
const tagsList = ref([])
const selectedTagIds = ref([])

const form = reactive({
  title: '',
  content: '',
  viewPermission: 'all',
  isTask: 0
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

const loadTags = async () => {
  try {
    const response = await tagApi.getAll()
    if (response.data.success) {
      tagsList.value = response.data.tags || []
    }
  } catch (error) {
    console.error('加载标签列表失败:', error)
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
        
        if (selectedTagIds.value && selectedTagIds.value.length > 0) {
          formData.append('tag_ids', selectedTagIds.value.join(','))
        }
        
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
  loadTags()
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
  max-width: 800px;
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

.tag-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-name {
  font-size: 14px;
  color: var(--color-text);
}

.form-tip {
  margin-top: 8px;
}
</style>
