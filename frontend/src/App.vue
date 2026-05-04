<template>
  <div id="app" class="min-h-screen">
    <NavBar />
    <main class="container mx-auto px-4 py-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
</script>
