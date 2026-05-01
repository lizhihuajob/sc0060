<template>
  <div class="users-page">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <p class="page-subtitle">管理平台注册用户</p>
    </div>
    
    <div class="card">
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名或邮箱"
          prefix-icon="Search"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
          style="width: 200px;"
        />
        <el-select
          v-model="filterLevel"
          placeholder="会员等级"
          clearable
          @change="handleSearch"
          style="width: 150px;"
        >
          <el-option label="青铜会员" value="bronze" />
          <el-option label="白银会员" value="silver" />
          <el-option label="黄金会员" value="gold" />
          <el-option label="黑卡会员" value="black" />
          <el-option label="钻石会员" value="diamond" />
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
        :data="users"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="120">
          <template #default="{ row }">
            <div class="user-info">
              <div class="user-avatar-small" v-if="row.avatar">
                <img :src="`/uploads/${row.avatar}`" alt="头像" class="avatar-img" />
              </div>
              <div class="user-avatar-small" v-else>
                {{ row.username?.charAt(0).toUpperCase() }}
              </div>
              <span>{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180">
          <template #default="{ row }">
            <span>{{ row.email || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="会员等级" width="100">
          <template #default="{ row }">
            <span class="level-badge" :class="row.level">{{ getLevelName(row.level) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="posts_count" label="发布数" width="80" align="center">
          <template #default="{ row }">
            <span>{{ row.posts_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="balance" label="余额" width="100" align="center">
          <template #default="{ row }">
            <span>¥{{ row.balance?.toFixed(2) || '0.00' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" min-width="180">
          <template #default="{ row }">
            <span>{{ formatTime(row.created_at) }}</span>
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { adminApi } from '../services/api'

const loading = ref(false)
const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const filterLevel = ref('')

const userLevels = {
  bronze: '青铜会员',
  silver: '白银会员',
  gold: '黄金会员',
  black: '黑卡会员',
  diamond: '钻石会员'
}

const getLevelName = (level) => {
  return userLevels[level] || level
}

const formatTime = (time) => {
  if (!time) return '-'
  return time.replace(' GMT', '')
}

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }
    
    if (filterLevel.value) {
      params.level = filterLevel.value
    }
    
    const response = await adminApi.getUsers(params)
    if (response.data.success) {
      users.value = response.data.users || []
      total.value = response.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载用户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadUsers()
}

const resetSearch = () => {
  searchKeyword.value = ''
  filterLevel.value = ''
  currentPage.value = 1
  loadUsers()
}

const handlePageChange = () => {
  loadUsers()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadUsers()
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-page {
  padding: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 12px;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.level-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  color: white;
}

.level-badge.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #a0522d 100%);
}

.level-badge.silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #a9a9a9 100%);
  color: #1d1d1f;
}

.level-badge.gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  color: #1d1d1f;
}

.level-badge.black {
  background: linear-gradient(135deg, #2f2f2f 0%, #1a1a1a 100%);
}

.level-badge.diamond {
  background: linear-gradient(135deg, #b9f2ff 0%, #87ceeb 100%);
  color: #1d1d1f;
}
</style>
