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
          localStorage.removeItem('admin_auth')
          localStorage.removeItem('admin')
          window.location.href = '/login'
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

export const adminApi = {
  login: (data) => apiClient.post('/auth/login', data),
  logout: () => apiClient.post('/auth/logout'),
  getMe: () => apiClient.get('/auth/me'),
  updateProfile: (data) => apiClient.put('/profile', data),
  changePassword: (data) => apiClient.put('/password', data),
  
  getDashboard: () => apiClient.get('/dashboard'),
  
  getUsers: (params) => apiClient.get('/users', { params }),
  getUser: (userId) => apiClient.get(`/users/${userId}`),
  getUsersStats: () => apiClient.get('/users/stats'),
  
  getPosts: (params) => apiClient.get('/posts', { params }),
  getPost: (postId) => apiClient.get(`/posts/${postId}`),
  hidePost: (postId, data) => apiClient.post(`/posts/${postId}/hide`, data),
  unhidePost: (postId) => apiClient.post(`/posts/${postId}/unhide`),
  getPostsStats: () => apiClient.get('/posts/stats'),
  
  getTags: (params) => apiClient.get('/tags', { params }),
  getAllTags: () => apiClient.get('/tags/all'),
  getTag: (tagId) => apiClient.get(`/tags/${tagId}`),
  createTag: (data) => apiClient.post('/tags', data),
  updateTag: (tagId, data) => apiClient.put(`/tags/${tagId}`, data),
  deleteTag: (tagId) => apiClient.delete(`/tags/${tagId}`)
}

export default apiClient
