import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'

async function bootstrap() {
  const app = createApp(App)
  const pinia = createPinia()
  app.use(pinia)

  // Resolve session before the router's first navigation so requiresAuth
  // guards see the real user (F5 on /cup/... was redirecting to login).
  const authStore = useAuthStore()
  await authStore.checkAuth()

  app.use(router)
  app.mount('#app')
}

bootstrap()
