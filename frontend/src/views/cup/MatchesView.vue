<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Zápasy</h2>
    
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>
    
    <div v-else class="overflow-x-auto rounded-lg border border-gray-200">
      <table class="w-full min-w-[32rem] text-left">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th scope="col" class="py-3 px-4 font-semibold text-gray-700">Zápas</th>
            <th scope="col" class="py-3 px-4 font-semibold text-gray-700 whitespace-nowrap">Datum, čas</th>
            <th scope="col" class="py-3 px-4 font-semibold text-gray-700">Skóre</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="match in matches"
            :key="match.id"
            class="border-b border-gray-100 last:border-b-0 hover:bg-gray-50"
          >
            <td class="py-2.5 px-4">
              <span class="flex items-center gap-2">
                <TeamWithFlag :team="match.team_a" />
                <span class="text-gray-400">–</span>
                <TeamWithFlag :team="match.team_b" />
              </span>
            </td>
            <td class="py-2.5 px-4 text-gray-600 whitespace-nowrap">{{ formatDate(match.date) }}, {{ formatTime(match.date) }}</td>
            <td class="py-2.5 px-4 text-lg font-bold tabular-nums">
              <template v-if="finalScore(match) != null">
                {{ finalScore(match).a }} : {{ finalScore(match).b }}
                <span v-if="isOvertime(match)" class="text-xs font-medium text-amber-600 ml-1">OT</span>
              </template>
              <span v-else class="text-gray-400 font-normal">– : –</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
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
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await api.get(`/matches/?cup=${props.cup.id}`)
    matches.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading matches:', error)
  } finally {
    loading.value = false
  }
})

function formatDate(dateString) {
  const d = new Date(dateString)
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  return `${day}/${month}`
}

function formatTime(dateString) {
  const d = new Date(dateString)
  const h = String(d.getHours()).padStart(2, '0')
  const m = String(d.getMinutes()).padStart(2, '0')
  return `${h}:${m}`
}

function finalScore(match) {
  const a = match.score_a_final != null ? match.score_a_final : match.score_a
  const b = match.score_b_final != null ? match.score_b_final : match.score_b
  if (a == null || b == null) return null
  return { a, b }
}

function isOvertime(match) {
  if (match.overtime) return true
  const sa = match.score_a
  const sb = match.score_b
  const fa = match.score_a_final
  const fb = match.score_b_final
  if (sa == null || fa == null) return false
  return sa !== fa || sb !== fb
}
</script>
