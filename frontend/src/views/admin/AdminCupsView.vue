<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold">Správa turnajů</h1>
      <router-link to="/admin/cups/new" class="btn btn-primary">
        Přidat turnaj
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>

    <div v-else class="card">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rok</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Místo</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Od</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Do</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Akce</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="cup in cups" :key="cup.id">
            <td class="px-6 py-4 whitespace-nowrap font-medium">{{ cup.year }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ cup.location }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ formatDate(cup.date_start) }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ formatDate(cup.date_end) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right">
              <router-link
                :to="`/admin/cups/${cup.id}`"
                class="text-primary-600 hover:underline mr-4"
              >
                Upravit / zápasy
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="cups.length === 0" class="py-8 text-center text-gray-500">
        Žádné turnaje. Přidejte první turnaj.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const cups = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/cups/')
    cups.value = res.data.results ?? res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('cs-CZ')
}
</script>
