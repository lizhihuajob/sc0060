import axios from 'axios'
import { ElMessage } from 'element-plus'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true
})

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
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
          localStorage.removeItem('token')
          localStorage.removeItem('user')
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
  me: () => apiClient.get('/auth/me'),
  login: (data) => apiClient.post('/auth/login', data),
  register: (data) => apiClient.post('/auth/register', data),
  logout: () => apiClient.post('/auth/logout')
}

export const postApi = {
  getList: (params) => apiClient.get('/posts', { params }),
  search: (params) => apiClient.get('/posts', { params }),
  getPinned: () => apiClient.get('/posts/pinned'),
  getMy: (params) => apiClient.get('/posts/my', { params }),
  getById: (id) => apiClient.get(`/posts/${id}`),
  create: (data) => apiClient.post('/posts', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  update: (id, data) => apiClient.put(`/posts/${id}`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  delete: (id) => apiClient.delete(`/posts/${id}`),
  pin: (id) => apiClient.post(`/posts/${id}/pin`),
  toggleFavorite: (id) => apiClient.post(`/posts/${id}/favorite`),
  getComments: (postId, params) => apiClient.get(`/posts/${postId}/comments`, { params }),
  createComment: (postId, data) => apiClient.post(`/posts/${postId}/comments`, data),
  deleteComment: (postId, commentId) => apiClient.delete(`/posts/${postId}/comments/${commentId}`)
}

export const userApi = {
  getProfile: () => apiClient.get('/user/profile'),
  getFavorites: (params) => apiClient.get('/user/favorites', { params }),
  getEditLogs: (params) => apiClient.get('/user/edit-logs', { params }),
  recharge: (amount) => apiClient.post('/user/recharge', { amount }),
  upgrade: (targetLevel) => apiClient.post('/user/upgrade', { target_level: targetLevel }),
  uploadAvatar: (data) => apiClient.post('/user/avatar', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  changePassword: (data) => apiClient.put('/user/password', data)
}

export const configApi = {
  getMembership: () => apiClient.get('/config')
}

export const reportApi = {
  create: (data) => apiClient.post('/reports', data),
  getMy: (params) => apiClient.get('/reports/my', { params })
}

export const announcementApi = {
  getActive: (params) => apiClient.get('/announcements', { params }),
  getPinned: () => apiClient.get('/announcements/pinned'),
  getById: (id) => apiClient.get(`/announcements/${id}`)
}

export const tagApi = {
  getAll: () => apiClient.get('/tags')
}

export default apiClient
