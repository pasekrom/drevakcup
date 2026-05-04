<template>
  <div>
    <h2 class="text-2xl font-bold mb-2">Přehled tipů</h2>
    <p class="text-gray-600 text-sm mb-6">
      Tipy všech hráčů u zápasů a u speciálu. Před začátkem prvního zápasu turnaje se místo tipů zobrazuje <span class="font-mono">?:?</span>.
    </p>

    <div v-if="loading" class="text-center py-12 text-gray-600">Načítání…</div>

    <template v-else>
      <p v-if="loadError" class="text-red-700 mb-8">
        {{ loadError }}
      </p>
      <p v-else-if="!matrix.users?.length" class="text-gray-600 mb-8">
        Zatím tu nejsou žádné tipy od hráčů.
      </p>

      <template v-else-if="!loadError">
        <!-- 1. část: zápasy -->
        <h3 class="text-lg font-bold text-gray-900 mb-3">1. část – zápasy</h3>
        <div class="w-full max-w-full overflow-x-auto rounded-lg border border-gray-200 mb-12 shadow-sm">
          <table class="text-sm border-collapse min-w-max w-max">
            <thead>
              <tr class="bg-gray-100 border-b border-gray-200">
                <th class="sticky left-0 z-20 bg-gray-100 px-3 py-2 text-left font-semibold text-gray-700 whitespace-nowrap border-r border-gray-200 shadow-[2px_0_4px_rgba(0,0,0,0.06)] min-w-[9rem]">
                  Zápas
                </th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700 whitespace-nowrap border-r border-gray-200 bg-gray-100 min-w-[6.5rem]">
                  Datum
                </th>
                <th class="px-3 py-2 text-center font-semibold text-gray-700 whitespace-nowrap border-r border-gray-200 bg-gray-100 min-w-[5rem]">
                  Výsledek
                </th>
                <th
                  v-for="(u, ui) in usersSortedMatches"
                  :key="'h-' + u.id"
                  class="px-2 py-2 text-center font-semibold text-gray-800 whitespace-nowrap min-w-[4.75rem] border-r border-gray-200/80"
                  :class="userColClass(ui)"
                >
                  {{ u.display_name }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="m in matrix.matches"
                :key="m.id"
                class="border-b border-gray-100 hover:bg-gray-50/80"
              >
                <td class="sticky left-0 z-10 bg-white px-3 py-2 border-r border-gray-200 shadow-[2px_0_4px_rgba(0,0,0,0.04)] min-w-[9rem]">
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
                  :key="m.id + '-' + u.id"
                  class="px-2 py-2 text-center tabular-nums border-r border-gray-100"
                  :class="userColClass(ui)"
                >
                  <template
                    v-for="p in [matchTipPresentation(m, m.tips[String(u.id)], matrix.tournament_started)]"
                    :key="'p-' + u.id"
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
                  v-for="(u, ui) in usersSortedMatches"
                  :key="'fa-' + u.id"
                  class="px-2 py-2 text-center tabular-nums border-r border-gray-200/80"
                  :class="userColClass(ui)"
                >
                  {{ u.points_part_a ?? 0 }}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- 2. část: speciál -->
        <h3 class="text-lg font-bold text-gray-900 mb-3">2. část – speciální tipy</h3>
        <div class="w-full max-w-full overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
          <table class="text-sm border-collapse min-w-max w-max">
            <thead>
              <tr class="bg-gray-100 border-b border-gray-200">
                <th class="sticky left-0 z-20 bg-gray-100 px-3 py-2 text-left font-semibold text-gray-700 border-r border-gray-200 min-w-[14rem]">
                  Položka
                </th>
                <th class="px-2 py-2 text-center font-semibold text-gray-700 whitespace-nowrap border-r border-gray-200 bg-amber-50/60">
                  Body
                </th>
                <th class="px-3 py-2 text-center font-semibold text-gray-700 border-r border-gray-200 bg-gray-100 min-w-[7rem]">
                  Výsledek
                </th>
                <th
                  v-for="(u, ui) in usersSortedSpecial"
                  :key="'sh-' + u.id"
                  class="px-2 py-2 text-center font-semibold text-gray-800 whitespace-nowrap min-w-[5rem] border-r border-gray-200/80"
                  :class="userColClass(ui)"
                >
                  {{ u.display_name }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in matrix.special_rows"
                :key="row.tip_field"
                class="border-b border-gray-100 hover:bg-gray-50/80"
              >
                <td class="sticky left-0 z-10 bg-white px-3 py-2 text-gray-900 border-r border-gray-200">
                  {{ row.label }}
                </td>
                <td class="px-2 py-2 text-center text-amber-900/90 font-medium border-r border-gray-200 bg-amber-50/40">
                  {{ row.points }}
                </td>
                <td class="px-3 py-2 text-center border-r border-gray-200 bg-gray-50/40 text-gray-900">
                  {{ formatSpecialResult(row, matrix.special_result) }}
                </td>
                <td
                  v-for="(u, ui) in usersSortedSpecial"
                  :key="row.tip_field + '-' + u.id"
                  class="px-2 py-2 text-center border-r border-gray-100"
                  :class="userColClass(ui)"
                >
                  <template
                    v-for="p in [
                      specialTipPresentation(
                        row,
                        row.tips[String(u.id)],
                        matrix.special_result,
                        matrix.tournament_started,
                      ),
                    ]"
                    :key="'sp-' + u.id"
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
                  Celkem – část B
                </td>
                <td
                  v-for="(u, ui) in usersSortedSpecial"
                  :key="'fb-' + u.id"
                  class="px-2 py-2 text-center tabular-nums border-r border-gray-200/80"
                  :class="userColClass(ui)"
                >
                  {{ u.points_part_b ?? 0 }}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import TeamWithFlag from '../../components/TeamWithFlag.vue'

const props = defineProps({
  cup: { type: Object, required: true },
})

const loading = ref(true)
const loadError = ref('')
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

const teamsById = computed(() => {
  const m = new Map()
  for (const t of matrix.value.teams || []) {
    m.set(t.id, t)
  }
  return m
})

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

const usersSortedSpecial = computed(() => {
  const u = matrix.value.users || []
  return [...u].sort((a, b) => compareUsersByPointsThenName(a, b, 'points_part_b'))
})

function userColClass(index) {
  return USER_BG[index % USER_BG.length]
}

onMounted(async () => {
  loadError.value = ''
  try {
    const res = await api.get(`/cups/${props.cup.id}/tips_matrix/`)
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
    s += ' p'
  }
  return s
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
