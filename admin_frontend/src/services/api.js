import axios from 'axios'
import { ElMessage } from 'element-plus'

const apiClient = axios.create({
  baseURL: '/api/admin',
  timeout: 10000,
  withCredentials: true
})

apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          if (window.location.pathname !== '/login') {
            window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname)
          }
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(error.response.data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (data) => apiClient.post('/auth/login', data),
  logout: () => apiClient.post('/auth/logout'),
  me: () => apiClient.get('/auth/me')
}

export const adminApi = {
  getProfile: () => apiClient.get('/profile'),
  updateProfile: (data) => apiClient.put('/profile', data),
  changePassword: (data) => apiClient.put('/password', data)
}

export const userApi = {
  getList: (params) => apiClient.get('/users', { params }),
  getById: (userId) => apiClient.get(`/users/${userId}`),
  getStats: () => apiClient.get('/users/stats')
}

export const postApi = {
  getList: (params) => apiClient.get('/posts', { params }),
  getById: (postId) => apiClient.get(`/posts/${postId}`),
  hide: (postId, reason) => apiClient.post(`/posts/${postId}/hide`, { reason }),
  unhide: (postId) => apiClient.post(`/posts/${postId}/unhide`),
  getStats: () => apiClient.get('/posts/stats')
}

export const dashboardApi = {
  getDashboard: () => apiClient.get('/dashboard')
}

export default apiClient
