<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Speciální tipy</h2>
    
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-600">Načítání...</p>
    </div>
    
    <form v-else @submit.prevent="handleSubmit" class="space-y-6">
      <div class="card">
        <h3 class="text-xl font-bold mb-4">Finálové tipy</h3>
        <div class="space-y-4">
          <div>
            <label class="label">Vítěz turnaje</label>
            <select v-model="form.winner_id" class="input w-full">
              <option :value="null">Vyberte tým</option>
              <option v-for="team in allTeams" :key="team.id" :value="team.id">
                {{ team.name }}
              </option>
            </select>
          </div>
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="label">Finalista 1</label>
              <select v-model="form.final_a_id" class="input">
                <option :value="null">Vyberte tým</option>
                <option v-for="team in allTeams" :key="team.id" :value="team.id">
                  {{ team.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="label">Finalista 2</label>
              <select v-model="form.final_b_id" class="input">
                <option :value="null">Vyberte tým</option>
                <option v-for="team in allTeams" :key="team.id" :value="team.id">
                  {{ team.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="label">Tým 1, který se utká o bronz</label>
              <select v-model="form.bronze_a_id" class="input">
                <option :value="null">Vyberte tým</option>
                <option v-for="team in allTeams" :key="team.id" :value="team.id">
                  {{ team.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="label">Tým 2, který se utká o bronz</label>
              <select v-model="form.bronze_b_id" class="input">
                <option :value="null">Vyberte tým</option>
                <option v-for="team in allTeams" :key="team.id" :value="team.id">
                  {{ team.name }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <h3 class="text-xl font-bold mb-4">Skupiny</h3>
        <div class="grid md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-bold mb-3">Skupina A</h4>
            <div class="space-y-3">
              <div v-for="(label, index) in groupLabels" :key="`a-${index}`">
                <label class="label">{{ label }}</label>
                <select v-model="form[`group_a_${index + 1}_id`]" class="input">
                  <option :value="null">Vyberte tým</option>
                  <option v-for="team in groupATeams" :key="team.id" :value="team.id">
                    {{ team.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="label">Tým, který sestoupí</label>
                <select v-model="form.team_drop_a_id" class="input">
                  <option :value="null">Vyberte tým</option>
                  <option v-for="team in groupATeams" :key="team.id" :value="team.id">{{ team.name }}</option>
                </select>
              </div>
            </div>
          </div>
          <div>
            <h4 class="font-bold mb-3">Skupina B</h4>
            <div class="space-y-3">
              <div v-for="(label, index) in groupLabels" :key="`b-${index}`">
                <label class="label">{{ label }}</label>
                <select v-model="form[`group_b_${index + 1}_id`]" class="input">
                  <option :value="null">Vyberte tým</option>
                  <option v-for="team in groupBTeams" :key="team.id" :value="team.id">
                    {{ team.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="label">Tým, který sestoupí</label>
                <select v-model="form.team_drop_b_id" class="input">
                  <option :value="null">Vyberte tým</option>
                  <option v-for="team in groupBTeams" :key="team.id" :value="team.id">{{ team.name }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="text-xl font-bold mb-4">České tipy</h3>
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="label">Český střelec 1. gólu</label>
            <input v-model="form.czech_shooter_first" type="text" class="input" placeholder="Jméno hráče" />
          </div>
          <div>
            <label class="label">Český střelec posledního gólu</label>
            <input v-model="form.czech_shooter_last" type="text" class="input" placeholder="Jméno hráče" />
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="text-xl font-bold mb-4">Další tipy</h3>
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="label">Tým, který vstřelí nejvíce branek (celkem na MS)</label>
            <select v-model="form.team_most_goals_id" class="input">
              <option :value="null">Vyberte tým</option>
              <option v-for="team in allTeams" :key="team.id" :value="team.id">{{ team.name }}</option>
            </select>
          </div>
          <div>
            <label class="label">Tým, který obdrží nejméně branek (celkem na MS)</label>
            <select v-model="form.team_least_goals_id" class="input">
              <option :value="null">Vyberte tým</option>
              <option v-for="team in allTeams" :key="team.id" :value="team.id">{{ team.name }}</option>
            </select>
          </div>
          <div>
            <label class="label">Tým, který vstřelí první branku na MS</label>
            <select v-model="form.team_first_goal_id" class="input">
              <option :value="null">Vyberte tým</option>
              <option v-for="team in allTeams" :key="team.id" :value="team.id">{{ team.name }}</option>
            </select>
          </div>
          <div>
            <label class="label">Tým, který vstřelí poslední branku na MS</label>
            <select v-model="form.team_last_goal_id" class="input">
              <option :value="null">Vyberte tým</option>
              <option v-for="team in allTeams" :key="team.id" :value="team.id">{{ team.name }}</option>
            </select>
          </div>
          <div>
            <label class="label">Nejvíce branek v jednom utkání (dohromady)</label>
            <input v-model.number="form.max_goals_per_game" type="number" min="0" class="input" placeholder="0" />
          </div>
          <div>
            <label class="label">Počet remíz/prodloužení (celkem za MS)</label>
            <input v-model.number="form.overtimes" type="number" min="0" class="input" placeholder="0" />
          </div>
        </div>
      </div>
      
      <div class="flex justify-end">
        <button
          type="submit"
          :disabled="saving"
          class="btn btn-primary"
        >
          <span v-if="saving">Ukládání...</span>
          <span v-else>Uložit speciální tipy</span>
        </button>
      </div>
    </form>
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

const loading = ref(true)
const saving = ref(false)
const allTeams = ref([])
const groupATeams = ref([])
const groupBTeams = ref([])
const form = ref({
  winner_id: null,
  final_a_id: null,
  final_b_id: null,
  bronze_a_id: null,
  bronze_b_id: null,
  group_a_1_id: null,
  group_a_2_id: null,
  group_a_3_id: null,
  group_a_4_id: null,
  group_b_1_id: null,
  group_b_2_id: null,
  group_b_3_id: null,
  group_b_4_id: null,
  czech_shooter_first: '',
  czech_shooter_last: '',
  max_goals_per_game: null,
  team_most_goals_id: null,
  team_least_goals_id: null,
  team_first_goal_id: null,
  team_last_goal_id: null,
  team_drop_a_id: null,
  team_drop_b_id: null,
  overtimes: null,
})

const groupLabels = ['1. místo', '2. místo', '3. místo', '4. místo']

onMounted(async () => {
  await loadData()
})

async function loadData() {
  try {
    // Load teams
    const teamsResponse = await api.get(`/teams/?cup=${props.cup.id}`)
    const teams = teamsResponse.data.results || teamsResponse.data
    allTeams.value = teams
    groupATeams.value = teams.filter(t => t.group === 'A')
    groupBTeams.value = teams.filter(t => t.group === 'B')
    
    // Load existing special tip
    try {
      const tipResponse = await api.get(`/special-tips/by_cup/?cup=${props.cup.id}`)
      const tip = tipResponse.data
      if (tip) {
        form.value.winner_id = tip.winner?.id ?? null
        form.value.final_a_id = tip.final_a?.id ?? null
        form.value.final_b_id = tip.final_b?.id ?? null
        form.value.bronze_a_id = tip.bronze_a?.id ?? null
        form.value.bronze_b_id = tip.bronze_b?.id ?? null
        form.value.group_a_1_id = tip.group_a_1?.id ?? null
        form.value.group_a_2_id = tip.group_a_2?.id ?? null
        form.value.group_a_3_id = tip.group_a_3?.id ?? null
        form.value.group_a_4_id = tip.group_a_4?.id ?? null
        form.value.group_b_1_id = tip.group_b_1?.id ?? null
        form.value.group_b_2_id = tip.group_b_2?.id ?? null
        form.value.group_b_3_id = tip.group_b_3?.id ?? null
        form.value.group_b_4_id = tip.group_b_4?.id ?? null
        form.value.czech_shooter_first = tip.czech_shooter_first ?? ''
        form.value.czech_shooter_last = tip.czech_shooter_last ?? ''
        form.value.max_goals_per_game = tip.max_goals_per_game ?? null
        form.value.team_most_goals_id = tip.team_most_goals?.id ?? null
        form.value.team_least_goals_id = tip.team_least_goals?.id ?? null
        form.value.team_first_goal_id = tip.team_first_goal?.id ?? null
        form.value.team_last_goal_id = tip.team_last_goal?.id ?? null
        form.value.team_drop_a_id = tip.team_drop_a?.id ?? null
        form.value.team_drop_b_id = tip.team_drop_b?.id ?? null
        form.value.overtimes = tip.overtimes ?? null
      }
    } catch (error) {
      // No existing tip, that's okay
    }
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  saving.value = true
  try {
    const data = {
      cup_id: props.cup.id,
      ...form.value,
    }
    // Ensure null instead of empty string for unset team ids
    const teamKeys = [
      'winner_id', 'final_a_id', 'final_b_id', 'bronze_a_id', 'bronze_b_id',
      'group_a_1_id', 'group_a_2_id', 'group_a_3_id', 'group_a_4_id',
      'group_b_1_id', 'group_b_2_id', 'group_b_3_id', 'group_b_4_id',
      'team_most_goals_id', 'team_least_goals_id', 'team_first_goal_id', 'team_last_goal_id',
      'team_drop_a_id', 'team_drop_b_id',
    ]
    teamKeys.forEach(k => {
      if (data[k] === '' || data[k] === undefined) data[k] = null
    })
    if (data.max_goals_per_game === '' || data.max_goals_per_game === undefined) data.max_goals_per_game = null
    if (data.overtimes === '' || data.overtimes === undefined) data.overtimes = null

    await api.post('/special-tips/', data)
    alert('Speciální tipy byly úspěšně uloženy!')
  } catch (error) {
    console.error('Error saving special tips:', error)
    const msg = error.response?.data?.detail
      || (typeof error.response?.data === 'object' && Object.keys(error.response?.data).length
        ? JSON.stringify(error.response.data)
        : null)
    alert(msg || 'Chyba při ukládání speciálních tipů')
  } finally {
    saving.value = false
  }
}
</script>
