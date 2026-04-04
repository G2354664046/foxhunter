import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Results from '../views/Results.vue'
import Samples from '../views/Samples.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/samples',
    name: 'Samples',
    component: Samples,
    meta: { requiresAuth: true }
  },
  {
    path: '/results/:id',
    name: 'Results',
    component: Results,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    // redirect backwards compatible link into unified login component
    redirect: to => ({ path: '/login', query: { mode: 'register' } })
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  if (!to.meta?.requiresAuth) return true
  // 仅展示 sessionStorage 中的 URL/哈希预览，不调用需登录的 API
  if (to.name === 'Results' && to.params.id === 'preview') return true
  const token = localStorage.getItem('access_token')
  if (token) return true
  return { name: 'Login', query: { redirect: to.fullPath } }
})

export default router