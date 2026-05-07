import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/cups',
    name: 'cups',
    component: () => import('../views/CupsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/cup/:year',
    name: 'cup-detail',
    component: () => import('../views/CupDetailView.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'cup-home',
        component: () => import('../views/cup/HomeView.vue'),
      },
      {
        path: 'matches',
        name: 'cup-matches',
        component: () => import('../views/cup/MatchesView.vue'),
      },
      {
        path: 'tips',
        name: 'cup-tips',
        component: () => import('../views/cup/MatchTipsView.vue'),
      },
      {
        path: 'special-tips',
        name: 'cup-special-tips',
        component: () => import('../views/cup/SpecialTipsView.vue'),
      },
      {
        path: 'teams',
        name: 'cup-teams',
        component: () => import('../views/cup/TeamsView.vue'),
      },
      {
        path: 'playoff',
        name: 'cup-playoff',
        component: () => import('../views/cup/PlayoffView.vue'),
      },
      {
        path: 'tips-overview',
        name: 'cup-tips-overview',
        component: () => import('../views/cup/TipsOverviewView.vue'),
      },
      {
        path: 'ladder',
        name: 'cup-ladder',
        component: () => import('../views/cup/LadderView.vue'),
      },
      {
        path: 'rules',
        name: 'cup-rules',
        component: () => import('../views/cup/RulesView.vue'),
      },
    ],
  },
  {
    path: '/cup/:year/tips-overview/excel',
    name: 'cup-tips-overview-excel',
    component: () => import('../views/cup/TipsOverviewExcelView.vue'),
    meta: { requiresAuth: true, layout: 'blank' },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/signup',
    name: 'signup',
    component: () => import('../views/SignupView.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/SettingsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    redirect: '/admin/cups',
  },
  {
    path: '/admin/cups',
    name: 'admin-cups',
    component: () => import('../views/admin/AdminCupsView.vue'),
    meta: { requiresAuth: true, requiresStaff: true },
  },
  {
    path: '/admin/cups/new',
    name: 'admin-cup-new',
    component: () => import('../views/admin/AdminCupFormView.vue'),
    meta: { requiresAuth: true, requiresStaff: true },
  },
  {
    path: '/admin/cups/:id',
    name: 'admin-cup-detail',
    component: () => import('../views/admin/AdminCupDetailView.vue'),
    meta: { requiresAuth: true, requiresStaff: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresStaff && !authStore.user?.is_staff) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
