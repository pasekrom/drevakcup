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
      <div class="inline-block pb-8">
        <table class="text-sm border-collapse min-w-max w-max">
          <thead>
            <tr class="bg-gray-100 border-b border-gray-200">
              <th
                class="sticky top-0 left-0 z-30 bg-gray-100 px-3 py-2 text-left font-semibold text-gray-700 whitespace-nowrap border-r border-gray-200 min-w-[14rem] shadow-[2px_2px_4px_rgba(0,0,0,0.06)]"
              >
                Položka / zápas
              </th>
              <th
                class="sticky top-0 z-20 bg-gray-100 px-3 py-2 text-left font-semibold text-gray-700 whitespace-nowrap border-r border-gray-200 min-w-[7.25rem]"
              >
                Datum / body
              </th>
              <th
                class="sticky top-0 z-20 bg-gray-100 px-3 py-2 text-center font-semibold text-gray-700 whitespace-nowrap border-r border-gray-200 min-w-[5.25rem]"
              >
                Výsledek
              </th>
              <th
                v-for="(u, ui) in usersSorted"
                :key="'eh-' + u.id"
                class="sticky top-0 z-20 px-2 py-2 text-center font-semibold text-gray-800 whitespace-nowrap min-w-[5rem] border-r border-gray-200/80"
                :class="[userHeaderColClass(ui), userHeaderClass(u, ui)]"
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
                class="sticky left-0 z-10 px-3 py-2 border-r border-gray-200 shadow-[2px_0_4px_rgba(0,0,0,0.04)]"
                :class="isToday(m.date) ? 'bg-primary-50' : 'bg-white'"
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
                v-for="(u, ui) in usersSorted"
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

            <tr class="bg-amber-100/90 border-y-2 border-amber-300/80">
              <td
                class="px-3 py-2.5 text-center text-sm font-bold text-amber-950 tracking-wide"
                :colspan="3 + usersSorted.length"
              >
                2. část – speciální tipy
              </td>
            </tr>

            <tr
              v-for="row in matrix.special_rows"
              :key="'sr-' + row.tip_field"
              class="border-b border-gray-100 hover:bg-gray-50/80"
            >
              <td class="sticky left-0 z-10 bg-white px-3 py-2 text-gray-900 border-r border-gray-200 shadow-[2px_0_4px_rgba(0,0,0,0.04)]">
                {{ row.label }}
              </td>
              <td class="px-2 py-2 text-center text-amber-900/90 font-medium border-r border-gray-200 bg-amber-50/40 whitespace-nowrap">
                {{ row.points }}
              </td>
              <td class="px-3 py-2 text-center border-r border-gray-200 bg-gray-50/40 text-gray-900">
                {{ formatSpecialResult(row, matrix.special_result) }}
              </td>
              <td
                v-for="(u, ui) in usersSorted"
                :key="'sec-' + row.tip_field + '-' + u.id"
                class="px-2 py-2 text-center border-r border-gray-100"
                :class="[userColClass(ui), userCellClass(u)]"
              >
                <template
                  v-for="p in [
                    specialTipPresentation(
                      row,
                      row.tips?.[String(u.id)],
                      matrix.special_result,
                      matrix.tournament_started,
                    ),
                  ]"
                  :key="'sep-' + row.tip_field + '-' + u.id"
                >
                  <span :class="p.classes">{{ p.text }}</span>
                </template>
              </td>
            </tr>
          </tbody>

          <tfoot>
            <tr class="bg-gray-100 border-t-2 border-gray-300 font-semibold text-gray-900">
              <td
                class="sticky left-0 z-10 bg-gray-100 px-3 py-2 border-r border-gray-200 shadow-[2px_0_4px_rgba(0,0,0,0.06)]"
                colspan="3"
              >
                Celkem – část A
              </td>
              <td
                v-for="(u, ui) in usersSorted"
                :key="'ef-a-' + u.id"
                class="px-2 py-2 text-center tabular-nums border-r border-gray-200/80"
                :class="[userColClass(ui), userCellClass(u)]"
              >
                {{ u.points_part_a ?? 0 }}
              </td>
            </tr>
            <tr class="bg-gray-100 border-t border-gray-200 font-semibold text-gray-900">
              <td
                class="sticky left-0 z-10 bg-gray-100 px-3 py-2 border-r border-gray-200 shadow-[2px_0_4px_rgba(0,0,0,0.06)]"
                colspan="3"
              >
                Celkem – část B
              </td>
              <td
                v-for="(u, ui) in usersSorted"
                :key="'ef-b-' + u.id"
                class="px-2 py-2 text-center tabular-nums border-r border-gray-200/80"
                :class="[userColClass(ui), userCellClass(u)]"
              >
                {{ u.points_part_b ?? 0 }}
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
const USER_HDR_BG = ['bg-pink-50', 'bg-sky-50', 'bg-emerald-50', 'bg-amber-50']

function compareUsersByTotalThenName(a, b) {
  const ta = Number(a.points_part_a ?? 0) + Number(a.points_part_b ?? 0)
  const tb = Number(b.points_part_a ?? 0) + Number(b.points_part_b ?? 0)
  if (tb !== ta) return tb - ta
  return String(a.display_name || '').localeCompare(String(b.display_name || ''), 'cs', {
    sensitivity: 'base',
  })
}

/** Jedno pořadí sloupců pro zápasy i speciál (celkové body A+B, pak jméno). */
const usersSorted = computed(() => {
  const u = matrix.value.users || []
  return [...u].sort(compareUsersByTotalThenName)
})

const teamsById = computed(() => {
  const m = new Map()
  for (const t of matrix.value.teams || []) {
    m.set(t.id, t)
  }
  return m
})

function userColClass(index) {
  return USER_BG[index % USER_BG.length]
}

function userHeaderColClass(index) {
  return USER_HDR_BG[index % USER_HDR_BG.length]
}

const myUserId = computed(() => {
  const id = authStore.user?.id
  return id == null ? '' : String(id)
})

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

function teamName(id) {
  if (id == null) return '—'
  const t = teamsById.value.get(id)
  if (!t) return '—'
  return t.display_name || t.name || '—'
}

function formatSpecialResult(row, sr) {
  if (!sr) return '—'
  const v = sr[row.result_field]
  if (row.field_type === 'team') {
    return teamName(v)
  }
  if (row.field_type === 'text') {
    const s = String(v ?? '').trim()
    return s || '—'
  }
  if (v == null && v !== 0) return '—'
  return String(v)
}

function formatSpecialTipValue(row, tipVal) {
  if (row.field_type === 'number') {
    if (tipVal == null || tipVal === '') return '—'
    return String(tipVal)
  }
  if (tipVal == null || tipVal === '') return '—'
  if (row.field_type === 'team') return teamName(tipVal)
  if (row.field_type === 'text') return String(tipVal).trim() || '—'
  return String(tipVal)
}

function specialResultKnown(row, sr) {
  if (!sr) return false
  const v = sr[row.result_field]
  if (row.field_type === 'team') return v != null
  if (row.field_type === 'text') return !!foldText(String(v ?? ''))
  return v != null && v !== ''
}

function specialTipPresentation(row, tipVal, sr, started) {
  if (!started) {
    return { text: '?:?', classes: ['text-gray-500', 'font-mono'] }
  }
  if (row.field_type === 'number') {
    if (tipVal == null || tipVal === '') {
      return { text: '—', classes: ['text-gray-400'] }
    }
  } else if (tipVal == null || tipVal === '') {
    return { text: '—', classes: ['text-gray-400'] }
  }

  const text = formatSpecialTipValue(row, tipVal)

  if (!specialResultKnown(row, sr)) {
    return { text, classes: ['text-gray-800'] }
  }

  const res = sr[row.result_field]
  const mode = row.mode

  if (mode === 'exact' && row.field_type === 'team') {
    if (tipVal === res && res != null) return { text, classes: ['font-bold', 'underline', 'text-gray-900'] }
    if (res == null) return { text, classes: ['text-gray-800'] }
    return { text, classes: ['line-through', 'text-gray-600', 'font-normal'] }
  }

  if (mode === 'either_final' && row.field_type === 'team') {
    const saId = sr.final_a_id
    const sbId = sr.final_b_id
    if (!saId && !sbId) return { text, classes: ['text-gray-800'] }
    const pick = tipVal
    if (pick == null) return { text: '—', classes: ['text-gray-400'] }
    const hit = (!!saId && pick === saId) || (!!sbId && pick === sbId)
    if (hit) return { text, classes: ['font-bold', 'text-gray-900'] }
    return { text, classes: ['line-through', 'text-gray-600', 'font-normal'] }
  }

  if (mode === 'either_bronze' && row.field_type === 'team') {
    const baId = sr.bronze_a_id
    const bbId = sr.bronze_b_id
    if (!baId && !bbId) return { text, classes: ['text-gray-800'] }
    const pick = tipVal
    if (pick == null) return { text: '—', classes: ['text-gray-400'] }
    const hit = (!!baId && pick === baId) || (!!bbId && pick === bbId)
    if (hit) return { text, classes: ['font-bold', 'text-gray-900'] }
    return { text, classes: ['line-through', 'text-gray-600', 'font-normal'] }
  }

  if (mode === 'fold_text' && row.field_type === 'text') {
    const fr = foldText(String(res ?? ''))
    if (!fr) return { text, classes: ['text-gray-800'] }
    const ft = foldText(String(tipVal ?? ''))
    if (ft && ft === fr) return { text, classes: ['font-bold', 'underline', 'text-gray-900'] }
    if (ft) return { text, classes: ['line-through', 'text-gray-600', 'font-normal'] }
    return { text: '—', classes: ['text-gray-400'] }
  }

  if (mode === 'exact_num' && row.field_type === 'number') {
    const nr = Number(res)
    if (Number.isNaN(nr)) return { text, classes: ['text-gray-800'] }
    const nt = Number(tipVal)
    if (Number.isNaN(nt)) return { text: '—', classes: ['text-gray-400'] }
    if (nt === nr) return { text, classes: ['font-bold', 'underline', 'text-gray-900'] }
    return { text, classes: ['line-through', 'text-gray-600', 'font-normal'] }
  }

  return { text, classes: ['text-gray-800'] }
}

</script>
