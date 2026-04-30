<template>
  <div class="tags-page">
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 class="page-title">标签管理</h1>
        <p class="page-subtitle">管理内容分类标签</p>
      </div>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建标签
      </el-button>
    </div>
    
    <div class="card">
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索标签名称"
          prefix-icon="Search"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
          style="width: 200px;"
        />
        <el-select
          v-model="filterStatus"
          placeholder="状态筛选"
          clearable
          @change="handleSearch"
          style="width: 150px;"
        >
          <el-option label="启用" value="1" />
          <el-option label="禁用" value="0" />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetSearch">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
      
      <el-table
        :data="tags"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="标签名称" min-width="150">
          <template #default="{ row }">
            <div class="tag-name-cell">
              <span 
                class="tag-color-dot" 
                :style="{ backgroundColor: row.color || '#0071e3' }"
              ></span>
              <span class="tag-name">{{ row.name }}</span>
              <span class="tag-slug">（{{ row.slug }}）</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="posts_count" label="关联内容数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="primary" size="small">{{ row.posts_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            <span>{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" link size="small" @click="handleEdit(row)">
                编辑
              </el-button>
              <el-button 
                type="danger" 
                link 
                size="small"
                :disabled="row.posts_count > 0"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
      
      <div class="empty-wrapper" v-else-if="!loading && tags.length === 0">
        <el-empty description="暂无标签数据" />
      </div>
    </div>
    
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑标签' : '新建标签'"
      width="500px"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="标签名称" prop="name">
          <el-input 
            v-model="form.name" 
            placeholder="请输入标签名称" 
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="标识" prop="slug">
          <el-input 
            v-model="form.slug" 
            placeholder="请输入标签标识（英文，用于URL）" 
            maxlength="50"
            show-word-limit
          />
          <div class="form-tip">
            <span class="tip-text">标签标识用于URL识别，建议使用英文和连字符</span>
          </div>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            placeholder="请输入标签描述（可选）" 
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="标签颜色">
          <div class="color-picker-wrapper">
            <div 
              class="color-preview" 
              :style="{ backgroundColor: form.color }"
            ></div>
            <el-input 
              v-model="form.color" 
              placeholder="#0071e3" 
              maxlength="20"
              style="width: 150px;"
            />
            <el-color-picker v-model="form.color" />
          </div>
        </el-form-item>
        
        <el-form-item label="排序">
          <el-input-number 
            v-model="form.sort_order" 
            :min="0"
            :max="9999"
            :step="1"
          />
          <div class="form-tip">
            <span class="tip-text">数值越小排序越靠前</span>
          </div>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-radio-group v-model="form.is_active">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Search, Refresh, Edit, Delete 
} from '@element-plus/icons-vue'
import { adminApi } from '../services/api'

const loading = ref(false)
const submitting = ref(false)
const tags = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const filterStatus = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentTagId = ref(null)

const form = reactive({
  name: '',
  slug: '',
  description: '',
  color: '#0071e3',
  sort_order: 0,
  is_active: 1
})

const rules = {
  name: [
    { required: true, message: '请输入标签名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  slug: [
    { required: true, message: '请输入标签标识', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

const formatTime = (time) => {
  if (!time) return '-'
  return time.replace(' GMT', '')
}

const loadTags = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }
    
    if (filterStatus.value !== '') {
      params.is_active = filterStatus.value
    }
    
    const response = await adminApi.getTags(params)
    if (response.data.success) {
      tags.value = response.data.tags || []
      total.value = response.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载标签列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadTags()
}

const resetSearch = () => {
  searchKeyword.value = ''
  filterStatus.value = ''
  currentPage.value = 1
  loadTags()
}

const handlePageChange = () => {
  loadTags()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadTags()
}

const resetForm = () => {
  form.name = ''
  form.slug = ''
  form.description = ''
  form.color = '#0071e3'
  form.sort_order = 0
  form.is_active = 1
  currentTagId.value = null
  isEdit.value = false
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleCreate = () => {
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  isEdit.value = true
  currentTagId.value = row.id
  form.name = row.name
  form.slug = row.slug
  form.description = row.description || ''
  form.color = row.color || '#0071e3'
  form.sort_order = row.sort_order || 0
  form.is_active = row.is_active
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  if (row.posts_count > 0) {
    ElMessage.warning(`该标签下还有 ${row.posts_count} 篇内容，无法删除`)
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除标签「${row.name}」吗？`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await adminApi.deleteTag(row.id)
    if (response.data.success) {
      ElMessage.success('删除成功')
      loadTags()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        let response
        
        if (isEdit.value && currentTagId.value) {
          response = await adminApi.updateTag(currentTagId.value, {
            name: form.name.trim(),
            slug: form.slug.trim().toLowerCase().replace(/\s+/g, '-'),
            description: form.description.trim() || null,
            color: form.color,
            sort_order: form.sort_order,
            is_active: form.is_active
          })
        } else {
          response = await adminApi.createTag({
            name: form.name.trim(),
            slug: form.slug.trim().toLowerCase().replace(/\s+/g, '-'),
            description: form.description.trim() || null,
            color: form.color,
            sort_order: form.sort_order,
            is_active: form.is_active
          })
        }
        
        if (response.data.success) {
          ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
          dialogVisible.value = false
          loadTags()
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.tags-page {
  padding: 0;
}

.tag-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  flex-shrink: 0;
}

.tag-name {
  font-weight: 500;
  color: var(--color-text);
}

.tag-slug {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.form-tip {
  margin-top: 8px;
}

.tip-text {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
