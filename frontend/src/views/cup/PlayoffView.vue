<template>
  <div>
    <h2 class="text-2xl font-bold mb-2">Play-off</h2>
    <p class="text-gray-600 text-sm mb-8">
      Pavouk play-off — týmy a výsledky se zobrazí, jakmile je správce zadá v administraci.
    </p>

    <div v-if="loading" class="text-center py-12 text-gray-600">Načítání…</div>

    <div v-else-if="playoffs.length === 0" class="card text-center py-12 text-gray-600">
      <p>Pro tento turnaj zatím není vypsaný play-off.</p>
    </div>

    <div v-else class="space-y-10">
      <!-- Desktop pavouk -->
      <div class="hidden lg:block overflow-x-auto pb-4">
        <div class="mx-auto inline-flex items-stretch gap-0 min-h-[280px]">
          <!-- Sk. A: QF -> SF -->
          <div class="flex items-stretch">
            <div class="flex flex-col justify-around gap-6 py-1 w-[11.5rem] shrink-0">
              <PlayoffMatchCard :playoff="byType.QFA1" :label="typeLabel('QFA1')" />
              <PlayoffMatchCard :playoff="byType.QFA2" :label="typeLabel('QFA2')" />
            </div>
            <BracketJoinTwo />
            <div class="flex items-center px-1 w-[11.5rem] shrink-0">
              <PlayoffMatchCard :playoff="byType.SFA" :label="typeLabel('SFA')" />
            </div>
          </div>

          <div class="flex items-center self-center h-12 w-8 shrink-0">
            <BracketJoinSingle />
          </div>

          <div class="flex flex-col justify-center items-center gap-6 px-2 w-[12rem] shrink-0">
            <PlayoffMatchCard :playoff="byType.BMG" :label="typeLabel('BMG')" compact />
            <PlayoffMatchCard :playoff="byType.GMG" :label="typeLabel('GMG')" highlight />
          </div>

          <div class="flex items-center self-center h-12 w-8 shrink-0 scale-x-[-1]">
            <BracketJoinSingle />
          </div>

          <div class="flex items-stretch flex-row-reverse">
            <div class="flex flex-col justify-around gap-6 py-1 w-[11.5rem] shrink-0">
              <PlayoffMatchCard :playoff="byType.QFB1" :label="typeLabel('QFB1')" />
              <PlayoffMatchCard :playoff="byType.QFB2" :label="typeLabel('QFB2')" />
            </div>
            <BracketJoinTwo extra-class="scale-x-[-1]" />
            <div class="flex items-center px-1 w-[11.5rem] shrink-0">
              <PlayoffMatchCard :playoff="byType.SFB" :label="typeLabel('SFB')" />
            </div>
          </div>
        </div>
      </div>

      <!-- Mobil -->
      <div class="lg:hidden space-y-6">
        <div>
          <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Čtvrtfinále</h3>
          <div class="space-y-3">
            <PlayoffMatchCard v-for="t in qfTypes" :key="t" :playoff="byType[t]" :label="typeLabel(t)" />
          </div>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Semifinále</h3>
          <div class="space-y-3">
            <PlayoffMatchCard :playoff="byType.SFA" :label="typeLabel('SFA')" />
            <PlayoffMatchCard :playoff="byType.SFB" :label="typeLabel('SFB')" />
          </div>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Medaile</h3>
          <div class="space-y-3">
            <PlayoffMatchCard :playoff="byType.BMG" :label="typeLabel('BMG')" />
            <PlayoffMatchCard :playoff="byType.GMG" :label="typeLabel('GMG')" highlight />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import PlayoffMatchCard from '../../components/PlayoffMatchCard.vue'
import BracketJoinTwo from '../../components/BracketJoinTwo.vue'
import BracketJoinSingle from '../../components/BracketJoinSingle.vue'

const props = defineProps({
  cup: { type: Object, required: true },
})

const loading = ref(true)
const playoffs = ref([])

const ORDER = ['QFA1', 'QFA2', 'QFB1', 'QFB2', 'SFA', 'SFB', 'BMG', 'GMG']
const qfTypes = ['QFA1', 'QFA2', 'QFB1', 'QFB2']

const LABELS = {
  QFA1: 'Čtvrtfinále 1 (sk. A)',
  QFA2: 'Čtvrtfinále 2 (sk. A)',
  QFB1: 'Čtvrtfinále 1 (sk. B)',
  QFB2: 'Čtvrtfinále 2 (sk. B)',
  SFA: 'Semifinále (sk. A)',
  SFB: 'Semifinále (sk. B)',
  BMG: 'O bronz',
  GMG: 'Finále',
}

const byType = computed(() => {
  const m = {}
  for (const p of playoffs.value) {
    m[p.playoff_type] = p
  }
  return m
})

function typeLabel(t) {
  return LABELS[t] || t
}

onMounted(async () => {
  try {
    const res = await api.get(`/playoffs/?cup=${props.cup.id}`)
    const list = res.data.results ?? res.data ?? []
    const orderIndex = (t) => {
      const i = ORDER.indexOf(t)
      return i === -1 ? 99 : i
    }
    playoffs.value = [...list].sort((a, b) => orderIndex(a.playoff_type) - orderIndex(b.playoff_type))
  } catch (e) {
    console.error(e)
    playoffs.value = []
  } finally {
    loading.value = false
  }
})
</script>
