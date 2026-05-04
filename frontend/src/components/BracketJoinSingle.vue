<template>
  <svg
    class="w-8 max-w-[2rem] shrink-0 text-gray-300"
    :class="extraClass"
    viewBox="0 0 32 48"
    preserveAspectRatio="none"
    aria-hidden="true"
  >
    <path d="M0 24 H32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
  </svg>
</template>

<script setup>
defineProps({
  extraClass: { type: String, default: '' },
})
</script>
