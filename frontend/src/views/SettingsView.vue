<template>
  <div class="max-w-lg mx-auto">
    <h1 class="text-2xl font-bold mb-6">Nastavení účtu</h1>

    <!-- Profile section -->
    <div class="card mb-6">
      <h2 class="text-lg font-semibold mb-4">Profil</h2>
      <form @submit.prevent="saveProfile" class="space-y-4">
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0">
            <div
              class="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden border-2 border-gray-200"
            >
              <img
                v-if="avatarPreview || user?.avatar_url"
                :src="avatarPreview || user?.avatar_url"
                alt="Avatar"
                class="w-full h-full object-cover"
              />
              <span v-else class="text-2xl text-gray-500 font-medium">
                {{ (user?.name || user?.email || '?').charAt(0).toUpperCase() }}
              </span>
            </div>
            <div class="mt-2 flex flex-col items-center gap-1">
              <label>
                <span class="text-sm text-primary-600 hover:underline cursor-pointer">Změnit</span>
                <input
                  type="file"
                  accept="image/*"
                  class="hidden"
                  @change="onAvatarChange"
                />
              </label>
              <button
                v-if="user?.avatar_url || avatarPreview"
                type="button"
                @click="clearAvatar"
                class="text-xs text-gray-500 hover:text-red-600"
              >
                Odebrat
              </button>
            </div>
          </div>
          <div class="flex-1 min-w-0 space-y-4">
            <div>
              <label class="label">Email</label>
              <input
                :value="user?.email"
                type="email"
                disabled
                class="input bg-gray-100 cursor-not-allowed"
              />
              <p class="text-xs text-gray-500 mt-1">Email nelze změnit.</p>
            </div>
            <div>
              <label class="label">Zobrazované jméno (uživatelské jméno)</label>
              <input
                v-model="form.name"
                type="text"
                maxlength="30"
                class="input"
                placeholder="Např. Jan Novák"
              />
              <p class="text-xs text-gray-500 mt-1">Zobrazuje se v žebříčku a v menu.</p>
            </div>
          </div>
        </div>
        <div v-if="profileMessage" :class="profileSuccess ? 'text-green-600' : 'text-red-600'" class="text-sm">
          {{ profileMessage }}
        </div>
        <button type="submit" :disabled="profileSaving" class="btn btn-primary">
          {{ profileSaving ? 'Ukládám...' : 'Uložit profil' }}
        </button>
      </form>
    </div>

    <!-- Password section -->
    <div class="card">
      <h2 class="text-lg font-semibold mb-4">Změna hesla</h2>
      <form @submit.prevent="changePassword" class="space-y-4">
        <div>
          <label class="label">Současné heslo</label>
          <input
            v-model="passwordForm.current"
            type="password"
            required
            class="input"
            placeholder="••••••••"
          />
        </div>
        <div>
          <label class="label">Nové heslo</label>
          <input
            v-model="passwordForm.new"
            type="password"
            required
            minlength="8"
            class="input"
            placeholder="••••••••"
          />
          <p class="text-xs text-gray-500 mt-1">Min. 8 znaků.</p>
        </div>
        <div>
          <label class="label">Nové heslo znovu</label>
          <input
            v-model="passwordForm.confirm"
            type="password"
            required
            class="input"
            placeholder="••••••••"
          />
        </div>
        <div v-if="passwordMessage" :class="passwordSuccess ? 'text-green-600' : 'text-red-600'" class="text-sm">
          {{ passwordMessage }}
        </div>
        <button type="submit" :disabled="passwordSaving" class="btn btn-primary">
          {{ passwordSaving ? 'Měním...' : 'Změnit heslo' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const user = ref(null)
const form = reactive({ name: '' })
const avatarFile = ref(null)
const avatarPreview = ref(null)
const clearAvatarRequested = ref(false)
const profileSaving = ref(false)
const profileMessage = ref('')
const profileSuccess = ref(false)

const passwordForm = reactive({ current: '', new: '', confirm: '' })
const passwordSaving = ref(false)
const passwordMessage = ref('')
const passwordSuccess = ref(false)

onMounted(async () => {
  await authStore.checkAuth()
  user.value = authStore.user
  if (user.value) {
    form.name = user.value.name || ''
  }
})

watch(() => authStore.user, (u) => {
  user.value = u
  if (u) form.name = u.name || ''
}, { immediate: true })

function onAvatarChange(e) {
  const file = e.target?.files?.[0]
  if (!file) return
  avatarFile.value = file
  clearAvatarRequested.value = false
  const reader = new FileReader()
  reader.onload = () => { avatarPreview.value = reader.result }
  reader.readAsDataURL(file)
}

function clearAvatar() {
  avatarFile.value = null
  avatarPreview.value = null
  clearAvatarRequested.value = true
}

async function saveProfile() {
  profileMessage.value = ''
  profileSaving.value = true
  try {
    const body = new FormData()
    body.append('name', form.name)
    if (avatarFile.value) {
      body.append('avatar', avatarFile.value)
    }
    if (clearAvatarRequested.value) {
      body.append('clear_avatar', 'true')
    }
    const response = await api.patch('/auth/user/', body)
    authStore.user = response.data
    user.value = response.data
    avatarFile.value = null
    avatarPreview.value = null
    clearAvatarRequested.value = false
    profileSuccess.value = true
    profileMessage.value = 'Profil byl uložen.'
  } catch (err) {
    profileSuccess.value = false
    profileMessage.value = err.response?.data?.detail || 'Uložení profilu se nezdařilo.'
  } finally {
    profileSaving.value = false
  }
}

async function changePassword() {
  passwordMessage.value = ''
  if (passwordForm.new !== passwordForm.confirm) {
    passwordMessage.value = 'Nové heslo a potvrzení se neshodují.'
    passwordSuccess.value = false
    return
  }
  if (passwordForm.new.length < 8) {
    passwordMessage.value = 'Nové heslo musí mít alespoň 8 znaků.'
    passwordSuccess.value = false
    return
  }
  passwordSaving.value = true
  try {
    await api.post('/auth/change-password/', {
      current_password: passwordForm.current,
      new_password: passwordForm.new,
    })
    passwordSuccess.value = true
    passwordMessage.value = 'Heslo bylo změněno.'
    passwordForm.current = ''
    passwordForm.new = ''
    passwordForm.confirm = ''
  } catch (err) {
    passwordSuccess.value = false
    passwordMessage.value = err.response?.data?.detail || 'Změna hesla se nezdařila.'
  } finally {
    passwordSaving.value = false
  }
}
</script>
