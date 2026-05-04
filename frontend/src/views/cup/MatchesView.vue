<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Zápasy</h2>

    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>

    <div v-else class="overflow-x-auto rounded-lg border border-gray-200">
      <table class="w-full text-left" :class="cup?.tournament_started ? 'min-w-[36rem]' : 'min-w-[44rem]'">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th scope="col" class="py-3 px-4 font-semibold text-gray-700">Zápas</th>
            <th scope="col" class="py-3 px-4 font-semibold text-gray-700 whitespace-nowrap">Datum, čas</th>
            <th scope="col" class="py-3 px-4 font-semibold text-gray-700 whitespace-nowrap">Můj tip</th>
            <th scope="col" class="py-3 px-4 font-semibold text-gray-700">Skóre</th>
            <th
              v-if="!cup?.tournament_started"
              scope="col"
              class="py-3 px-4 font-semibold text-gray-700 whitespace-nowrap text-right"
            >
              Tip
            </th>
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
            <td class="py-2.5 px-4 text-sm tabular-nums text-primary-700 font-semibold whitespace-nowrap">
              <span v-if="myTipText(match.id)">{{ myTipText(match.id) }}</span>
              <span v-else class="font-normal text-gray-400">—</span>
            </td>
            <td class="py-2.5 px-4 text-lg font-bold tabular-nums">
              <template v-if="finalScore(match) != null">
                {{ finalScore(match).a }} : {{ finalScore(match).b }}
                <span v-if="isOvertime(match)" class="text-xs font-medium text-amber-600 ml-1">OT</span>
              </template>
              <span v-else class="text-gray-400 font-normal">– : –</span>
            </td>
            <td v-if="!cup?.tournament_started" class="py-2.5 px-4 text-right whitespace-nowrap">
              <button
                type="button"
                class="btn btn-secondary text-sm py-1.5 px-3 whitespace-nowrap"
                @click="openTipModal(match)"
              >
                Upravit můj tip
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <MatchTipEditModal
      v-model="modalOpen"
      :match="modalMatch"
      :initial-tip="modalInitialTip"
      @saved="onTipSaved"
      @save-error="onTipSaveError"
    />
    <MessageModal
      v-model="messageOpen"
      :title="messageTitle"
      :message="messageMessage"
      variant="error"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import TeamWithFlag from '../../components/TeamWithFlag.vue'
import MatchTipEditModal from '../../components/MatchTipEditModal.vue'
import MessageModal from '../../components/MessageModal.vue'

const props = defineProps({
  cup: {
    type: Object,
    required: true,
  },
})

const matches = ref([])
const tipsByMatchId = ref({})
const loading = ref(true)

const modalOpen = ref(false)
const modalMatchId = ref(null)
const modalMatch = computed(() => matches.value.find((m) => m.id === modalMatchId.value) ?? null)
const modalInitialTip = computed(() => {
  const id = modalMatchId.value
  if (id == null) return null
  const t = tipsByMatchId.value[id]
  if (!t) return null
  return { score_a: t.score_a, score_b: t.score_b }
})

const messageOpen = ref(false)
const messageTitle = ref('')
const messageMessage = ref('')

onMounted(async () => {
  try {
    const [matchesRes, tipsRes] = await Promise.all([
      api.get(`/matches/?cup=${props.cup.id}`),
      api.get(`/match-tips/by_cup/?cup=${props.cup.id}`),
    ])
    matches.value = matchesRes.data.results || matchesRes.data
    const tipMap = {}
    for (const t of tipsRes.data) {
      const mid = t.match?.id
      if (mid != null) {
        tipMap[mid] = { score_a: t.score_a, score_b: t.score_b }
      }
    }
    tipsByMatchId.value = tipMap
  } catch (error) {
    console.error('Error loading matches:', error)
  } finally {
    loading.value = false
  }
})

function myTipText(matchId) {
  const t = tipsByMatchId.value[matchId]
  if (!t || t.score_a == null || t.score_b == null) return null
  return `${t.score_a} : ${t.score_b}`
}

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

function openTipModal(match) {
  modalMatchId.value = match.id
  modalOpen.value = true
}

function onTipSaved({ matchId, score_a, score_b }) {
  tipsByMatchId.value = {
    ...tipsByMatchId.value,
    [matchId]: { score_a, score_b },
  }
}

function onTipSaveError(msg) {
  messageTitle.value = 'Tip se nepodařilo uložit'
  messageMessage.value = msg || 'Zkus to prosím znovu.'
  messageOpen.value = true
}
</script>
