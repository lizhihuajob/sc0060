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
  getMy: (params) => apiClient.get('/posts/my', { params }),
  getById: (id) => apiClient.get(`/posts/${id}`),
  create: (data) => apiClient.post('/posts', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  update: (id, data) => apiClient.put(`/posts/${id}`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  delete: (id) => apiClient.delete(`/posts/${id}`)
}

export const userApi = {
  getProfile: () => apiClient.get('/user/profile'),
  recharge: (amount) => apiClient.post('/user/recharge', { amount }),
  upgrade: (targetLevel) => apiClient.post('/user/upgrade', { target_level: targetLevel })
}

export const configApi = {
  getMembership: () => apiClient.get('/config/membership')
}

export default apiClient
