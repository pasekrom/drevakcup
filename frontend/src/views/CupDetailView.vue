<template>
  <div>
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>
    
    <div v-else-if="!cup" class="text-center py-12">
      <p class="text-gray-600 mb-4">Turnaj nenalezen.</p>
      <router-link to="/cups" class="btn btn-primary">Zpět na turnaje</router-link>
    </div>
    
    <div v-else-if="cup">
      <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">
          {{ cup.year }} - {{ cup.location }}
        </h1>
        <p class="text-gray-600">
          {{ formatDate(cup.date_start) }} - {{ formatDate(cup.date_end) }}
        </p>
      </div>

      <nav class="border-b border-gray-200 mb-8 relative">
        <div class="-mx-4 flex gap-6 overflow-x-auto px-4 scrollbar-none sm:mx-0 sm:gap-8 sm:px-0">
          <router-link
            :to="`/cup/${cup.year}`"
            class="shrink-0 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap"
            :class="isActive('cup-home') ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Domů
          </router-link>
          <router-link
            :to="`/cup/${cup.year}/matches`"
            class="shrink-0 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap"
            :class="isActive('cup-matches') ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Zápasy
          </router-link>
          <router-link
            v-if="!cup.tournament_started"
            :to="`/cup/${cup.year}/tips`"
            class="shrink-0 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap"
            :class="isActive('cup-tips') ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Vyplnění tipů
          </router-link>
          <router-link
            :to="`/cup/${cup.year}/special-tips`"
            class="shrink-0 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap"
            :class="isActive('cup-special-tips') ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Speciální tipy
          </router-link>
          <router-link
            :to="`/cup/${cup.year}/teams`"
            class="shrink-0 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap"
            :class="isActive('cup-teams') ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Týmy
          </router-link>
          <router-link
            :to="`/cup/${cup.year}/playoff`"
            class="shrink-0 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap"
            :class="isActive('cup-playoff') ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Play-off
          </router-link>
          <router-link
            :to="`/cup/${cup.year}/tips-overview`"
            class="shrink-0 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap"
            :class="isActive('cup-tips-overview') ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Přehled tipů
          </router-link>
          <router-link
            :to="`/cup/${cup.year}/ladder`"
            class="shrink-0 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap"
            :class="isActive('cup-ladder') ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Žebříček
          </router-link>
          <router-link
            :to="`/cup/${cup.year}/rules`"
            class="shrink-0 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap"
            :class="isActive('cup-rules') ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Pravidla
          </router-link>
        </div>

        <!-- Mobile hint that tabs continue horizontally -->
        <div class="pointer-events-none absolute inset-y-0 left-0 w-8 bg-gradient-to-r from-white to-transparent sm:hidden" />
        <div class="pointer-events-none absolute inset-y-0 right-0 w-14 bg-gradient-to-l from-white to-transparent sm:hidden" />
        <div class="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 sm:hidden">
          <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fill-rule="evenodd"
              d="M7.22 4.22a.75.75 0 0 1 1.06 0l5 5a.75.75 0 0 1 0 1.06l-5 5a.75.75 0 1 1-1.06-1.06L11.69 10 7.22 5.28a.75.75 0 0 1 0-1.06Z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
      </nav>

      <router-view :cup="cup" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const cup = ref(null)
const loading = ref(true)

async function fetchCup() {
  const year = route.params.year
  if (!year) return
  loading.value = true
  cup.value = null
  try {
    const response = await api.get(`/cups/?year=${year}`)
    const data = response.data
    const cups = data.results != null ? data.results : (Array.isArray(data) ? data : [data])
    const list = Array.isArray(cups) ? cups : (cups ? [cups] : [])
    cup.value = list.length ? list[0] : null
  } catch (error) {
    console.error('Error fetching cup:', error)
    cup.value = null
  } finally {
    loading.value = false
  }
}

onMounted(fetchCup)
watch(() => route.params.year, fetchCup)

function isActive(routeName) {
  return route.name === routeName
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('cs-CZ')
}
</script>
