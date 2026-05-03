<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Žebříček</h2>
    
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>
    
    <div v-else class="card">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Pořadí
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Uživatel
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Část A
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Část B
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Celkem
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="entry in ladder" :key="entry.user.id">
              <td class="px-6 py-4 whitespace-nowrap font-bold">
                {{ entry.rank }}.
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ entry.user.display_name || entry.user.name || entry.user.email }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ entry.points_a }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ entry.points_b }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap font-bold">
                {{ entry.points_c }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="ladder.length === 0 && !loading" class="py-6 text-center text-gray-500">
        Zatím žádná data. Vyplňte tipy a nechte si dopočítat body.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const props = defineProps({
  cup: {
    type: Object,
    required: true,
  },
})

const ladder = ref([])
const loading = ref(true)

onMounted(async () => {
  if (!props.cup?.id && !props.cup?.year) return
  try {
    const params = props.cup.id
      ? `cup=${props.cup.id}`
      : `year=${props.cup.year}`
    const response = await api.get(`/user-points/ladder/?${params}`)
    ladder.value = response.data
  } catch (error) {
    console.error('Error loading ladder:', error)
  } finally {
    loading.value = false
  }
})
</script>
