<template>
  <div class="max-w-4xl mx-auto">
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">
        Drevak Cup
      </h1>
      <p class="text-xl text-gray-600">
        IIHF Tournament Prediction Platform
      </p>
    </div>

    <div v-if="currentCup" class="card mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold mb-2">
            {{ currentCup.year }} - {{ currentCup.location }}
          </h2>
          <p class="text-gray-600">
            {{ formatDate(currentCup.date_start) }} - {{ formatDate(currentCup.date_end) }}
          </p>
        </div>
        <router-link
          :to="`/cup/${currentCup.year}`"
          class="btn btn-primary"
        >
          Zobrazit turnaj
        </router-link>
      </div>
    </div>

    <div class="grid md:grid-cols-2 gap-6">
      <div class="card">
        <h3 class="text-xl font-bold mb-4">O aplikaci</h3>
        <p class="text-gray-700">
          Drevak Cup je platforma pro předpovídání výsledků IIHF turnajů.
          Sázejte na své oblíbené týmy, předpovídejte skóre a soutěžte
          s přáteli o nejlepší předpovědi.
        </p>
      </div>

      <div class="card">
        <h3 class="text-xl font-bold mb-4">Jak to funguje?</h3>
        <ul class="space-y-2 text-gray-700">
          <li>• Předpovídejte výsledky jednotlivých zápasů</li>
          <li>• Vyplňte speciální tipy (vítěz, finalisté, skupiny)</li>
          <li>• Sledujte žebříček a soutěžte s ostatními</li>
          <li>• Získejte body za správné předpovědi</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const currentCup = ref(null)

onMounted(async () => {
  try {
    const response = await api.get('/cups/current/')
    currentCup.value = response.data
  } catch (error) {
    console.error('Error fetching current cup:', error)
  }
})

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('cs-CZ')
}
</script>
