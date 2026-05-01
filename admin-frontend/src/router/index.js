import { createRouter, createWebHistory } from 'vue-router'
import { adminApi } from '../services/api'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '管理员登录', guestOnly: true }
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘', requiresAuth: true }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { title: '用户管理', requiresAuth: true }
      },
      {
        path: 'posts',
        name: 'Posts',
        component: () => import('../views/Posts.vue'),
        meta: { title: '内容管理', requiresAuth: true }
      },
      {
        path: 'tags',
        name: 'Tags',
        component: () => import('../views/Tags.vue'),
        meta: { title: '标签管理', requiresAuth: true }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue'),
        meta: { title: '系统设置', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

let authChecked = false

router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 后台管理系统` : '后台管理系统'
  
  const isAuthenticated = localStorage.getItem('admin_auth') === 'true'
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    try {
      const response = await adminApi.getMe()
      if (response.data.success) {
        localStorage.setItem('admin_auth', 'true')
        next()
      } else {
        localStorage.removeItem('admin_auth')
        localStorage.removeItem('admin')
        next({ name: 'Login', query: { redirect: to.fullPath } })
      }
    } catch {
      localStorage.removeItem('admin_auth')
      localStorage.removeItem('admin')
      next({ name: 'Login', query: { redirect: to.fullPath } })
    }
  } else if (to.meta.guestOnly && isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
