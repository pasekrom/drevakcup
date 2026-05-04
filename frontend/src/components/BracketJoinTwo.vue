<template>
  <svg
    class="h-full min-h-[140px] w-7 shrink-0 text-gray-300"
    :class="extraClass"
    viewBox="0 0 28 120"
    preserveAspectRatio="xMidYMid meet"
    aria-hidden="true"
  >
    <path
      d="M0 18 L14 18 L14 60 L28 60"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M0 102 L14 102 L14 60"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>

<script setup>
defineProps({
  extraClass: { type: String, default: '' },
})
</script>
