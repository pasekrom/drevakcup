<template>
  <div v-if="loading" class="text-center py-12">Načítání...</div>
  <div v-else-if="cup" class="space-y-8">
    <div class="flex flex-wrap justify-between items-start gap-4">
      <div>
        <h1 class="text-3xl font-bold">{{ cup.year }} – {{ cup.location }}</h1>
        <p class="text-gray-600 mt-1">
          {{ formatDate(cup.date_start) }} – {{ formatDate(cup.date_end) }}
        </p>
      </div>
      <div class="flex gap-2">
        <button
          type="button"
          :disabled="calculatingPoints"
          class="btn btn-primary"
          @click="recalculatePoints"
        >
          {{ calculatingPoints ? 'Počítám…' : 'Přepočítat body' }}
        </button>
        <router-link to="/admin/cups" class="btn btn-secondary">← Zpět na turnaje</router-link>
      </div>
    </div>

    <!-- Upravit turnaj -->
    <div class="card">
      <h2 class="text-xl font-bold mb-4">Upravit turnaj</h2>
      <form @submit.prevent="saveCup" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="label">Rok</label>
          <input v-model.number="editForm.year" type="number" class="input" />
        </div>
        <div>
          <label class="label">Místo</label>
          <input v-model="editForm.location" type="text" class="input" />
        </div>
        <div>
          <label class="label">Datum začátku</label>
          <input v-model="editForm.date_start" type="date" class="input" />
        </div>
        <div>
          <label class="label">Datum konce</label>
          <input v-model="editForm.date_end" type="date" class="input" />
        </div>
        <div class="md:col-span-2">
          <button type="submit" :disabled="savingCup" class="btn btn-primary">
            {{ savingCup ? 'Ukládám...' : 'Uložit změny turnaje' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Týmy -->
    <div class="card">
      <h2 class="text-xl font-bold mb-4">Týmy</h2>
      <form v-if="showTeamForm" @submit.prevent="addTeam" class="mb-4 p-4 bg-gray-50 rounded-lg flex flex-wrap gap-4 items-end">
        <div class="flex-1 min-w-[120px]">
          <label class="label">Název týmu</label>
          <input v-model="teamForm.name" type="text" required class="input" placeholder="Česko" />
        </div>
        <div class="w-24">
          <label class="label">Skupina</label>
          <select v-model="teamForm.group" class="input">
            <option value="A">A</option>
            <option value="B">B</option>
          </select>
        </div>
        <button type="submit" :disabled="savingTeam" class="btn btn-primary">Přidat</button>
        <button type="button" @click="showTeamForm = false" class="btn btn-secondary">Zrušit</button>
      </form>
      <button v-else @click="showTeamForm = true" class="btn btn-primary mb-4">Přidat tým</button>
      <div class="-mx-4 overflow-x-auto px-4 scrollbar-none sm:mx-0 sm:px-0">
        <table class="min-w-[44rem] w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100 select-none"
                @click="setTeamsSort('name')"
              >
                Tým {{ sortTeamsBy === 'name' ? (teamsSortDir === 'asc' ? '↑' : '↓') : '' }}
              </th>
              <th
                class="px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100 select-none"
                @click="setTeamsSort('group')"
              >
                Skupina {{ sortTeamsBy === 'group' ? (teamsSortDir === 'asc' ? '↑' : '↓') : '' }}
              </th>
              <th
                class="px-6 py-2 text-right text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100 select-none"
                @click="setTeamsSort('gp')"
              >
                Z {{ sortTeamsBy === 'gp' ? (teamsSortDir === 'asc' ? '↑' : '↓') : '' }}
              </th>
              <th
                class="px-6 py-2 text-right text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100 select-none"
                @click="setTeamsSort('win')"
              >
                V {{ sortTeamsBy === 'win' ? (teamsSortDir === 'asc' ? '↑' : '↓') : '' }}
              </th>
              <th
                class="px-6 py-2 text-right text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100 select-none"
                @click="setTeamsSort('los')"
              >
                P {{ sortTeamsBy === 'los' ? (teamsSortDir === 'asc' ? '↑' : '↓') : '' }}
              </th>
              <th
                class="px-6 py-2 text-right text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100 select-none"
                @click="setTeamsSort('gf')"
              >
                GV {{ sortTeamsBy === 'gf' ? (teamsSortDir === 'asc' ? '↑' : '↓') : '' }}
              </th>
              <th
                class="px-6 py-2 text-right text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100 select-none"
                @click="setTeamsSort('ga')"
              >
                GO {{ sortTeamsBy === 'ga' ? (teamsSortDir === 'asc' ? '↑' : '↓') : '' }}
              </th>
              <th
                class="px-6 py-2 text-right text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100 select-none"
                @click="setTeamsSort('points')"
              >
                Body {{ sortTeamsBy === 'points' ? (teamsSortDir === 'asc' ? '↑' : '↓') : '' }}
              </th>
              <th class="px-6 py-2 text-right text-xs font-medium text-gray-500 uppercase">Akce</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="t in sortedTeams" :key="t.id">
              <td class="px-6 py-2 whitespace-nowrap"><TeamWithFlag :team="t" /></td>
              <td class="px-6 py-2 whitespace-nowrap">{{ t.group }}</td>
              <td class="px-6 py-2 text-right whitespace-nowrap">{{ t.gp ?? 0 }}</td>
              <td class="px-6 py-2 text-right whitespace-nowrap">{{ t.win ?? 0 }}</td>
              <td class="px-6 py-2 text-right whitespace-nowrap">{{ t.los ?? 0 }}</td>
              <td class="px-6 py-2 text-right whitespace-nowrap">{{ t.gf ?? 0 }}</td>
              <td class="px-6 py-2 text-right whitespace-nowrap">{{ t.ga ?? 0 }}</td>
              <td class="px-6 py-2 text-right font-medium whitespace-nowrap">{{ t.points ?? 0 }}</td>
              <td class="px-6 py-2 text-right whitespace-nowrap">
                <button type="button" @click="deleteTeam(t.id)" class="text-red-600 hover:underline text-sm">
                  Smazat
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="teams.length === 0" class="py-4 text-gray-500">Žádné týmy. Přidejte týmy před přidáním zápasů.</p>
    </div>

    <!-- Zápasy -->
    <div class="card">
      <h2 class="text-xl font-bold mb-4">Zápasy</h2>
      <form v-if="showMatchForm" @submit.prevent="addMatch" class="mb-4 p-4 bg-gray-50 rounded-lg space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Tým A</label>
            <select v-model.number="matchForm.team_a_id" required class="input">
              <option :value="null">— vyberte —</option>
              <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.display_name || t.name }}</option>
            </select>
          </div>
          <div>
            <label class="label">Tým B</label>
            <select v-model.number="matchForm.team_b_id" required class="input">
              <option :value="null">— vyberte —</option>
              <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.display_name || t.name }}</option>
            </select>
          </div>
        </div>
        <div>
          <label class="label">Datum a čas</label>
          <input v-model="matchForm.date" type="datetime-local" required class="input" />
        </div>
        <div class="flex gap-3">
          <button type="submit" :disabled="savingMatch" class="btn btn-primary">Přidat zápas</button>
          <button type="button" @click="showMatchForm = false" class="btn btn-secondary">Zrušit</button>
        </div>
      </form>
      <button v-else @click="showMatchForm = true" class="btn btn-primary mb-4">Přidat zápas</button>
      <div class="-mx-4 overflow-x-auto px-4 scrollbar-none sm:mx-0 sm:px-0">
        <table class="admin-matches-table min-w-[56rem] w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Datum</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Zápas</th>
              <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Zákl.</th>
              <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Konečný</th>
              <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Nájezdy</th>
              <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Akce</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="m in matches" :key="m.id">
              <td class="px-4 py-2 whitespace-nowrap text-sm">{{ formatDateTime(m.date) }}</td>
              <td class="px-4 py-2 whitespace-nowrap">
                <TeamWithFlag :team="m.team_a" /> – <TeamWithFlag :team="m.team_b" />
              </td>
              <td class="px-4 py-2">
                <div class="flex items-center justify-center gap-1">
                  <input
                    v-model.number="matchScores[m.id].score_a"
                    type="number"
                    min="0"
                    class="input input-score w-14 min-w-[3rem] text-center"
                    placeholder="0"
                  />
                  <span class="text-gray-500">:</span>
                  <input
                    v-model.number="matchScores[m.id].score_b"
                    type="number"
                    min="0"
                    class="input input-score w-14 min-w-[3rem] text-center"
                    placeholder="0"
                  />
                </div>
              </td>
              <td class="px-4 py-2">
                <div class="flex items-center justify-center gap-1">
                  <input
                    v-model.number="matchScores[m.id].score_a_final"
                    type="number"
                    min="0"
                    class="input input-score w-14 min-w-[3rem] text-center"
                    placeholder="0"
                  />
                  <span class="text-gray-500">:</span>
                  <input
                    v-model.number="matchScores[m.id].score_b_final"
                    type="number"
                    min="0"
                    class="input input-score w-14 min-w-[3rem] text-center"
                    placeholder="0"
                  />
                </div>
              </td>
              <td class="px-4 py-2 text-center">
                <input
                  v-model="matchScores[m.id].shootout"
                  type="checkbox"
                  class="h-4 w-4 accent-primary-600"
                  :disabled="savingMatchId === m.id"
                  :title="'Zaškrtni, pokud byl zápas rozhodnut na nájezdy (konečné skóre je pak po nájezdech).'"
                />
              </td>
              <td class="px-4 py-2 text-right whitespace-nowrap">
                <div class="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    :disabled="savingMatchId === m.id"
                    class="btn btn-secondary text-sm py-1 px-2"
                    @click="saveMatchResult(m)"
                  >
                    {{ savingMatchId === m.id ? '…' : 'Uložit' }}
                  </button>
                  <button type="button" @click="deleteMatch(m.id)" class="text-red-600 hover:underline text-sm">
                    Smazat
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="matches.length === 0" class="py-4 text-gray-500">Žádné zápasy.</p>
    </div>

    <!-- Play-off -->
    <div class="card">
      <h2 class="text-xl font-bold mb-2">Play-off</h2>
      <p class="text-gray-600 text-sm mb-4">
        Čtvrtfinále (4×), semifinále (2×), zápas o bronz a finále — u každého vyber týmy a později dopiš skóre.
        Údaje <strong>finále, bronz a vítěz</strong> se po uložení skóre nebo „Přepočítat body“ doplní do výsledků speciálu (už je nevyplňuješ ručně ve speciálu).
      </p>
      <div v-if="playoffs.length === 0" class="flex flex-wrap items-center gap-3">
        <button
          type="button"
          :disabled="ensuringPlayoffs"
          class="btn btn-primary"
          @click="ensurePlayoffs"
        >
          {{ ensuringPlayoffs ? 'Zakládám…' : 'Založit play-off zápasy' }}
        </button>
        <span class="text-sm text-gray-500">Vytvoří 8 řádků (QF → finále).</span>
      </div>
      <div v-else class="space-y-8">
        <div v-for="group in playoffDisplayGroups" :key="group.title">
          <h3 class="text-lg font-semibold text-gray-900 mb-3">{{ group.title }}</h3>
          <div class="overflow-x-auto rounded-lg border border-gray-200">
            <table class="w-full min-w-[52rem] text-left text-sm">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="py-2 px-3 font-medium text-gray-600">Kód</th>
                  <th class="py-2 px-3 font-medium text-gray-600">Datum</th>
                  <th class="py-2 px-3 font-medium text-gray-600">Tým A</th>
                  <th class="py-2 px-3 font-medium text-gray-600">Tým B</th>
                  <th class="py-2 px-3 font-medium text-gray-600 text-center">Zákl.</th>
                  <th class="py-2 px-3 font-medium text-gray-600 text-center">Konečný</th>
                  <th class="py-2 px-3 font-medium text-gray-600 text-center whitespace-nowrap">Nájezdy</th>
                  <th class="py-2 px-3 font-medium text-gray-600 text-right w-px">Akce</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <template v-for="p in group.rows" :key="p.id">
                  <tr v-if="playoffScores[p.id]">
                    <td class="py-2 px-3 font-mono text-xs text-gray-500">{{ p.playoff_type }}</td>
                    <td class="py-2 px-3">
                      <input
                        v-model="playoffScores[p.id].date"
                        type="datetime-local"
                        class="input py-1 text-sm min-w-[11rem]"
                      />
                    </td>
                    <td class="py-2 px-3">
                      <select v-model="playoffScores[p.id].team_a_id" class="input py-1 text-sm w-full max-w-[10rem]">
                        <option :value="null">—</option>
                        <option v-for="t in teams" :key="'pa-' + p.id + '-' + t.id" :value="t.id">{{ t.display_name || t.name }}</option>
                      </select>
                    </td>
                    <td class="py-2 px-3">
                      <select v-model="playoffScores[p.id].team_b_id" class="input py-1 text-sm w-full max-w-[10rem]">
                        <option :value="null">—</option>
                        <option v-for="t in teams" :key="'pb-' + p.id + '-' + t.id" :value="t.id">{{ t.display_name || t.name }}</option>
                      </select>
                    </td>
                    <td class="py-2 px-3">
                      <div class="flex items-center justify-center gap-1">
                        <input
                          v-model.number="playoffScores[p.id].score_a"
                          type="number"
                          min="0"
                          class="input input-score w-12 text-center py-1"
                        />
                        <span class="text-gray-400">:</span>
                        <input
                          v-model.number="playoffScores[p.id].score_b"
                          type="number"
                          min="0"
                          class="input input-score w-12 text-center py-1"
                        />
                      </div>
                    </td>
                    <td class="py-2 px-3">
                      <div class="flex items-center justify-center gap-1">
                        <input
                          v-model.number="playoffScores[p.id].score_a_final"
                          type="number"
                          min="0"
                          class="input input-score w-12 text-center py-1"
                        />
                        <span class="text-gray-400">:</span>
                        <input
                          v-model.number="playoffScores[p.id].score_b_final"
                          type="number"
                          min="0"
                          class="input input-score w-12 text-center py-1"
                        />
                      </div>
                    </td>
                    <td class="py-2 px-3 text-center">
                      <input
                        v-model="playoffScores[p.id].shootout"
                        type="checkbox"
                        class="h-4 w-4 accent-primary-600"
                        :disabled="savingPlayoffId === p.id"
                        :title="'Zaškrtni, pokud byl zápas rozhodnut na nájezdy (konečné skóre je pak po nájezdech).'"
                      />
                    </td>
                    <td class="py-2 px-3 text-right">
                      <button
                        type="button"
                        class="btn btn-secondary text-xs py-1 px-2"
                        :disabled="savingPlayoffId === p.id"
                        @click="savePlayoffResult(p)"
                      >
                        {{ savingPlayoffId === p.id ? '…' : 'Uložit' }}
                      </button>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Výsledky speciálních tipů -->
    <div class="card">
      <h2 class="text-xl font-bold mb-4">Výsledky speciálních tipů</h2>
      <p class="text-gray-600 mb-4">Vyplň skutečné výsledky (skupiny, čeští střelci, …). Finále, bronz a vítěz jdou z play-off výše.</p>
      <div v-if="specialLoading" class="py-4 text-gray-500">Načítání…</div>
      <form v-else @submit.prevent="saveSpecialResults" class="space-y-6">
        <div class="space-y-4">
          <div class="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-4 md:col-span-2">
            <p class="text-sm font-medium text-gray-800">Z play-off → speciál (jen náhled)</p>
            <p class="text-xs text-gray-600 mt-1 mb-3">
              Po uložení řádku play-off nebo „Přepočítat body“ se sem promítnou GMG (finále), BMG (o bronz) a vítěz z finále.
            </p>
            <div class="grid sm:grid-cols-2 gap-3 text-sm">
              <div><span class="text-gray-600">Vítěz:</span> <span class="ml-1 font-medium">{{ teamNameById(specialForm.winner_id) }}</span></div>
              <div><span class="text-gray-600">Finále:</span> <span class="ml-1 font-medium">{{ teamNameById(specialForm.final_a_id) }}</span> vs <span class="font-medium">{{ teamNameById(specialForm.final_b_id) }}</span></div>
              <div><span class="text-gray-600">O bronz:</span> <span class="ml-1 font-medium">{{ teamNameById(specialForm.bronze_a_id) }}</span> vs <span class="font-medium">{{ teamNameById(specialForm.bronze_b_id) }}</span></div>
            </div>
          </div>
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="label">Český střelec 1. gólu</label>
              <input v-model="specialForm.czech_shooter_first" type="text" class="input" />
            </div>
            <div>
              <label class="label">Český střelec posledního gólu</label>
              <input v-model="specialForm.czech_shooter_last" type="text" class="input" />
            </div>
          </div>
          <div class="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-4 md:col-span-2">
            <p class="text-sm font-medium text-gray-800">Zápasy → dopočet (neupravuješ ručně)</p>
            <p class="text-xs text-gray-600 mt-1 mb-3">
              Po uložení skóre zápasu nebo tlačítku „Přepočítat body“ se z tabulky týmů a výsledků doplní tyto údaje do výsledků speciálu.
            </p>
            <div class="grid sm:grid-cols-2 gap-3 text-sm">
              <div>
                <span class="text-gray-600">Nejvíce branek v jednom utkání:</span>
                <span class="ml-1 font-semibold tabular-nums">{{ specialForm.max_goals_per_game ?? '—' }}</span>
              </div>
              <div>
                <span class="text-gray-600">Remízy / prodloužení (počet):</span>
                <span class="ml-1 font-semibold tabular-nums">{{ specialForm.overtimes ?? '—' }}</span>
              </div>
              <div>
                <span class="text-gray-600">Tým – nejvíce vstřelených:</span>
                <span class="ml-1 font-medium">{{ teamNameById(specialForm.team_most_goals_id) }}</span>
              </div>
              <div>
                <span class="text-gray-600">Tým – nejméně obdržených:</span>
                <span class="ml-1 font-medium">{{ teamNameById(specialForm.team_least_goals_id) }}</span>
              </div>
            </div>
          </div>
          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-bold mb-2">Skupina A</h4>
              <div class="space-y-2">
                <div v-for="(label, i) in groupLabels" :key="'a-' + i">
                  <label class="label">{{ label }}</label>
                  <select v-model="specialForm[`group_a_${i + 1}_id`]" class="input w-full">
                    <option :value="null">—</option>
                    <option v-for="t in groupATeams" :key="t.id" :value="t.id">{{ t.display_name || t.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="label">Sestup</label>
                  <select v-model="specialForm.team_drop_a_id" class="input w-full">
                    <option :value="null">—</option>
                    <option v-for="t in groupATeams" :key="t.id" :value="t.id">{{ t.display_name || t.name }}</option>
                  </select>
                </div>
              </div>
            </div>
            <div>
              <h4 class="font-bold mb-2">Skupina B</h4>
              <div class="space-y-2">
                <div v-for="(label, i) in groupLabels" :key="'b-' + i">
                  <label class="label">{{ label }}</label>
                  <select v-model="specialForm[`group_b_${i + 1}_id`]" class="input w-full">
                    <option :value="null">—</option>
                    <option v-for="t in groupBTeams" :key="t.id" :value="t.id">{{ t.display_name || t.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="label">Sestup</label>
                  <select v-model="specialForm.team_drop_b_id" class="input w-full">
                    <option :value="null">—</option>
                    <option v-for="t in groupBTeams" :key="t.id" :value="t.id">{{ t.display_name || t.name }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="label">Tým – první branka MS</label>
              <select v-model="specialForm.team_first_goal_id" class="input">
                <option :value="null">—</option>
                <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.display_name || t.name }}</option>
              </select>
            </div>
            <div>
              <label class="label">Tým – poslední branka MS</label>
              <select v-model="specialForm.team_last_goal_id" class="input">
                <option :value="null">—</option>
                <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.display_name || t.name }}</option>
              </select>
            </div>
          </div>
        </div>
        <button type="submit" :disabled="savingSpecial" class="btn btn-primary">
          {{ savingSpecial ? 'Ukládám…' : 'Uložit výsledky speciálních tipů' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'
import TeamWithFlag from '../../components/TeamWithFlag.vue'

const route = useRoute()
const cup = ref(null)
const teams = ref([])
const matches = ref([])
const loading = ref(true)
const savingCup = ref(false)
const savingTeam = ref(false)
const savingMatch = ref(false)
const savingMatchId = ref(null)
const showTeamForm = ref(false)
const showMatchForm = ref(false)
const specialLoading = ref(false)
const savingSpecial = ref(false)
const calculatingPoints = ref(false)

const editForm = reactive({ year: '', location: '', date_start: '', date_end: '' })
const teamForm = reactive({ name: '', group: 'A' })
const matchForm = reactive({ team_a_id: null, team_b_id: null, date: '' })
const matchScores = ref({})
const playoffs = ref([])
const playoffScores = ref({})
const ensuringPlayoffs = ref(false)
const savingPlayoffId = ref(null)
const groupLabels = ['1. místo', '2. místo', '3. místo', '4. místo']

const PLAYOFF_GROUPS = [
  { title: 'Čtvrtfinále (4 zápasy)', types: ['QFA1', 'QFA2', 'QFB1', 'QFB2'] },
  { title: 'Semifinále', types: ['SFA', 'SFB'] },
  { title: 'O bronz', types: ['BMG'] },
  { title: 'Finále', types: ['GMG'] },
]

const playoffDisplayGroups = computed(() => {
  const byType = {}
  for (const p of playoffs.value) {
    byType[p.playoff_type] = p
  }
  return PLAYOFF_GROUPS.map((g) => ({
    title: g.title,
    rows: g.types.map((t) => byType[t]).filter(Boolean),
  })).filter((g) => g.rows.length > 0)
})

const groupATeams = computed(() => teams.value.filter((t) => t.group === 'A'))
const groupBTeams = computed(() => teams.value.filter((t) => t.group === 'B'))

const sortTeamsBy = ref('points')
const teamsSortDir = ref('desc')
const sortedTeams = computed(() => {
  const list = [...teams.value]
  const key = sortTeamsBy.value
  const dir = teamsSortDir.value === 'asc' ? 1 : -1
  list.sort((a, b) => {
    const va = key === 'name' ? (a.name || '') : (Number(a[key]) ?? 0)
    const vb = key === 'name' ? (b.name || '') : (Number(b[key]) ?? 0)
    if (key === 'name' || key === 'group') return dir * (va < vb ? -1 : va > vb ? 1 : 0)
    return dir * (va - vb)
  })
  return list
})
function setTeamsSort(key) {
  if (sortTeamsBy.value === key) teamsSortDir.value = teamsSortDir.value === 'asc' ? 'desc' : 'asc'
  else {
    sortTeamsBy.value = key
    teamsSortDir.value = key === 'points' || key === 'gf' || key === 'gp' || key === 'win' || key === 'los' || key === 'ga' ? 'desc' : 'asc'
  }
}

const specialForm = reactive({
  winner_id: null,
  final_a_id: null,
  final_b_id: null,
  bronze_a_id: null,
  bronze_b_id: null,
  czech_shooter_first: '',
  czech_shooter_last: '',
  max_goals_per_game: null,
  overtimes: null,
  group_a_1_id: null,
  group_a_2_id: null,
  group_a_3_id: null,
  group_a_4_id: null,
  group_b_1_id: null,
  group_b_2_id: null,
  group_b_3_id: null,
  group_b_4_id: null,
  team_drop_a_id: null,
  team_drop_b_id: null,
  team_most_goals_id: null,
  team_least_goals_id: null,
  team_first_goal_id: null,
  team_last_goal_id: null,
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('cs-CZ')
}
function formatDateTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('cs-CZ')
}

function toLocalDatetime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function rebuildPlayoffScores() {
  const next = {}
  for (const p of playoffs.value) {
    next[p.id] = {
      team_a_id: p.team_a?.id ?? null,
      team_b_id: p.team_b?.id ?? null,
      score_a: p.score_a != null && p.score_a !== '' ? Number(p.score_a) : '',
      score_b: p.score_b != null && p.score_b !== '' ? Number(p.score_b) : '',
      score_a_final:
        p.score_a_final != null && p.score_a_final !== ''
          ? Number(p.score_a_final)
          : p.score_a != null && p.score_a !== ''
            ? Number(p.score_a)
            : '',
      score_b_final:
        p.score_b_final != null && p.score_b_final !== ''
          ? Number(p.score_b_final)
          : p.score_b != null && p.score_b !== ''
            ? Number(p.score_b)
            : '',
      date: toLocalDatetime(p.date),
      shootout: !!p.shootout,
    }
  }
  playoffScores.value = next
}

async function ensurePlayoffs() {
  if (!cup.value?.id) return
  ensuringPlayoffs.value = true
  try {
    const res = await api.post('/playoffs/ensure/', { cup_id: cup.value.id })
    playoffs.value = res.data.playoffs ?? []
    rebuildPlayoffScores()
    await loadSpecial()
  } catch (e) {
    console.error(e)
  } finally {
    ensuringPlayoffs.value = false
  }
}

async function savePlayoffResult(p) {
  savingPlayoffId.value = p.id
  try {
    const s = playoffScores.value[p.id]
    const scoreA = s.score_a === '' || s.score_a === undefined ? null : Number(s.score_a)
    const scoreB = s.score_b === '' || s.score_b === undefined ? null : Number(s.score_b)
    let scoreAFinal = s.score_a_final === '' || s.score_a_final === undefined ? null : Number(s.score_a_final)
    let scoreBFinal = s.score_b_final === '' || s.score_b_final === undefined ? null : Number(s.score_b_final)
    if (scoreAFinal == null && scoreA != null) scoreAFinal = scoreA
    if (scoreBFinal == null && scoreB != null) scoreBFinal = scoreB
    const payload = {
      team_a_id: s.team_a_id ?? null,
      team_b_id: s.team_b_id ?? null,
      score_a: scoreA,
      score_b: scoreB,
      score_a_final: scoreAFinal,
      score_b_final: scoreBFinal,
      shootout: !!s.shootout,
    }
    if (s.date) payload.date = new Date(s.date).toISOString()
    const res = await api.patch(`/playoffs/${p.id}/`, payload)
    const idx = playoffs.value.findIndex((x) => x.id === p.id)
    if (idx !== -1) playoffs.value[idx] = res.data
    const pr = res.data
    playoffScores.value[p.id] = {
      team_a_id: pr.team_a?.id ?? null,
      team_b_id: pr.team_b?.id ?? null,
      score_a: pr.score_a != null ? Number(pr.score_a) : '',
      score_b: pr.score_b != null ? Number(pr.score_b) : '',
      score_a_final:
        pr.score_a_final != null
          ? Number(pr.score_a_final)
          : pr.score_a != null
            ? Number(pr.score_a)
            : '',
      score_b_final:
        pr.score_b_final != null
          ? Number(pr.score_b_final)
          : pr.score_b != null
            ? Number(pr.score_b)
            : '',
      date: toLocalDatetime(pr.date),
    }
    const teamsRes = await api.get(`/teams/?cup=${cup.value.id}`)
    teams.value = teamsRes.data.results ?? teamsRes.data
    await loadSpecial()
  } catch (e) {
    console.error(e)
  } finally {
    savingPlayoffId.value = null
  }
}

async function load() {
  const id = route.params.id
  try {
    const [cupRes, teamsRes, matchesRes, playoffsRes] = await Promise.all([
      api.get(`/cups/${id}/`),
      api.get(`/teams/?cup=${id}`),
      api.get(`/matches/?cup=${id}`),
      api.get(`/playoffs/?cup=${id}`),
    ])
    cup.value = cupRes.data
    teams.value = Array.isArray(teamsRes.data) ? teamsRes.data : (teamsRes.data?.results ?? [])
    const matchList = Array.isArray(matchesRes.data) ? matchesRes.data : (matchesRes.data?.results ?? [])
    matches.value = matchList
    const plist = Array.isArray(playoffsRes.data) ? playoffsRes.data : (playoffsRes.data?.results ?? [])
    playoffs.value = plist
    rebuildPlayoffScores()
    editForm.year = cup.value.year
    editForm.location = cup.value.location || ''
    editForm.date_start = cup.value.date_start ? cup.value.date_start.slice(0, 10) : ''
    editForm.date_end = cup.value.date_end ? cup.value.date_end.slice(0, 10) : ''
    const byId = {}
    const toScore = (v) => (v != null && v !== '') ? Number(v) : ''
    for (const m of matches.value) {
      byId[m.id] = {
        score_a: toScore(m.score_a),
        score_b: toScore(m.score_b),
        score_a_final: toScore(m.score_a_final != null ? m.score_a_final : m.score_a),
        score_b_final: toScore(m.score_b_final != null ? m.score_b_final : m.score_b),
      shootout: !!m.shootout,
      }
    }
    matchScores.value = byId
    await loadSpecial()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => route.params.id, load)

async function saveCup() {
  savingCup.value = true
  try {
    await api.patch(`/cups/${cup.value.id}/`, {
      year: editForm.year,
      location: editForm.location,
      date_start: editForm.date_start || null,
      date_end: editForm.date_end || null,
    })
    cup.value = { ...cup.value, ...editForm }
  } catch (e) {
    console.error(e)
  } finally {
    savingCup.value = false
  }
}

async function addTeam() {
  savingTeam.value = true
  try {
    const res = await api.post('/teams/', {
      name: teamForm.name,
      cup_id: cup.value.id,
      group: teamForm.group,
    })
    teams.value.push(res.data)
    teamForm.name = ''
    showTeamForm.value = false
  } catch (e) {
    console.error(e)
  } finally {
    savingTeam.value = false
  }
}

async function deleteTeam(teamId) {
  if (!confirm('Opravdu smazat tento tým?')) return
  try {
    await api.delete(`/teams/${teamId}/`)
    teams.value = teams.value.filter((t) => t.id !== teamId)
  } catch (e) {
    console.error(e)
  }
}

function toISO(d) {
  if (!d) return ''
  const d2 = new Date(d)
  return d2.toISOString().slice(0, 16)
}

async function addMatch() {
  if (!matchForm.team_a_id || !matchForm.team_b_id || !matchForm.date) return
  savingMatch.value = true
  try {
    const res = await api.post('/matches/', {
      cup_id: cup.value.id,
      team_a_id: matchForm.team_a_id,
      team_b_id: matchForm.team_b_id,
      date: new Date(matchForm.date).toISOString(),
    })
    matches.value.push(res.data)
    matchScores.value = {
      ...matchScores.value,
      [res.data.id]: { score_a: '', score_b: '', score_a_final: '', score_b_final: '', shootout: false },
    }
    matchForm.team_a_id = null
    matchForm.team_b_id = null
    matchForm.date = ''
    showMatchForm.value = false
  } catch (e) {
    console.error(e)
  } finally {
    savingMatch.value = false
  }
}

async function deleteMatch(matchId) {
  if (!confirm('Opravdu smazat tento zápas?')) return
  try {
    await api.delete(`/matches/${matchId}/`)
    matches.value = matches.value.filter((m) => m.id !== matchId)
    const next = { ...matchScores.value }
    delete next[matchId]
    matchScores.value = next
  } catch (e) {
    console.error(e)
  }
}

async function saveMatchResult(m) {
  savingMatchId.value = m.id
  try {
    const s = matchScores.value[m.id]
    const scoreA = s.score_a === '' || s.score_a === undefined ? null : Number(s.score_a)
    const scoreB = s.score_b === '' || s.score_b === undefined ? null : Number(s.score_b)
    let scoreAFinal = s.score_a_final === '' || s.score_a_final === undefined ? null : Number(s.score_a_final)
    let scoreBFinal = s.score_b_final === '' || s.score_b_final === undefined ? null : Number(s.score_b_final)
    if (scoreAFinal == null && scoreA != null) scoreAFinal = scoreA
    if (scoreBFinal == null && scoreB != null) scoreBFinal = scoreB
    const payload = {
      score_a: scoreA,
      score_b: scoreB,
      score_a_final: scoreAFinal,
      score_b_final: scoreBFinal,
      shootout: !!s.shootout,
    }
    const res = await api.patch(`/matches/${m.id}/`, payload)
    const idx = matches.value.findIndex((x) => x.id === m.id)
    if (idx !== -1) matches.value[idx] = res.data
    // Backend recalculates points automatically; refresh teams table
    const teamsRes = await api.get(`/teams/?cup=${cup.value.id}`)
    teams.value = teamsRes.data.results ?? teamsRes.data
    await loadSpecial()
  } catch (e) {
    console.error(e)
  } finally {
    savingMatchId.value = null
  }
}

function teamIdFromApi(value) {
  if (value == null) return null
  return typeof value === 'object' && value !== null && 'id' in value ? value.id : value
}

function teamNameById(id) {
  if (id == null) return '—'
  const t = teams.value.find((x) => x.id === id)
  return t?.display_name || t?.name || '—'
}

async function loadSpecial() {
  if (!cup.value?.id) return
  specialLoading.value = true
  try {
    const res = await api.get(`/special/by_cup/?cup=${cup.value.id}`)
    const d = res.data
    specialForm.winner_id = teamIdFromApi(d.winner)
    specialForm.final_a_id = teamIdFromApi(d.final_a)
    specialForm.final_b_id = teamIdFromApi(d.final_b)
    specialForm.bronze_a_id = teamIdFromApi(d.bronze_a)
    specialForm.bronze_b_id = teamIdFromApi(d.bronze_b)
    specialForm.czech_shooter_first = d.czech_shooter_first ?? ''
    specialForm.czech_shooter_last = d.czech_shooter_last ?? ''
    specialForm.max_goals_per_game = d.max_goals_per_game ?? null
    specialForm.overtimes = d.overtimes ?? null
    specialForm.group_a_1_id = teamIdFromApi(d.group_a_1)
    specialForm.group_a_2_id = teamIdFromApi(d.group_a_2)
    specialForm.group_a_3_id = teamIdFromApi(d.group_a_3)
    specialForm.group_a_4_id = teamIdFromApi(d.group_a_4)
    specialForm.group_b_1_id = teamIdFromApi(d.group_b_1)
    specialForm.group_b_2_id = teamIdFromApi(d.group_b_2)
    specialForm.group_b_3_id = teamIdFromApi(d.group_b_3)
    specialForm.group_b_4_id = teamIdFromApi(d.group_b_4)
    specialForm.team_drop_a_id = teamIdFromApi(d.team_drop_a)
    specialForm.team_drop_b_id = teamIdFromApi(d.team_drop_b)
    specialForm.team_most_goals_id = teamIdFromApi(d.team_most_goals)
    specialForm.team_least_goals_id = teamIdFromApi(d.team_least_goals)
    specialForm.team_first_goal_id = teamIdFromApi(d.team_first_goal)
    specialForm.team_last_goal_id = teamIdFromApi(d.team_last_goal)
  } catch (e) {
    if (e.response?.status !== 404) console.error(e)
    // 404 = no results yet, keep form empty
  } finally {
    specialLoading.value = false
  }
}

function specialPayload() {
  const f = specialForm
  return {
    cup_id: cup.value.id,
    czech_shooter_first: f.czech_shooter_first || '',
    czech_shooter_last: f.czech_shooter_last || '',
    group_a_1: f.group_a_1_id || null,
    group_a_2: f.group_a_2_id || null,
    group_a_3: f.group_a_3_id || null,
    group_a_4: f.group_a_4_id || null,
    group_b_1: f.group_b_1_id || null,
    group_b_2: f.group_b_2_id || null,
    group_b_3: f.group_b_3_id || null,
    group_b_4: f.group_b_4_id || null,
    team_drop_a: f.team_drop_a_id || null,
    team_drop_b: f.team_drop_b_id || null,
    team_first_goal: f.team_first_goal_id || null,
    team_last_goal: f.team_last_goal_id || null,
  }
}

async function saveSpecialResults() {
  savingSpecial.value = true
  try {
    await api.put(`/special/by_cup/?cup=${cup.value.id}`, specialPayload())
    await loadSpecial()
  } catch (e) {
    console.error(e)
  } finally {
    savingSpecial.value = false
  }
}

async function recalculatePoints() {
  if (!cup.value?.id) return
  calculatingPoints.value = true
  try {
    await api.post('/admin/calculate_points/', { cup_id: cup.value.id })
    await load()
  } catch (e) {
    console.error(e)
  } finally {
    calculatingPoints.value = false
  }
}
</script>

<style scoped>
.input-score::-webkit-inner-spin-button,
.input-score::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.input-score {
  -moz-appearance: textfield;
}
</style>
