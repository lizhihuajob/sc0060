import { createRouter, createWebHistory } from 'vue-router'
import { useAdminStore } from '../stores/adminStore'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表板' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'posts',
        name: 'Posts',
        component: () => import('../views/Posts.vue'),
        meta: { title: '公告管理' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('../views/Reports.vue'),
        meta: { title: '举报管理' }
      },
      {
        path: 'announcements',
        name: 'Announcements',
        component: () => import('../views/Announcements.vue'),
        meta: { title: '系统公告' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { title: '个人设置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const adminStore = useAdminStore()
  
  document.title = to.meta.title ? `${to.meta.title} - 后台管理系统` : '后台管理系统'
  
  if (to.meta.requiresAuth !== false) {
    if (!adminStore.isLoggedIn) {
      try {
        await adminStore.fetchAdmin()
        if (!adminStore.isLoggedIn) {
          next({ path: '/login', query: { redirect: to.fullPath } })
          return
        }
      } catch (error) {
        next({ path: '/login', query: { redirect: to.fullPath } })
        return
      }
    }
  }
  
  if (to.path === '/login' && adminStore.isLoggedIn) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router
