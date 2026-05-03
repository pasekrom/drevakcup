<template>
  <nav class="bg-white shadow-lg">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center space-x-8">
          <router-link to="/" class="text-xl font-bold text-primary-600">
            Drevak Cup
          </router-link>
          <router-link
            v-if="authStore.isAuthenticated"
            to="/cups"
            class="text-gray-700 hover:text-primary-600 transition-colors"
          >
            Turnaje
          </router-link>
          <router-link
            v-if="authStore.user?.is_staff"
            to="/admin/cups"
            class="text-gray-700 hover:text-primary-600 transition-colors"
          >
            Správa
          </router-link>
        </div>
        
        <div class="flex items-center space-x-4">
          <template v-if="authStore.isAuthenticated">
            <div class="relative" ref="userMenuRef">
              <button
                type="button"
                @click="userMenuOpen = !userMenuOpen"
                class="flex items-center gap-2 rounded-lg px-3 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
              >
                <span class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center overflow-hidden flex-shrink-0">
                  <img
                    v-if="authStore.user?.avatar_url"
                    :src="authStore.user.avatar_url"
                    alt=""
                    class="w-full h-full object-cover"
                  />
                  <span v-else class="text-sm font-medium text-primary-700">
                    {{ displayInitial }}
                  </span>
                </span>
                <span class="max-w-[120px] truncate">{{ displayName }}</span>
                <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div
                v-if="userMenuOpen"
                class="absolute right-0 mt-1 w-48 py-1 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
              >
                <router-link
                  to="/settings"
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  @click="userMenuOpen = false"
                >
                  Nastavení
                </router-link>
                <button
                  type="button"
                  @click="handleLogout"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Odhlásit se
                </button>
              </div>
            </div>
          </template>
          <template v-else>
            <router-link to="/signup" class="text-gray-700 hover:text-primary-600 transition-colors">
              Registrace
            </router-link>
            <router-link to="/login" class="btn btn-primary">
              Přihlásit se
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const userMenuOpen = ref(false)
const userMenuRef = ref(null)

const displayName = computed(() => {
  const u = authStore.user
  if (!u) return ''
  return (u.display_name || u.name || u.email || '').trim() || u.email
})

const displayInitial = computed(() => {
  const n = displayName.value
  return n ? n.charAt(0).toUpperCase() : '?'
})

function onClickOutside(e) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    userMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
})
onUnmounted(() => {
  document.removeEventListener('click', onClickOutside)
})

async function handleLogout() {
  userMenuOpen.value = false
  await authStore.logout()
  router.push('/')
}
</script>
