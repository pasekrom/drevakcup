<template>
  <span class="inline-flex items-center gap-2">
    <img
      v-if="team?.flag_url"
      :src="team.flag_url"
      :alt="team?.name"
      class="w-6 h-4 object-contain rounded flex-shrink-0"
      loading="lazy"
    />
    <span class="w-4 h-4 flex-shrink-0 rounded bg-gray-200" v-else-if="showPlaceholder" />
    <span>{{ team?.shortcut || team?.name || '—' }}</span>
  </span>
</template>

<script setup>
defineProps({
  team: {
    type: Object,
    default: null,
  },
  showPlaceholder: {
    type: Boolean,
    default: true,
  },
})
</script>
