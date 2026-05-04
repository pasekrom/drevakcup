<template>
  <span class="inline-flex items-center gap-2">
    <img
      v-if="team?.flag_url"
      :src="team.flag_url"
      :alt="team?.display_name || team?.name"
      class="w-6 h-4 object-contain rounded flex-shrink-0"
      loading="lazy"
    />
    <span class="w-4 h-4 flex-shrink-0 rounded bg-gray-200" v-else-if="showPlaceholder" />
    <span>{{ labelText }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  team: {
    type: Object,
    default: null,
  },
  showPlaceholder: {
    type: Boolean,
    default: true,
  },
  /** 'name' = celý název z DB (default), 'shortcut' = CZE/CAN pro přehledové tabulky */
  display: {
    type: String,
    default: 'name',
    validator: (v) => v === 'name' || v === 'shortcut',
  },
})

const labelText = computed(() => {
  const t = props.team
  if (!t) return '—'
  if (props.display === 'shortcut') {
    return t.shortcut || t.name || '—'
  }
  // Režim „celý název“: zkratku použij jen když v DB opravdu není nic rozumného (jinak starý build zobrazil CZE i u „Česko“).
  const full = String(t.display_name || t.name || '').trim()
  if (full) return full
  return t.shortcut || '—'
})
</script>
