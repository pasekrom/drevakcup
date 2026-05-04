<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Vyplnění tipů</h2>

    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-6">
      <p
        v-if="tournamentStarted"
        class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
      >
        Turnaj už začal — tipy na zápasy nelze měnit. Uprav je před začátkem prvního zápasu turnaje.
      </p>
      <div
        v-for="match in matches"
        :id="'match-' + match.id"
        :key="match.id"
        class="card scroll-mt-24"
      >
        <div class="mb-4">
          <p class="font-medium mb-1">
            <TeamWithFlag :team="match.team_a" /> vs <TeamWithFlag :team="match.team_b" />
          </p>
          <p class="text-sm text-gray-600">{{ formatDateTime(match.date) }}</p>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label"><TeamWithFlag :team="match.team_a" /></label>
            <input
              v-model.number="tips[match.id].score_a"
              type="number"
              min="0"
              :disabled="tournamentStarted"
              class="input"
            />
          </div>
          <div>
            <label class="label"><TeamWithFlag :team="match.team_b" /></label>
            <input
              v-model.number="tips[match.id].score_b"
              type="number"
              min="0"
              :disabled="tournamentStarted"
              class="input"
            />
          </div>
        </div>
      </div>

      <div v-if="!tournamentStarted" class="flex justify-end">
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

    <MessageModal
      v-model="dialogOpen"
      :title="dialogTitle"
      :message="dialogMessage"
      :variant="dialogVariant"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import TeamWithFlag from '../../components/TeamWithFlag.vue'
import MessageModal from '../../components/MessageModal.vue'

const props = defineProps({
  cup: {
    type: Object,
    required: true,
  },
})

const router = useRouter()
const route = useRoute()
const matches = ref([])
const tips = ref({})
const loading = ref(true)
const saving = ref(false)

const tournamentStarted = computed(() => !!props.cup?.tournament_started)

const dialogOpen = ref(false)
const dialogTitle = ref('')
const dialogMessage = ref('')
const dialogVariant = ref('success')

function openFeedback(title, message, variant = 'success') {
  dialogTitle.value = title
  dialogMessage.value = message
  dialogVariant.value = variant
  dialogOpen.value = true
}

function redirectIfStarted() {
  if (props.cup?.tournament_started) {
    router.replace({ name: 'cup-home', params: { year: String(props.cup.year) } })
  }
}

watch(
  () => props.cup?.tournament_started,
  () => redirectIfStarted(),
  { immediate: true }
)

watch(
  () => route.hash,
  async () => {
    if (!matches.value.length) return
    await nextTick()
    scrollToMatchHash()
  }
)

onMounted(async () => {
  if (props.cup?.tournament_started) {
    loading.value = false
    return
  }
  await loadData()
})

async function loadData() {
  try {
    const matchesResponse = await api.get(`/matches/?cup=${props.cup.id}`)
    matches.value = matchesResponse.data.results || matchesResponse.data

    const tipsResponse = await api.get(`/match-tips/by_cup/?cup=${props.cup.id}`)
    const existingTips = tipsResponse.data

    matches.value.forEach((match) => {
      const existingTip = existingTips.find((t) => t.match.id === match.id)
      tips.value[match.id] = {
        score_a: existingTip?.score_a ?? null,
        score_b: existingTip?.score_b ?? null,
      }
    })
    await nextTick()
    scrollToMatchHash()
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

function scrollToMatchHash() {
  const h = route.hash
  if (!h || !h.startsWith('#match-')) return
  requestAnimationFrame(() => {
    document.querySelector(h)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

async function handleSubmit() {
  if (tournamentStarted.value) return
  saving.value = true
  try {
    const tipsArray = Object.entries(tips.value)
      .map(([matchId, tip]) => ({
        match_id: parseInt(matchId, 10),
        score_a: tip.score_a != null && !Number.isNaN(Number(tip.score_a)) ? Number(tip.score_a) : null,
        score_b: tip.score_b != null && !Number.isNaN(Number(tip.score_b)) ? Number(tip.score_b) : null,
      }))
      .filter((t) => t.score_a !== null && t.score_b !== null)

    await api.post('/match-tips/bulk_update/', { tips: tipsArray })
    openFeedback('Tipy uloženy', 'Tipy byly úspěšně uloženy.', 'success')
  } catch (error) {
    console.error('Error saving tips:', error)
    const detail = error.response?.data?.detail
    openFeedback(
      'Chyba při ukládání',
      typeof detail === 'string' ? detail : 'Tipy se nepodařilo uložit. Zkus to prosím znovu.',
      'error'
    )
  } finally {
    saving.value = false
  }
}

function formatDateTime(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString('cs-CZ')
}
</script>
