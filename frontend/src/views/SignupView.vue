<template>
  <div class="max-w-md mx-auto">
    <div class="card">
      <h1 class="text-2xl font-bold mb-6 text-center">Registrace</h1>
      
      <form @submit.prevent="handleSignup" class="space-y-4">
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
          <label class="label">Jméno (nepovinné)</label>
          <input
            v-model="name"
            type="text"
            class="input"
            placeholder="Vaše jméno"
          />
        </div>
        
        <div>
          <label class="label">Heslo (min. 8 znaků)</label>
          <input
            v-model="password"
            type="password"
            required
            minlength="8"
            class="input"
            placeholder="••••••••"
          />
        </div>
        
        <div>
          <label class="label">Heslo znovu</label>
          <input
            v-model="passwordConfirm"
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
          <span v-if="loading">Vytváření účtu...</span>
          <span v-else>Zaregistrovat se</span>
        </button>
      </form>
      
      <p class="mt-4 text-sm text-gray-600 text-center">
        Už máte účet?
        <router-link to="/login" class="text-primary-600 hover:underline font-medium">
          Přihlásit se
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const name = ref('')
const password = ref('')
const passwordConfirm = ref('')
const loading = ref(false)
const error = ref('')

async function handleSignup() {
  if (password.value !== passwordConfirm.value) {
    error.value = 'Hesla se neshodují.'
    return
  }
  if (password.value.length < 8) {
    error.value = 'Heslo musí mít alespoň 8 znaků.'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const response = await api.post('/auth/signup/', {
      email: email.value,
      name: name.value,
      password: password.value,
    })
    authStore.user = response.data.user
    router.push('/cups')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registrace selhala.'
  } finally {
    loading.value = false
  }
}
</script>
