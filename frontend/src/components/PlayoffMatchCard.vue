<template>
  <div
    v-if="playoff"
    class="rounded-lg border bg-white shadow-sm overflow-hidden"
    :class="[
      highlight ? 'border-primary-400 ring-1 ring-primary-200' : 'border-gray-200',
      compact ? 'text-sm' : '',
    ]"
  >
    <div class="px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-gray-500 bg-gray-50 border-b border-gray-100">
      {{ label }}
    </div>
    <div :class="compact ? 'p-2 space-y-1.5' : 'p-3 space-y-2'">
      <div class="flex items-center justify-between gap-1 min-h-[1.5rem] text-sm">
        <TeamWithFlag v-if="playoff.team_a" :team="playoff.team_a" />
        <span v-else class="text-gray-400">?</span>
        <span v-if="fs" class="tabular-nums font-bold text-gray-900 shrink-0">{{ fs.a }}</span>
        <span v-else class="text-gray-300 text-sm">–</span>
      </div>
      <div class="flex items-center justify-between gap-1 min-h-[1.5rem] text-sm">
        <TeamWithFlag v-if="playoff.team_b" :team="playoff.team_b" />
        <span v-else class="text-gray-400">?</span>
        <span v-if="fs" class="tabular-nums font-bold text-gray-900 shrink-0">{{ fs.b }}</span>
        <span v-else class="text-gray-300 text-sm">–</span>
      </div>
      <div v-if="fs && ot" class="text-[10px] text-amber-600 font-medium">Po prodloužení / nájezdy</div>
      <div class="text-[10px] text-gray-500 pt-0.5 border-t border-gray-100">{{ shortDate }}</div>
    </div>
  </div>
  <div v-else class="rounded-lg border border-dashed border-gray-200 bg-gray-50 p-4 text-center text-sm text-gray-400">
    {{ label }}
  </div>
</template>

<script setup>
import { computed } from 'vue'
import TeamWithFlag from './TeamWithFlag.vue'

const props = defineProps({
  playoff: { type: Object, default: null },
  label: { type: String, default: '' },
  compact: { type: Boolean, default: false },
  highlight: { type: Boolean, default: false },
})

const fs = computed(() => {
  const p = props.playoff
  if (!p) return null
  const a = p.score_a_final != null ? p.score_a_final : p.score_a
  const b = p.score_b_final != null ? p.score_b_final : p.score_b
  if (a == null || b == null) return null
  return { a, b }
})

const ot = computed(() => {
  const p = props.playoff
  if (!p) return false
  if (p.overtime) return true
  const sa = p.score_a
  const sb = p.score_b
  const fa = p.score_a_final
  const fb = p.score_b_final
  if (sa == null || fa == null) return false
  return sa !== fa || sb !== fb
})

const shortDate = computed(() => {
  if (!props.playoff?.date) return ''
  return new Date(props.playoff.date).toLocaleString('cs-CZ', {
    day: 'numeric',
    month: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
})
</script>
