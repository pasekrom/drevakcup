<template>
  <div id="app" class="min-h-screen">
    <NavBar v-if="!isBlankLayout" />
    <main :class="isBlankLayout ? '' : 'container mx-auto px-4 py-8'">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isBlankLayout = computed(() => route.meta?.layout === 'blank')
</script>
