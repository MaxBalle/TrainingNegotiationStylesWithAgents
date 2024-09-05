import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },{
      path: '/sandbox',
      name: 'sandbox',
      component: () => import('../views/SandboxView.vue')
    }, {
      path: '/identification',
      name: 'identification',
      component: () => import('../views/IdentificationView.vue')
    }, {
      path: '/turing',
      name: 'turing',
      component: () => import('../views/TuringView.vue')
    }
  ]
})

export default router
