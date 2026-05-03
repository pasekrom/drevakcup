<template>
  <div class="max-w-lg">
    <h1 class="text-2xl font-bold mb-6">Přidat turnaj</h1>
    <form @submit.prevent="submit" class="card space-y-4">
      <div>
        <label class="label">Rok *</label>
        <input v-model.number="form.year" type="number" required min="2000" max="2100" class="input" />
      </div>
      <div>
        <label class="label">Místo</label>
        <input v-model="form.location" type="text" class="input" placeholder="např. Praha" />
      </div>
      <div>
        <label class="label">Datum začátku</label>
        <input v-model="form.date_start" type="date" class="input" />
      </div>
      <div>
        <label class="label">Datum konce</label>
        <input v-model="form.date_end" type="date" class="input" />
      </div>
      <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>
      <div class="flex gap-3">
        <button type="submit" :disabled="saving" class="btn btn-primary">
          {{ saving ? 'Ukládám...' : 'Vytvořit turnaj' }}
        </button>
        <router-link to="/admin/cups" class="btn btn-secondary">Zrušit</router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()
const saving = ref(false)
const error = ref('')

const form = reactive({
  year: new Date().getFullYear(),
  location: '',
  date_start: '',
  date_end: '',
})

async function submit() {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      year: form.year,
      location: form.location || '',
      date_start: form.date_start || null,
      date_end: form.date_end || null,
    }
    const res = await api.post('/cups/', payload)
    router.push(`/admin/cups/${res.data.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.year?.[0] || 'Chyba při ukládání.'
  } finally {
    saving.value = false
  }
}
</script>
