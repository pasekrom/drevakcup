<template>
  <div>
    <div class="grid md:grid-cols-2 gap-6 mb-8">
      <div class="card">
        <h2 class="text-xl font-bold mb-4">Rychlý přehled</h2>
        <div class="space-y-2">
          <p><strong>Zápasy:</strong> {{ stats.matches }}</p>
          <p><strong>Týmy:</strong> {{ stats.teams }}</p>
          <p><strong>Moje tipy:</strong> {{ stats.myTips }}</p>
        </div>
      </div>
      
      <div class="card">
        <h2 class="text-xl font-bold mb-4">Moje body</h2>
        <div class="space-y-2">
          <p><strong>Část A:</strong> {{ myPoints.points_a }}</p>
          <p><strong>Část B:</strong> {{ myPoints.points_b }}</p>
          <p><strong>Celkem:</strong> {{ myPoints.points_c }}</p>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 class="text-xl font-bold mb-4">Nadcházející zápasy</h2>
      <div v-if="upcomingMatches.length === 0" class="text-gray-600">
        Žádné nadcházející zápasy
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="match in upcomingMatches"
          :key="match.id"
          class="border-b border-gray-200 pb-4"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium"><TeamWithFlag :team="match.team_a" /> vs <TeamWithFlag :team="match.team_b" /></p>
              <p class="text-sm text-gray-600">{{ formatDateTime(match.date) }}</p>
            </div>
            <router-link
              :to="`/cup/${cup.year}/matches`"
              class="btn btn-secondary text-sm"
            >
              Zobrazit
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../services/api'
import TeamWithFlag from '../../components/TeamWithFlag.vue'

const props = defineProps({
  cup: {
    type: Object,
    required: true,
  },
})

const authStore = useAuthStore()
const stats = ref({ matches: 0, teams: 0, myTips: 0 })
const myPoints = ref({ points_a: 0, points_b: 0, points_c: 0 })
const upcomingMatches = ref([])

onMounted(async () => {
  await loadData()
})

async function loadData() {
  try {
    // Load matches
    const matchesResponse = await api.get(`/matches/?cup=${props.cup.id}`)
    const matches = matchesResponse.data.results || matchesResponse.data
    stats.value.matches = matches.length
    
    // Load teams
    const teamsResponse = await api.get(`/teams/?cup=${props.cup.id}`)
    const teams = teamsResponse.data.results || teamsResponse.data
    stats.value.teams = teams.length
    
    // Load my tips
    const tipsResponse = await api.get(`/match-tips/by_cup/?cup=${props.cup.id}`)
    stats.value.myTips = tipsResponse.data.length
    
    // Load my points
    const pointsResponse = await api.get(`/user-points/?cup=${props.cup.id}`)
    const points = pointsResponse.data.results || pointsResponse.data
    points.forEach(point => {
      if (point.part === 'A') myPoints.value.points_a = point.points
      if (point.part === 'B') myPoints.value.points_b = point.points
      if (point.part === 'C') myPoints.value.points_c = point.points
    })
    
    // Load upcoming matches
    const now = new Date()
    upcomingMatches.value = matches
      .filter(m => new Date(m.date) > now)
      .slice(0, 5)
  } catch (error) {
    console.error('Error loading data:', error)
  }
}

function formatDateTime(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString('cs-CZ')
}
</script>
