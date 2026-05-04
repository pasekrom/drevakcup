<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="modelValue && match"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6"
      >
        <div
          class="absolute inset-0 bg-gray-900/45 backdrop-blur-[1px]"
          aria-hidden="true"
          @click="close"
        />
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="match-tip-modal-title"
          class="relative w-full max-w-md overflow-hidden rounded-xl bg-white shadow-xl ring-1 ring-gray-200/80"
          @click.stop
        >
          <div class="p-6">
            <h3 id="match-tip-modal-title" class="text-lg font-semibold text-gray-900">
              Upravit tip
            </h3>
            <p class="mt-1 text-sm text-gray-600">
              {{ formatDateTime(match.date) }}
            </p>
            <p class="mt-3 font-medium text-gray-900">
              <TeamWithFlag :team="match.team_a" />
              <span class="mx-1 text-gray-400">vs</span>
              <TeamWithFlag :team="match.team_b" />
            </p>

            <div v-if="match.has_started" class="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              Zápas již začal — tip nelze upravit.
            </div>

            <div v-else class="mt-5 space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label"><TeamWithFlag :team="match.team_a" /></label>
                  <input
                    v-model.number="scoreA"
                    type="number"
                    min="0"
                    class="input"
                    autocomplete="off"
                  />
                </div>
                <div>
                  <label class="label"><TeamWithFlag :team="match.team_b" /></label>
                  <input
                    v-model.number="scoreB"
                    type="number"
                    min="0"
                    class="input"
                    autocomplete="off"
                  />
                </div>
              </div>
            </div>

            <div class="mt-6 flex flex-wrap justify-end gap-2">
              <button type="button" class="btn btn-secondary" @click="close">
                {{ match.has_started ? 'Zavřít' : 'Zrušit' }}
              </button>
              <button
                v-if="!match.has_started"
                type="button"
                class="btn btn-primary"
                :disabled="saving || !canSave"
                @click="submit"
              >
                <span v-if="saving">Ukládání…</span>
                <span v-else>Uložit</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import api from '../services/api'
import TeamWithFlag from './TeamWithFlag.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  match: { type: Object, default: null },
  initialTip: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'saved', 'save-error'])

const scoreA = ref(null)
const scoreB = ref(null)
const saving = ref(false)

const canSave = computed(() => {
  const a = scoreA.value
  const b = scoreB.value
  return (
    a != null &&
    b != null &&
    !Number.isNaN(Number(a)) &&
    !Number.isNaN(Number(b)) &&
    Number(a) >= 0 &&
    Number(b) >= 0
  )
})

watch(
  () => [props.modelValue, props.match?.id],
  () => {
    if (!props.modelValue || !props.match) return
    const t = props.initialTip
    scoreA.value = t?.score_a ?? null
    scoreB.value = t?.score_b ?? null
    saving.value = false
  }
)

function close() {
  emit('update:modelValue', false)
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString('cs-CZ')
}

async function submit() {
  if (!props.match || !canSave.value) return
  saving.value = true
  try {
    await api.post('/match-tips/bulk_update/', {
      tips: [
        {
          match_id: props.match.id,
          score_a: Number(scoreA.value),
          score_b: Number(scoreB.value),
        },
      ],
    })
    emit('saved', {
      matchId: props.match.id,
      score_a: Number(scoreA.value),
      score_b: Number(scoreB.value),
    })
    close()
  } catch (error) {
    console.error('Save tip:', error)
    const d = error.response?.data?.detail
    const msg =
      typeof d === 'string'
        ? d
        : Array.isArray(d)
          ? d.join(', ')
          : 'Tip se nepodařilo uložit.'
    emit('save-error', msg)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.18s ease;
}
.modal-fade-enter-active .relative,
.modal-fade-leave-active .relative {
  transition: transform 0.18s ease, opacity 0.18s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from .relative,
.modal-fade-leave-to .relative {
  transform: scale(0.97);
  opacity: 0;
}
</style>
