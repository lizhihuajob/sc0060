<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索用户名/邮箱"
              clearable
              style="width: 200px; margin-right: 10px;"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="searchForm.level"
              placeholder="选择等级"
              clearable
              style="width: 120px; margin-right: 10px;"
              @change="handleSearch"
            >
              <el-option label="青铜" value="bronze" />
              <el-option label="白银" value="silver" />
              <el-option label="黄金" value="gold" />
              <el-option label="黑金" value="black" />
              <el-option label="钻石" value="diamond" />
            </el-select>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="users" style="width: 100%" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="level_name" label="等级" width="100">
          <template #default="scope">
            <el-tag :type="getLevelTagType(scope.row.level)" size="small">
              {{ scope.row.level_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="posts_count" label="发布数" width="80" />
        <el-table-column prop="balance" label="余额" width="100">
          <template #default="scope">
            ¥{{ scope.row.balance }}
          </template>
        </el-table-column>
        <el-table-column prop="total_recharge" label="累计充值" width="100">
          <template #default="scope">
            <el-tag type="success" size="small">
              ¥{{ scope.row.total_recharge || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_spent" label="累计消费" width="100">
          <template #default="scope">
            <el-tag type="warning" size="small">
              ¥{{ scope.row.total_spent || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_banned" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_banned ? 'danger' : 'success'" size="small">
              {{ scope.row.is_banned ? '已封禁' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" text @click="viewDetail(scope.row)">
              详情
            </el-button>
            <el-button
              v-if="!scope.row.is_banned"
              type="danger"
              text
              @click="handleBan(scope.row)"
            >
              封禁
            </el-button>
            <el-button
              v-else
              type="success"
              text
              @click="handleUnban(scope.row)"
            >
              解封
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.perPage"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchUsers"
          @current-change="fetchUsers"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailVisible" title="用户详情" width="600px">
      <el-descriptions :column="2" border v-if="currentUser">
        <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentUser.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="等级">
          <el-tag :type="getLevelTagType(currentUser.level)" size="small">
            {{ currentUser.level_name }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布数">{{ currentUser.posts_count }}</el-descriptions-item>
        <el-descriptions-item label="发布限制">{{ currentUser.posts_limit }} 条/天</el-descriptions-item>
        <el-descriptions-item label="当前余额">
          <strong style="color: #409EFF;">¥{{ currentUser.balance }}</strong>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">
          {{ formatDate(currentUser.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="累计充值" :span="2">
          <el-tag type="success" size="small">
            ¥{{ currentUser.total_recharge || 0 }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="累计消费" :span="2">
          <el-tag type="warning" size="small">
            ¥{{ currentUser.total_spent || 0 }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="账户状态">
          <el-tag :type="currentUser.is_banned ? 'danger' : 'success'" size="small">
            {{ currentUser.is_banned ? '已封禁' : '正常' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="封禁时间">
          {{ formatDate(currentUser.banned_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="封禁原因" :span="2">
          {{ currentUser.ban_reason || '无' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">最近交易记录</el-divider>

      <el-table :data="currentUserTransactions" style="width: 100%" size="small">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="type_name" label="类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.amount > 0 ? 'success' : 'warning'" size="small">
              {{ scope.row.type_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="scope">
            <span :style="{ color: scope.row.amount > 0 ? '#67C23A' : '#F56C6C' }">
              {{ scope.row.amount > 0 ? '+' : '' }}{{ scope.row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <div v-if="currentUser">
          <el-button
            v-if="!currentUser.is_banned"
            type="danger"
            @click="handleBanDetail"
          >
            封禁用户
          </el-button>
          <el-button
            v-else
            type="success"
            @click="handleUnbanDetail"
          >
            解封用户
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="banReasonVisible" title="封禁原因" width="500px">
      <el-form :model="banForm" label-width="80px">
        <el-form-item label="封禁原因">
          <el-input
            v-model="banForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入封禁原因（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="banReasonVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmBan">确认封禁</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { userApi } from '../services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const banReasonVisible = ref(false)
const pendingBanUser = ref(null)

const banForm = reactive({
  reason: ''
})

const loading = ref(false)
const users = ref([])
const detailVisible = ref(false)
const currentUser = ref(null)
const currentUserTransactions = ref([])

const searchForm = reactive({
  keyword: '',
  level: ''
})

const pagination = reactive({
  page: 1,
  perPage: 20,
  total: 0
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage
    }
    
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    if (searchForm.level) {
      params.level = searchForm.level
    }

    const response = await userApi.getList(params)
    if (response.data.success) {
      users.value = response.data.users
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchUsers()
}

const getLevelTagType = (level) => {
  const levelTypes = {
    bronze: 'info',
    silver: '',
    gold: 'warning',
    black: 'danger',
    diamond: 'success'
  }
  return levelTypes[level] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const viewDetail = async (row) => {
  try {
    const response = await userApi.getById(row.id)
    if (response.data.success) {
      currentUser.value = response.data.user
      currentUserTransactions.value = response.data.transactions || []
      detailVisible.value = true
    }
  } catch (error) {
    console.error('获取用户详情失败:', error)
    ElMessage.error('获取用户详情失败')
  }
}

const handleBan = (row) => {
  pendingBanUser.value = row
  banForm.reason = ''
  banReasonVisible.value = true
}

const handleUnban = async (row) => {
  try {
    await ElMessageBox.confirm('确定要解封该用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await userApi.unban(row.id)
    if (response.data.success) {
      ElMessage.success('用户已解封')
      fetchUsers()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('解封用户失败:', error)
    }
  }
}

const handleBanDetail = () => {
  if (!currentUser.value) return
  pendingBanUser.value = currentUser.value
  banForm.reason = ''
  detailVisible.value = false
  banReasonVisible.value = true
}

const handleUnbanDetail = async () => {
  if (!currentUser.value) return
  
  try {
    await ElMessageBox.confirm('确定要解封该用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await userApi.unban(currentUser.value.id)
    if (response.data.success) {
      ElMessage.success('用户已解封')
      currentUser.value.is_banned = 0
      fetchUsers()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('解封用户失败:', error)
    }
  }
}

const confirmBan = async () => {
  if (!pendingBanUser.value) return

  try {
    const response = await userApi.ban(pendingBanUser.value.id, banForm.reason)
    if (response.data.success) {
      ElMessage.success('用户已封禁')
      banReasonVisible.value = false
      fetchUsers()
    }
  } catch (error) {
    console.error('封禁用户失败:', error)
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-page {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
