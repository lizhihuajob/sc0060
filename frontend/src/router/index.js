import { createRouter, createWebHistory } from 'vue-router'
import { authApi } from '../services/api'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册', guestOnly: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/my-posts',
    name: 'MyPosts',
    component: () => import('../views/MyPosts.vue'),
    meta: { title: '我的发布', requiresAuth: true }
  },
  {
    path: '/new-post',
    name: 'NewPost',
    component: () => import('../views/NewPost.vue'),
    meta: { title: '发布信息' }
  },
  {
    path: '/post/:id',
    name: 'PostDetail',
    component: () => import('../views/PostDetail.vue'),
    meta: { title: '详情' }
  },
  {
    path: '/recharge',
    name: 'Recharge',
    component: () => import('../views/Recharge.vue'),
    meta: { title: '充值', requiresAuth: true }
  },
  {
    path: '/upgrade',
    name: 'Upgrade',
    component: () => import('../views/Upgrade.vue'),
    meta: { title: '升级会员', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 信息发布平台` : '信息发布平台'
  
  const isAuthenticated = await checkAuth()
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.guestOnly && isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

async function checkAuth() {
  const token = localStorage.getItem('token')
  if (!token) {
    return false
  }
  
  try {
    const response = await authApi.me()
    return response.data.success
  } catch {
    return false
  }
}

export default router
