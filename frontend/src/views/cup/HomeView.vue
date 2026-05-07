<template>
  <div>
    <div
      v-if="!cup?.tournament_started && (incompleteMatchTipsCount > 0 || incompleteSpecialTipsCount > 0)"
      class="space-y-3 mb-6"
    >
      <div
        v-if="incompleteMatchTipsCount > 0"
        class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950 shadow-sm"
      >
        <p class="font-medium text-amber-900">
          Tipy na zápasy: nevyplněno <strong>{{ incompleteMatchTipsCount }}</strong> z
          {{ stats.matches }} zápasů.
        </p>
        <p class="mt-1 text-amber-800/90">
          Před začátkem prvního zápasu turnaje je potřeba mít tip na každý zápas.
        </p>
        <router-link
          :to="`/cup/${cup.year}/tips`"
          class="btn btn-primary text-sm mt-3 inline-flex"
        >
          Vyplnit tipy na zápasy
        </router-link>
      </div>
      <div
        v-if="incompleteSpecialTipsCount > 0"
        class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950 shadow-sm"
      >
        <p class="font-medium text-amber-900">
          Speciální tipy: nevyplněno <strong>{{ incompleteSpecialTipsCount }}</strong> z
          {{ SPECIAL_TOTAL_FIELDS }} položek.
        </p>
        <p class="mt-1 text-amber-800/90">
          Doplň všechna pole a ulož je na stránce speciálních tipů.
        </p>
        <router-link
          :to="`/cup/${cup.year}/special-tips`"
          class="btn btn-primary text-sm mt-3 inline-flex"
        >
          Vyplnit speciální tipy
        </router-link>
      </div>
    </div>

    <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-end gap-3">
      <router-link
        :to="`/cup/${cup.year}/tips-overview/excel`"
        target="_blank"
        rel="noopener"
        class="btn btn-danger w-full sm:w-auto text-center inline-flex items-center justify-center py-3"
      >
        Excel přehled tipů
      </router-link>
      <p class="text-xs text-gray-500 sm:text-sm sm:ml-2 sm:max-w-[22rem]">
        Kompletní tabulka tipů všech hráčů (velký přehled, scroll oběma směry).
      </p>
    </div>

    <div class="grid md:grid-cols-2 gap-6 mb-8">
      <div class="card">
        <h2 class="text-xl font-bold mb-4">Rychlý přehled</h2>
        <div class="space-y-2">
          <p><strong>Zápasy:</strong> {{ stats.matches }}</p>
          <p><strong>Týmy:</strong> {{ stats.teams }}</p>
          <p><strong>Vyplnění tipů:</strong> {{ stats.myTips }}</p>
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
          class="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0"
        >
          <div class="min-w-0">
            <p class="font-medium">
              <TeamWithFlag :team="match.team_a" /> vs <TeamWithFlag :team="match.team_b" />
            </p>
            <p class="text-sm text-gray-600">{{ formatDateTime(match.date) }}</p>
            <p class="mt-1.5 text-sm">
              <span class="text-gray-500">Můj tip:</span>
              <span
                v-if="myTipText(match.id)"
                class="ml-1 font-semibold tabular-nums text-primary-700"
              >{{ myTipText(match.id) }}</span>
              <span v-else class="ml-1 text-gray-400">—</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import TeamWithFlag from '../../components/TeamWithFlag.vue'

/** Stejná množina položek jako ve SpecialTipsView (GET vrací vnořené týmy pod těmito klíči). */
const SPECIAL_TEAM_KEYS = [
  'winner',
  'final_a',
  'final_b',
  'bronze_a',
  'bronze_b',
  'group_a_1',
  'group_a_2',
  'group_a_3',
  'group_a_4',
  'group_b_1',
  'group_b_2',
  'group_b_3',
  'group_b_4',
  'team_most_goals',
  'team_least_goals',
  'team_first_goal',
  'team_last_goal',
  'team_drop_a',
  'team_drop_b',
]

function countIncompleteSpecialFields(tip) {
  let n = 0
  for (const k of SPECIAL_TEAM_KEYS) {
    const t = tip?.[k]
    if (!t || t.id == null) n++
  }
  if (!(String(tip?.czech_shooter_first ?? '').trim())) n++
  if (!(String(tip?.czech_shooter_last ?? '').trim())) n++
  const mg = tip?.max_goals_per_game
  if (mg == null || Number.isNaN(Number(mg))) n++
  const ot = tip?.overtimes
  if (ot == null || Number.isNaN(Number(ot))) n++
  return n
}

const SPECIAL_TOTAL_FIELDS =
  SPECIAL_TEAM_KEYS.length + 2 /* střelci */ + 2 /* čísla */

const props = defineProps({
  cup: {
    type: Object,
    required: true,
  },
})

const stats = ref({ matches: 0, teams: 0, myTips: 0 })
const myPoints = ref({ points_a: 0, points_b: 0, points_c: 0 })
const upcomingMatches = ref([])
const tipsByMatchId = ref({})
const allMatches = ref([])
const specialTipRecord = ref(null)

const incompleteMatchTipsCount = computed(() => {
  if (props.cup?.tournament_started) return 0
  let n = 0
  for (const m of allMatches.value) {
    const t = tipsByMatchId.value[m.id]
    if (!t || t.score_a == null || t.score_b == null) n++
  }
  return n
})

const incompleteSpecialTipsCount = computed(() => {
  if (props.cup?.tournament_started) return 0
  return countIncompleteSpecialFields(specialTipRecord.value)
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  try {
    const [
      matchesResponse,
      teamsResponse,
      tipsResponse,
      pointsResponse,
      upcomingRes,
      specialRes,
    ] = await Promise.all([
      api.get(`/matches/?cup=${props.cup.id}`),
      api.get(`/teams/?cup=${props.cup.id}`),
      api.get(`/match-tips/by_cup/?cup=${props.cup.id}`),
      api.get(`/user-points/?cup=${props.cup.id}`),
      api.get(`/matches/upcoming/?cup=${props.cup.id}&limit=4`),
      api.get(`/special-tips/by_cup/?cup=${props.cup.id}`).catch((e) => {
        if (e.response?.status === 404) return { data: null }
        throw e
      }),
    ])

    const matches = matchesResponse.data.results || matchesResponse.data
    allMatches.value = Array.isArray(matches) ? matches : []
    stats.value.matches = allMatches.value.length

    const teams = teamsResponse.data.results || teamsResponse.data
    stats.value.teams = teams.length

    const tipRows = tipsResponse.data
    const tipMap = {}
    for (const t of tipRows) {
      const mid = t.match?.id
      if (mid != null) {
        tipMap[mid] = { score_a: t.score_a, score_b: t.score_b }
      }
    }
    tipsByMatchId.value = tipMap
    stats.value.myTips = allMatches.value.filter((m) => {
      const t = tipMap[m.id]
      return t && t.score_a != null && t.score_b != null
    }).length

    const points = pointsResponse.data.results || pointsResponse.data
    points.forEach((point) => {
      if (point.part === 'A') myPoints.value.points_a = point.points
      if (point.part === 'B') myPoints.value.points_b = point.points
      if (point.part === 'C') myPoints.value.points_c = point.points
    })

    upcomingMatches.value = upcomingRes.data
    specialTipRecord.value = specialRes?.data ?? null
  } catch (error) {
    console.error('Error loading data:', error)
  }
}

function formatDateTime(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString('cs-CZ')
}

function myTipText(matchId) {
  const t = tipsByMatchId.value[matchId]
  if (!t || t.score_a == null || t.score_b == null) return null
  return `${t.score_a} : ${t.score_b}`
}
</script>
