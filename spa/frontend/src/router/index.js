import { createRouter, createWebHistory } from 'vue-router'
import LoginView               from '../views/LoginView.vue'
import Issue1XssView           from '../views/Issue1XssView.vue'
import Issue2ClientStorageView from '../views/Issue2ClientStorageView.vue'
import Issue3ThirdPartyView    from '../views/Issue3ThirdPartyView.vue'
import Issue4MonitoringView    from '../views/Issue4MonitoringView.vue'
import Issue5BusinessLogicView from '../views/Issue5BusinessLogicView.vue'

const routes = [
  { path: '/login', component: LoginView },
  {
    path: '/',
    redirect: () => localStorage.getItem('token') ? '/issue-1-xss' : '/login',
  },
  { path: '/issue-1-xss',            component: Issue1XssView,           meta: { requiresAuth: true } },
  { path: '/issue-2-client-storage', component: Issue2ClientStorageView, meta: { requiresAuth: true } },
  { path: '/issue-3-third-party',    component: Issue3ThirdPartyView,    meta: { requiresAuth: true } },
  { path: '/issue-4-monitoring',     component: Issue4MonitoringView,    meta: { requiresAuth: true } },
  { path: '/issue-5-business-logic', component: Issue5BusinessLogicView, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    return '/login'
  }
})

export default router
