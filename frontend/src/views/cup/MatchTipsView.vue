<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Moje tipy</h2>
    
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>
    
    <form v-else @submit.prevent="handleSubmit" class="space-y-6">
      <div
        v-for="match in matches"
        :key="match.id"
        class="card"
      >
        <div class="mb-4">
          <p class="font-medium mb-1">
            <TeamWithFlag :team="match.team_a" /> vs <TeamWithFlag :team="match.team_b" />
          </p>
          <p class="text-sm text-gray-600">{{ formatDateTime(match.date) }}</p>
          <p v-if="match.has_started" class="text-sm text-red-600 mt-2">
            Zápas již začal - nelze upravit tip
          </p>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label"><TeamWithFlag :team="match.team_a" /></label>
            <input
              v-model.number="tips[match.id].score_a"
              type="number"
              min="0"
              :disabled="match.has_started"
              class="input"
            />
          </div>
          <div>
            <label class="label"><TeamWithFlag :team="match.team_b" /></label>
            <input
              v-model.number="tips[match.id].score_b"
              type="number"
              min="0"
              :disabled="match.has_started"
              class="input"
            />
          </div>
        </div>
      </div>
      
      <div class="flex justify-end">
        <button
          type="submit"
          :disabled="saving"
          class="btn btn-primary"
        >
          <span v-if="saving">Ukládání...</span>
          <span v-else>Uložit tipy</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import TeamWithFlag from '../../components/TeamWithFlag.vue'

const props = defineProps({
  cup: {
    type: Object,
    required: true,
  },
})

const matches = ref([])
const tips = ref({})
const loading = ref(true)
const saving = ref(false)

onMounted(async () => {
  await loadData()
})

async function loadData() {
  try {
    // Load matches
    const matchesResponse = await api.get(`/matches/?cup=${props.cup.id}`)
    matches.value = matchesResponse.data.results || matchesResponse.data
    
    // Load existing tips
    const tipsResponse = await api.get(`/match-tips/by_cup/?cup=${props.cup.id}`)
    const existingTips = tipsResponse.data
    
    // Initialize tips object
    matches.value.forEach(match => {
      const existingTip = existingTips.find(t => t.match.id === match.id)
      tips.value[match.id] = {
        score_a: existingTip?.score_a ?? null,
        score_b: existingTip?.score_b ?? null,
      }
    })
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  saving.value = true
  try {
    const tipsArray = Object.entries(tips.value)
      .map(([matchId, tip]) => ({
        match_id: parseInt(matchId, 10),
        score_a: tip.score_a != null && !Number.isNaN(Number(tip.score_a)) ? Number(tip.score_a) : null,
        score_b: tip.score_b != null && !Number.isNaN(Number(tip.score_b)) ? Number(tip.score_b) : null,
      }))
      .filter(t => t.score_a !== null && t.score_b !== null)
    
    await api.post('/match-tips/bulk_update/', { tips: tipsArray })
    alert('Tipy byly úspěšně uloženy!')
  } catch (error) {
    console.error('Error saving tips:', error)
    alert(error.response?.data?.detail || 'Chyba při ukládání tipů')
  } finally {
    saving.value = false
  }
}

function formatDateTime(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString('cs-CZ')
}
</script>
