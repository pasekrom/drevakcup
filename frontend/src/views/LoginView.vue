<template>
  <div class="max-w-md mx-auto">
    <div class="card">
      <h1 class="text-2xl font-bold mb-6 text-center">Přihlášení</h1>
      
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="label">Email</label>
          <input
            v-model="email"
            type="email"
            required
            class="input"
            placeholder="vas@email.cz"
          />
        </div>
        
        <div>
          <label class="label">Heslo</label>
          <input
            v-model="password"
            type="password"
            required
            class="input"
            placeholder="••••••••"
          />
        </div>
        
        <div v-if="error" class="text-red-600 text-sm">
          {{ error }}
        </div>
        
        <button
          type="submit"
          :disabled="loading"
          class="btn btn-primary w-full"
        >
          <span v-if="loading">Přihlašování...</span>
          <span v-else>Přihlásit se</span>
        </button>
      </form>
      
      <p class="mt-4 text-sm text-gray-600 text-center">
        Nemáte účet?
        <router-link to="/signup" class="text-primary-600 hover:underline font-medium">
          Zaregistrujte se
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  const result = await authStore.login({
    email: email.value,
    password: password.value,
  })
  
  if (result.success) {
    const redirect = route.query.redirect || '/cups'
    router.push(redirect)
  } else {
    error.value = result.error || 'Přihlášení selhalo'
  }
  
  loading.value = false
}
</script>
