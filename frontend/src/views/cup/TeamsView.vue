<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Týmy</h2>
    
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>
    
    <div v-else class="space-y-6">
      <div class="card">
        <h3 class="text-xl font-bold mb-4">Celkové pořadí</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('name')"
                >
                  Tým {{ sortBy === 'name' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('gp')"
                >
                  Z {{ sortBy === 'gp' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('win')"
                >
                  V {{ sortBy === 'win' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('los')"
                >
                  P {{ sortBy === 'los' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('wot')"
                >
                  VOT {{ sortBy === 'wot' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('lot')"
                >
                  POT {{ sortBy === 'lot' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('gf')"
                >
                  GV {{ sortBy === 'gf' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('ga')"
                >
                  GO {{ sortBy === 'ga' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('points')"
                >
                  Body {{ sortBy === 'points' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="team in teamsAll" :key="team.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <TeamWithFlag :team="team" />
                </td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.gp }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.win }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.los }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.wot }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.lot }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.gf }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.ga }}</td>
                <td class="px-6 py-4 whitespace-nowrap font-bold">{{ team.points }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-for="group in ['A', 'B']" :key="group" class="card">
        <h3 class="text-xl font-bold mb-4">Skupina {{ group }}</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('name')"
                >
                  Tým {{ sortBy === 'name' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('gp')"
                >
                  Z {{ sortBy === 'gp' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('win')"
                >
                  V {{ sortBy === 'win' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('los')"
                >
                  P {{ sortBy === 'los' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('wot')"
                >
                  VOT {{ sortBy === 'wot' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('lot')"
                >
                  POT {{ sortBy === 'lot' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('gf')"
                >
                  GV {{ sortBy === 'gf' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('ga')"
                >
                  GO {{ sortBy === 'ga' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
                <th
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  @click="setSort('points')"
                >
                  Body {{ sortBy === 'points' ? (sortDir === 'asc' ? '↑' : '↓') : '' }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="team in teamsByGroup[group]" :key="team.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <TeamWithFlag :team="team" />
                </td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.gp }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.win }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.los }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.wot }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.lot }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.gf }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.ga }}</td>
                <td class="px-6 py-4 whitespace-nowrap font-bold">{{ team.points }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import TeamWithFlag from '../../components/TeamWithFlag.vue'

const props = defineProps({
  cup: {
    type: Object,
    required: true,
  },
})

const teams = ref([])
const loading = ref(true)
const sortBy = ref('points')
const sortDir = ref('desc')

function sortTeamsList(list) {
  const dir = sortDir.value === 'asc' ? 1 : -1
  return [...list].sort((a, b) => {
    let va, vb
    if (sortBy.value === 'name') {
      va = a.name || ''
      vb = b.name || ''
      return dir * (va < vb ? -1 : va > vb ? 1 : 0)
    }
    if (sortBy.value === 'goalDiff') {
      va = (a.gf ?? 0) - (a.ga ?? 0)
      vb = (b.gf ?? 0) - (b.ga ?? 0)
    } else {
      va = Number(a[sortBy.value]) ?? 0
      vb = Number(b[sortBy.value]) ?? 0
    }
    return dir * (va - vb)
  })
}

function setSort(key) {
  if (sortBy.value === key) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else {
    sortBy.value = key
    sortDir.value = (key === 'points' || key === 'gf' || key === 'gp' || key === 'win' || key === 'goalDiff') ? 'desc' : 'asc'
  }
}

const teamsByGroup = computed(() => {
  const grouped = { A: [], B: [] }
  teams.value.forEach(team => {
    if (team.group === 'A' || team.group === 'B') {
      grouped[team.group].push(team)
    }
  })
  grouped.A = sortTeamsList(grouped.A)
  grouped.B = sortTeamsList(grouped.B)
  return grouped
})

const teamsAll = computed(() => sortTeamsList(teams.value.filter(t => t.group === 'A' || t.group === 'B')))

onMounted(async () => {
  try {
    const response = await api.get(`/teams/?cup=${props.cup.id}`)
    teams.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading teams:', error)
  } finally {
    loading.value = false
  }
})
</script>
