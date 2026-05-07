<template>
  <div class="h-screen w-screen overflow-hidden bg-white">
    <div v-if="loading" class="text-center py-12 text-gray-600">Načítání…</div>
    <div v-else-if="loadError" class="text-red-700 p-6">
      {{ loadError }}
    </div>
    <div v-else-if="!matrix.users?.length" class="text-gray-600 p-6">
      Zatím tu nejsou žádné tipy od hráčů.
    </div>

    <div v-else ref="sheetRef" class="h-full w-full overflow-auto">
      <div class="inline-block">
        <table class="text-sm border-collapse min-w-max w-max">
        <thead>
          <tr class="bg-gray-100 border-b border-gray-200">
            <th
              class="bg-gray-100 px-3 py-2 text-left font-semibold text-gray-700 whitespace-nowrap border-r border-gray-200 min-w-[10rem]"
            >
              Zápas
            </th>
            <th
              class="bg-gray-100 px-3 py-2 text-left font-semibold text-gray-700 whitespace-nowrap border-r border-gray-200 min-w-[7.25rem]"
            >
              Datum
            </th>
            <th
              class="bg-gray-100 px-3 py-2 text-center font-semibold text-gray-700 whitespace-nowrap border-r border-gray-200 min-w-[5.25rem]"
            >
              Výsledek
            </th>
            <th
              v-for="(u, ui) in usersSortedMatches"
              :key="'eh-' + u.id"
              class="px-2 py-2 text-center font-semibold text-gray-800 whitespace-nowrap min-w-[5rem] border-r border-gray-200/80"
              :class="[userColClass(ui), userHeaderClass(u, ui)]"
              :data-user-col="String(u.id)"
            >
              {{ u.display_name }}
            </th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="m in matrix.matches"
            :key="'er-' + m.id"
            class="border-b border-gray-100 hover:bg-gray-50/80"
            :class="isToday(m.date) ? 'bg-primary-50/40' : ''"
          >
            <td
              class="bg-white px-3 py-2 border-r border-gray-200 min-w-[10rem]"
            >
              <span class="inline-flex items-center gap-1.5 flex-wrap">
                <TeamWithFlag display="shortcut" :team="m.team_a" />
                <span class="text-gray-400">–</span>
                <TeamWithFlag display="shortcut" :team="m.team_b" />
              </span>
            </td>
            <td class="px-3 py-2 text-gray-600 whitespace-nowrap border-r border-gray-200 bg-white">
              {{ formatMatchDate(m.date) }}
            </td>
            <td class="px-3 py-2 text-center font-bold tabular-nums border-r border-gray-200 bg-gray-50/50">
              <template v-if="matchResultText(m)">{{ matchResultText(m) }}</template>
              <span v-else class="text-gray-400 font-normal">—</span>
            </td>
            <td
              v-for="(u, ui) in usersSortedMatches"
              :key="'ec-' + m.id + '-' + u.id"
              class="px-2 py-2 text-center tabular-nums border-r border-gray-100"
              :class="[userColClass(ui), userCellClass(u)]"
            >
              <template
                v-for="p in [matchTipPresentation(m, m.tips?.[String(u.id)], matrix.tournament_started)]"
                :key="'ep-' + m.id + '-' + u.id"
              >
                <span :class="p.classes">{{ p.text }}</span>
              </template>
            </td>
          </tr>
        </tbody>

        <tfoot>
          <tr class="bg-gray-100 border-t-2 border-gray-300 font-semibold text-gray-900">
            <td
              class="bg-gray-100 px-3 py-2 border-r border-gray-200"
              colspan="3"
            >
              Celkem – část A
            </td>
            <td
              v-for="(u, ui) in usersSortedMatches"
              :key="'ef-' + u.id"
              class="px-2 py-2 text-center tabular-nums border-r border-gray-200/80"
              :class="[userColClass(ui), userCellClass(u)]"
            >
              {{ u.points_part_a ?? 0 }}
            </td>
          </tr>
        </tfoot>
      </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'
import TeamWithFlag from '../../components/TeamWithFlag.vue'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const loading = ref(true)
const loadError = ref('')
const sheetRef = ref(null)

const matrix = ref({
  tournament_started: false,
  users: [],
  teams: [],
  matches: [],
  special_rows: [],
  special_result: null,
  special_exists: false,
})

const USER_BG = ['bg-pink-50/90', 'bg-sky-50/90', 'bg-emerald-50/90', 'bg-amber-50/90']

function compareUsersByPointsThenName(a, b, pointsField) {
  const pa = Number(a[pointsField] ?? 0)
  const pb = Number(b[pointsField] ?? 0)
  if (pb !== pa) return pb - pa
  return String(a.display_name || '').localeCompare(String(b.display_name || ''), 'cs', {
    sensitivity: 'base',
  })
}

const usersSortedMatches = computed(() => {
  const u = matrix.value.users || []
  return [...u].sort((a, b) => compareUsersByPointsThenName(a, b, 'points_part_a'))
})

function userColClass(index) {
  return USER_BG[index % USER_BG.length]
}

const myUserId = computed(() => {
  const id = authStore.user?.id
  return id == null ? '' : String(id)
})

const myUserColIndex = computed(() => {
  const id = myUserId.value
  if (!id) return -1
  return usersSortedMatches.value.findIndex((u) => String(u.id) === id)
})

const myUserColIndexKnown = computed(() => myUserColIndex.value >= 0)

function userHeaderClass(u, ui) {
  return String(u.id) === myUserId.value ? 'ring-2 ring-primary-300' : ''
}

function userCellClass(u) {
  return String(u.id) === myUserId.value ? 'ring-2 ring-primary-200 ring-inset' : ''
}

onMounted(async () => {
  loadError.value = ''
  try {
    const year = route.params.year
    const cupRes = await api.get(`/cups/?year=${year}`)
    const data = cupRes.data
    const cups = data.results != null ? data.results : (Array.isArray(data) ? data : [data])
    const list = Array.isArray(cups) ? cups : (cups ? [cups] : [])
    const cup = list.length ? list[0] : null
    if (!cup?.id) {
      loadError.value = 'Turnaj nenalezen.'
      return
    }
    const res = await api.get(`/cups/${cup.id}/tips_matrix/`)
    matrix.value = res.data
  } catch (e) {
    console.error(e)
    const status = e.response?.status
    loadError.value =
      status === 403 || status === 401
        ? 'Tento přehled nemáš oprávnění načíst. Zkus se odhlásit a znovu přihlásit.'
        : 'Přehled tipů se nepodařilo načíst. Zkus to prosím znovu později.'
  } finally {
    loading.value = false
  }
})

function formatMatchDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const day = d.getDate()
  const month = d.getMonth() + 1
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${day}.${month}. ${h}:${min}`
}

function matchResultText(m) {
  const a = m.score_a_final != null ? m.score_a_final : m.score_a
  const b = m.score_b_final != null ? m.score_b_final : m.score_b
  if (a == null || b == null) return null
  let s = `${a} : ${b}`
  if (m.overtime || (m.score_a != null && m.score_a_final != null && (m.score_a !== m.score_a_final || m.score_b !== m.score_b_final))) {
    s += m.shootout ? ' nájezdy' : ' prodloužení'
  }
  return s
}

function isToday(dateString) {
  if (!dateString) return false
  const d = new Date(dateString)
  const now = new Date()
  return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate()
}

function matchTipPresentation(match, tip, started) {
  if (!started) {
    return { text: '?:?', classes: ['text-gray-500', 'font-mono'] }
  }
  if (!tip || tip.score_a == null || tip.score_b == null) {
    return { text: '—', classes: ['text-gray-400'] }
  }
  const text = `${tip.score_a} : ${tip.score_b}`
  const ra = match.score_a
  const rb = match.score_b
  if (ra == null || rb == null) {
    return { text, classes: ['text-gray-800'] }
  }
  if (tip.score_a === ra && tip.score_b === rb) {
    return { text, classes: ['font-bold', 'underline', 'text-gray-900'] }
  }
  const sign = (x, y) => (x > y ? 1 : x < y ? -1 : 0)
  if (sign(tip.score_a, tip.score_b) === sign(ra, rb)) {
    return { text, classes: ['font-bold', 'text-gray-900'] }
  }
  return { text, classes: ['line-through', 'text-gray-600', 'font-normal'] }
}

</script>
