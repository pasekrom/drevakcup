<template>
  <div>
    <h1 class="text-3xl font-bold mb-8">Turnaje</h1>
    
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>
    
    <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <router-link
        v-for="cup in cups"
        :key="cup.id"
        :to="`/cup/${cup.year}`"
        class="card hover:shadow-lg transition-shadow block"
      >
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold">{{ cup.year }}</h2>
          <span v-if="cup.logo" class="text-4xl">🏒</span>
        </div>
        <p class="text-gray-600 mb-2">{{ cup.location }}</p>
        <p class="text-sm text-gray-500">
          {{ formatDate(cup.date_start) }} - {{ formatDate(cup.date_end) }}
        </p>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const cups = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await api.get('/cups/')
    cups.value = response.data.results || response.data
    if (!Array.isArray(cups.value)) {
      cups.value = cups.value ? [cups.value] : []
    }
  } catch (error) {
    console.error('Error fetching cups:', error)
    cups.value = []
  } finally {
    loading.value = false
  }
})

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('cs-CZ')
}
</script>
