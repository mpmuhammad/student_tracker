import { createRouter, createWebHistory } from 'vue-router'
import { session, loadSession } from './session'

const routes = [
  {
    path: '/',
    name: 'Students',
    component: () => import('./pages/Students.vue'),
  },
  {
    path: '/student/:name',
    name: 'Student',
    component: () => import('./pages/StudentDetail.vue'),
    props: true,
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./pages/Login.vue'),
    meta: { public: true },
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory('/mentor'),
  routes,
})

router.beforeEach(async (to) => {
  if (!session.loaded) await loadSession()
  if (to.meta.public) {
    if (to.name === 'Login' && session.isLoggedIn && session.isMentor) {
      return { name: 'Students' }
    }
    return true
  }
  if (!session.isLoggedIn) return { name: 'Login' }
  return true
})

export default router
