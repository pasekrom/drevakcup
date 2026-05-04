<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">Speciální tipy</h2>

    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>

    <div v-else class="space-y-6">
      <div
        v-if="!tournamentStarted"
        class="rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-800"
      >
        <p class="font-medium text-gray-900">
          Speciální tipy můžeš upravovat, dokud nezačne první zápas.
        </p>
        <p v-if="firstMatchDate" class="mt-2 text-gray-700">
          První utkání turnaje začíná {{ formatDateTime(firstMatchDate) }}.
        </p>
      </div>
      <div
        v-else
        class="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"
      >
        Turnaj už začal
        <template v-if="firstMatchDate"> (první zápas {{ formatDateTime(firstMatchDate) }})</template>.
        Tvoje speciální tipy jsou uzamčené; níže vidíš svůj tip a oficiální výsledek u každé položky.
      </div>

      <p
        v-if="tournamentStarted && specialResult === null"
        class="text-sm text-gray-600"
      >
        Oficiální výsledky speciálu v API zatím nejsou — po jejich zadání správcem se u položek doplní sloupec „Oficiální výsledek“.
      </p>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div v-for="section in sections" :key="section.title" class="card">
          <h3 class="text-xl font-bold mb-4">{{ section.title }}</h3>
          <div class="divide-y divide-gray-100">
            <div
              v-for="row in section.rows"
              :key="row.key"
              class="grid gap-3 py-4 first:pt-0 md:grid-cols-12 md:items-start"
            >
              <div class="md:col-span-5">
                <p class="text-sm font-medium text-gray-900">{{ row.label }}</p>
              </div>
              <div class="md:col-span-7 space-y-2">
                <template v-if="!tournamentStarted">
                  <select
                    v-if="row.type === 'team'"
                    v-model="form[row.key]"
                    class="input w-full"
                  >
                    <option :value="null">Vyberte tým</option>
                    <option v-for="team in teamsForSelect(row)" :key="team.id" :value="team.id">
                      {{ team.display_name || team.name }}
                    </option>
                  </select>
                  <input
                    v-else-if="row.type === 'text'"
                    v-model="form[row.key]"
                    type="text"
                    class="input w-full"
                    placeholder="Jméno hráče"
                  />
                  <input
                    v-else
                    v-model.number="form[row.key]"
                    type="number"
                    min="0"
                    class="input w-full"
                    placeholder="0"
                  />
                </template>
                <template v-else>
                  <div class="rounded-md border px-3 py-2 transition-colors" :class="tipBoxClass(row)">
                    <div class="flex flex-wrap items-baseline justify-between gap-2">
                      <p class="text-xs uppercase tracking-wide text-gray-500">Můj tip</p>
                      <span
                        v-if="rowOutcome(row).hit && rowOutcome(row).points != null"
                        class="text-sm font-bold text-green-700 tabular-nums"
                      >+{{ rowOutcome(row).points }} b</span>
                    </div>
                    <p class="font-medium text-gray-900">
                      <template v-if="row.type === 'team'">
                        <TeamWithFlag v-if="teamForTip(row)" :team="teamForTip(row)" />
                        <span v-else>{{ formatTipDisplay(row) }}</span>
                      </template>
                      <template v-else>
                        {{ formatTipDisplay(row) }}
                      </template>
                    </p>
                  </div>
                  <div class="rounded-md border border-dashed border-gray-200 bg-gray-50 px-3 py-2 text-sm">
                    <p class="text-xs uppercase tracking-wide text-gray-500">Oficiální výsledek</p>
                    <p class="font-medium text-gray-800">
                      <template v-if="row.type === 'team'">
                        <TeamWithFlag v-if="teamForResult(row)" :team="teamForResult(row)" />
                        <span v-else>{{ formatResultDisplay(row) }}</span>
                      </template>
                      <template v-else>
                        {{ formatResultDisplay(row) }}
                      </template>
                    </p>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!tournamentStarted" class="flex justify-end">
          <button type="submit" :disabled="saving" class="btn btn-primary">
            <span v-if="saving">Ukládání...</span>
            <span v-else>Uložit speciální tipy</span>
          </button>
        </div>
      </form>
    </div>

    <MessageModal
      v-model="dialogOpen"
      :title="dialogTitle"
      :message="dialogMessage"
      :variant="dialogVariant"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import MessageModal from '../../components/MessageModal.vue'
import TeamWithFlag from '../../components/TeamWithFlag.vue'

const props = defineProps({
  cup: {
    type: Object,
    required: true,
  },
})

const loading = ref(true)
const saving = ref(false)

const dialogOpen = ref(false)
const dialogTitle = ref('')
const dialogMessage = ref('')
const dialogVariant = ref('success')

const allTeams = ref([])
const groupATeams = ref([])
const groupBTeams = ref([])
const firstMatchDate = ref(null)
const specialResult = ref(null)

const form = ref({
  winner_id: null,
  final_a_id: null,
  final_b_id: null,
  bronze_a_id: null,
  bronze_b_id: null,
  group_a_1_id: null,
  group_a_2_id: null,
  group_a_3_id: null,
  group_a_4_id: null,
  group_b_1_id: null,
  group_b_2_id: null,
  group_b_3_id: null,
  group_b_4_id: null,
  czech_shooter_first: '',
  czech_shooter_last: '',
  max_goals_per_game: null,
  team_most_goals_id: null,
  team_least_goals_id: null,
  team_first_goal_id: null,
  team_last_goal_id: null,
  team_drop_a_id: null,
  team_drop_b_id: null,
  overtimes: null,
})

const GROUP_PLACES = ['1. místo', '2. místo', '3. místo', '4. místo']

const sections = computed(() => [
  {
    title: 'Finálové tipy',
    rows: [
      {
        key: 'winner_id',
        label: 'Vítěz turnaje',
        type: 'team',
        teams: 'all',
        resultKey: 'winner',
        points: 24,
        matchMode: 'exact',
      },
      {
        key: 'final_a_id',
        label: 'Finalista 1',
        type: 'team',
        teams: 'finalA',
        resultKey: 'final_a',
        points: 16,
        matchMode: 'eitherFinal',
      },
      {
        key: 'final_b_id',
        label: 'Finalista 2',
        type: 'team',
        teams: 'finalB',
        resultKey: 'final_b',
        points: 16,
        matchMode: 'eitherFinal',
      },
      {
        key: 'bronze_a_id',
        label: 'Tým 1, který se utká o bronz',
        type: 'team',
        teams: 'bronzeA',
        resultKey: 'bronze_a',
        points: 12,
        matchMode: 'eitherBronze',
      },
      {
        key: 'bronze_b_id',
        label: 'Tým 2, který se utká o bronz',
        type: 'team',
        teams: 'bronzeB',
        resultKey: 'bronze_b',
        points: 12,
        matchMode: 'eitherBronze',
      },
    ],
  },
  {
    title: 'Skupina A',
    rows: [
      ...GROUP_PLACES.map((place, i) => ({
        key: `group_a_${i + 1}_id`,
        label: place,
        type: 'team',
        teams: 'groupA',
        resultKey: `group_a_${i + 1}`,
        points: i === 0 ? 9 : 6,
        matchMode: 'exact',
      })),
      {
        key: 'team_drop_a_id',
        label: 'Tým, který sestoupí',
        type: 'team',
        teams: 'groupA',
        resultKey: 'team_drop_a',
        points: 6,
        matchMode: 'exact',
      },
    ],
  },
  {
    title: 'Skupina B',
    rows: [
      ...GROUP_PLACES.map((place, i) => ({
        key: `group_b_${i + 1}_id`,
        label: place,
        type: 'team',
        teams: 'groupB',
        resultKey: `group_b_${i + 1}`,
        points: i === 0 ? 9 : 6,
        matchMode: 'exact',
      })),
      {
        key: 'team_drop_b_id',
        label: 'Tým, který sestoupí',
        type: 'team',
        teams: 'groupB',
        resultKey: 'team_drop_b',
        points: 6,
        matchMode: 'exact',
      },
    ],
  },
  {
    title: 'České tipy',
    rows: [
      {
        key: 'czech_shooter_first',
        label: 'Český střelec 1. gólu',
        type: 'text',
        teams: null,
        resultKey: 'czech_shooter_first',
        points: 12,
        matchMode: 'foldText',
      },
      {
        key: 'czech_shooter_last',
        label: 'Český střelec posledního gólu',
        type: 'text',
        teams: null,
        resultKey: 'czech_shooter_last',
        points: 12,
        matchMode: 'foldText',
      },
    ],
  },
  {
    title: 'Další tipy',
    rows: [
      {
        key: 'team_most_goals_id',
        label: 'Tým, který vstřelí nejvíce branek (celkem na MS)',
        type: 'team',
        teams: 'all',
        resultKey: 'team_most_goals',
        points: 12,
        matchMode: 'exact',
      },
      {
        key: 'team_least_goals_id',
        label: 'Tým, který obdrží nejméně branek (celkem na MS)',
        type: 'team',
        teams: 'all',
        resultKey: 'team_least_goals',
        points: 12,
        matchMode: 'exact',
      },
      {
        key: 'team_first_goal_id',
        label: 'Tým, který vstřelí první branku na MS',
        type: 'team',
        teams: 'all',
        resultKey: 'team_first_goal',
        points: 3,
        matchMode: 'exact',
      },
      {
        key: 'team_last_goal_id',
        label: 'Tým, který vstřelí poslední branku na MS',
        type: 'team',
        teams: 'all',
        resultKey: 'team_last_goal',
        points: 12,
        matchMode: 'exact',
      },
      {
        key: 'max_goals_per_game',
        label: 'Nejvíce branek v jednom utkání (dohromady)',
        type: 'number',
        teams: null,
        resultKey: 'max_goals_per_game',
        points: 12,
        matchMode: 'exactNumber',
      },
      {
        key: 'overtimes',
        label: 'Počet remíz/prodloužení (celkem za MS)',
        type: 'number',
        teams: null,
        resultKey: 'overtimes',
        points: 24,
        matchMode: 'exactNumber',
      },
    ],
  },
])

/** Stejné jako backend `is_tournament_started` (čas prvního zápasu vs. teď). */
const tournamentStarted = computed(() => !!props.cup?.tournament_started)

const teamsForFinalA = computed(() =>
  allTeams.value.filter((t) => t.id !== form.value.final_b_id || t.id === form.value.final_a_id)
)
const teamsForFinalB = computed(() =>
  allTeams.value.filter((t) => t.id !== form.value.final_a_id || t.id === form.value.final_b_id)
)
const teamsForBronzeA = computed(() =>
  allTeams.value.filter((t) => t.id !== form.value.bronze_b_id || t.id === form.value.bronze_a_id)
)
const teamsForBronzeB = computed(() =>
  allTeams.value.filter((t) => t.id !== form.value.bronze_a_id || t.id === form.value.bronze_b_id)
)

function teamsForSelect(row) {
  switch (row.teams) {
    case 'all':
      return allTeams.value
    case 'groupA':
      return groupATeams.value
    case 'groupB':
      return groupBTeams.value
    case 'finalA':
      return teamsForFinalA.value
    case 'finalB':
      return teamsForFinalB.value
    case 'bronzeA':
      return teamsForBronzeA.value
    case 'bronzeB':
      return teamsForBronzeB.value
    default:
      return allTeams.value
  }
}

function openFeedback(title, message, variant = 'success') {
  dialogTitle.value = title
  dialogMessage.value = message
  dialogVariant.value = variant
  dialogOpen.value = true
}

function formatSaveError(error) {
  const data = error.response?.data
  if (!data) return 'Speciální tipy se nepodařilo uložit. Zkus to prosím znovu.'
  const d = data.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.join(', ')
  const lines = []
  for (const [key, val] of Object.entries(data)) {
    if (key === 'detail') continue
    if (Array.isArray(val)) lines.push(`${key}: ${val.join(', ')}`)
    else if (val != null && typeof val === 'object') lines.push(`${key}: ${JSON.stringify(val)}`)
    else lines.push(`${key}: ${val}`)
  }
  if (lines.length) return lines.join('\n')
  return typeof data === 'object' ? JSON.stringify(data) : String(data)
}

function formatDateTime(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('cs-CZ')
}

function teamIdFromApi(val) {
  if (val == null) return null
  if (typeof val === 'object' && val !== null && 'id' in val) return val.id
  return val
}

function teamById(id) {
  if (id == null) return null
  return allTeams.value.find((t) => t.id === id) ?? null
}

function rawResultValue(row) {
  if (!specialResult.value) return null
  return specialResult.value[row.resultKey]
}

function teamForTip(row) {
  if (row.type !== 'team') return null
  return teamById(form.value[row.key])
}

function teamForResult(row) {
  if (row.type !== 'team') return null
  const v = rawResultValue(row)
  const id = teamIdFromApi(v)
  return teamById(id)
}

function formatTipDisplay(row) {
  if (row.type === 'team') {
    const t = teamForTip(row)
    return t ? t.name : '—'
  }
  if (row.type === 'text') {
    const s = (form.value[row.key] ?? '').trim()
    return s || '—'
  }
  const v = form.value[row.key]
  if (v === null || v === undefined || v === '') return '—'
  return String(v)
}

function formatResultDisplay(row) {
  const raw = rawResultValue(row)
  if (raw == null || raw === '') {
    return specialResult.value ? 'Zatím nevyhlášeno' : '—'
  }
  if (row.type === 'team') {
    const id = teamIdFromApi(raw)
    const t = teamById(id)
    return t ? t.name : '—'
  }
  if (row.type === 'text') {
    const s = String(raw).trim()
    return s || 'Zatím nevyhlášeno'
  }
  return String(raw)
}

/** Stejná idea jako backend `fold_text` (diakritika, mezery, malá písmena). */
function foldText(value) {
  if (value == null) return ''
  let s = String(value).trim().toLowerCase()
  if (!s) return ''
  try {
    return s.normalize('NFD').replace(/\p{M}/gu, '')
  } catch {
    return s.replace(/[\u0300-\u036f]/g, '')
  }
}

function rowOutcome(row) {
  const neutral = { known: false, hit: false, points: null }
  if (!tournamentStarted.value || !specialResult.value) return neutral

  const pts = row.points ?? null

  if (row.matchMode === 'eitherFinal') {
    const saId = teamIdFromApi(specialResult.value.final_a)
    const sbId = teamIdFromApi(specialResult.value.final_b)
    if (!saId && !sbId) return neutral
    const pick = form.value[row.key]
    if (!pick) return { known: true, hit: false, points: null }
    const hit = (!!saId && pick === saId) || (!!sbId && pick === sbId)
    return { known: true, hit, points: hit ? pts : null }
  }

  if (row.matchMode === 'eitherBronze') {
    const baId = teamIdFromApi(specialResult.value.bronze_a)
    const bbId = teamIdFromApi(specialResult.value.bronze_b)
    if (!baId && !bbId) return neutral
    const pick = form.value[row.key]
    if (!pick) return { known: true, hit: false, points: null }
    const hit = (!!baId && pick === baId) || (!!bbId && pick === bbId)
    return { known: true, hit, points: hit ? pts : null }
  }

  if (row.matchMode === 'foldText') {
    const raw = rawResultValue(row)
    const foldedRes = foldText(String(raw ?? ''))
    if (!foldedRes) return neutral
    const foldedTip = foldText(String(form.value[row.key] ?? ''))
    const hit = !!foldedTip && foldedTip === foldedRes
    return { known: true, hit, points: hit ? pts : null }
  }

  if (row.matchMode === 'exactNumber') {
    const raw = rawResultValue(row)
    if (raw === null || raw === undefined || raw === '') return neutral
    const nr = Number(raw)
    if (Number.isNaN(nr)) return neutral
    const v = form.value[row.key]
    if (v === null || v === undefined || v === '') {
      return { known: true, hit: false, points: null }
    }
    const nt = Number(v)
    if (Number.isNaN(nt)) return { known: true, hit: false, points: null }
    const hit = nt === nr
    return { known: true, hit, points: hit ? pts : null }
  }

  // exact (tým i ostatní přesné FK)
  if (row.type === 'team') {
    const rid = teamIdFromApi(rawResultValue(row))
    if (rid == null) return neutral
    const tid = form.value[row.key]
    const hit = tid != null && tid === rid
    return { known: true, hit, points: hit ? pts : null }
  }

  return neutral
}

function tipBoxClass(row) {
  if (!tournamentStarted.value) return 'border-gray-200 bg-white'
  const o = rowOutcome(row)
  if (!o.known) return 'border-gray-200 bg-white'
  if (o.hit) return 'border-green-400 bg-green-100'
  return 'border-red-300 bg-red-100'
}

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const teamsResponse = await api.get(`/teams/?cup=${props.cup.id}`)
    const teams = teamsResponse.data.results || teamsResponse.data
    allTeams.value = teams
    groupATeams.value = teams.filter((t) => t.group === 'A')
    groupBTeams.value = teams.filter((t) => t.group === 'B')

    const matchesResponse = await api.get(`/matches/?cup=${props.cup.id}`)
    const matchList = matchesResponse.data.results || matchesResponse.data
    const dates = (Array.isArray(matchList) ? matchList : [])
      .map((m) => m.date)
      .filter(Boolean)
    if (dates.length) {
      firstMatchDate.value = dates.reduce((a, b) => (new Date(a) <= new Date(b) ? a : b))
    } else {
      firstMatchDate.value = null
    }

    const started = !!props.cup?.tournament_started
    specialResult.value = null
    if (started) {
      try {
        const sp = await api.get(`/special/by_cup/?cup=${props.cup.id}`)
        specialResult.value = sp.data
      } catch (e) {
        if (e.response?.status !== 404) console.error(e)
        specialResult.value = null
      }
    }

    try {
      const tipResponse = await api.get(`/special-tips/by_cup/?cup=${props.cup.id}`)
      const tip = tipResponse.data
      if (tip) {
        form.value.winner_id = tip.winner?.id ?? null
        form.value.final_a_id = tip.final_a?.id ?? null
        form.value.final_b_id = tip.final_b?.id ?? null
        form.value.bronze_a_id = tip.bronze_a?.id ?? null
        form.value.bronze_b_id = tip.bronze_b?.id ?? null
        form.value.group_a_1_id = tip.group_a_1?.id ?? null
        form.value.group_a_2_id = tip.group_a_2?.id ?? null
        form.value.group_a_3_id = tip.group_a_3?.id ?? null
        form.value.group_a_4_id = tip.group_a_4?.id ?? null
        form.value.group_b_1_id = tip.group_b_1?.id ?? null
        form.value.group_b_2_id = tip.group_b_2?.id ?? null
        form.value.group_b_3_id = tip.group_b_3?.id ?? null
        form.value.group_b_4_id = tip.group_b_4?.id ?? null
        form.value.czech_shooter_first = tip.czech_shooter_first ?? ''
        form.value.czech_shooter_last = tip.czech_shooter_last ?? ''
        form.value.max_goals_per_game = tip.max_goals_per_game ?? null
        form.value.team_most_goals_id = tip.team_most_goals?.id ?? null
        form.value.team_least_goals_id = tip.team_least_goals?.id ?? null
        form.value.team_first_goal_id = tip.team_first_goal?.id ?? null
        form.value.team_last_goal_id = tip.team_last_goal?.id ?? null
        form.value.team_drop_a_id = tip.team_drop_a?.id ?? null
        form.value.team_drop_b_id = tip.team_drop_b?.id ?? null
        form.value.overtimes = tip.overtimes ?? null
      }
    } catch (error) {
      if (error.response?.status !== 404) console.error('Error loading special tip:', error)
    }
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (tournamentStarted.value) return
  saving.value = true
  try {
    const data = {
      cup_id: props.cup.id,
      ...form.value,
    }
    const teamKeys = [
      'winner_id',
      'final_a_id',
      'final_b_id',
      'bronze_a_id',
      'bronze_b_id',
      'group_a_1_id',
      'group_a_2_id',
      'group_a_3_id',
      'group_a_4_id',
      'group_b_1_id',
      'group_b_2_id',
      'group_b_3_id',
      'group_b_4_id',
      'team_most_goals_id',
      'team_least_goals_id',
      'team_first_goal_id',
      'team_last_goal_id',
      'team_drop_a_id',
      'team_drop_b_id',
    ]
    teamKeys.forEach((k) => {
      if (data[k] === '' || data[k] === undefined) data[k] = null
    })
    const n = (v) =>
      v === '' || v === undefined || v === null || Number.isNaN(Number(v)) ? 0 : Number(v)
    data.max_goals_per_game = n(data.max_goals_per_game)
    data.overtimes = n(data.overtimes)

    await api.post('/special-tips/', data)
    openFeedback('Speciální tipy uloženy', 'Speciální tipy byly úspěšně uloženy.', 'success')
  } catch (error) {
    console.error('Error saving special tips:', error)
    openFeedback('Chyba při ukládání', formatSaveError(error), 'error')
  } finally {
    saving.value = false
  }
}
</script>
