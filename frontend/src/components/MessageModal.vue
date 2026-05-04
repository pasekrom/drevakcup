<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="modelValue"
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
          aria-labelledby="message-modal-title"
          class="relative w-full max-w-md overflow-hidden rounded-xl bg-white shadow-xl ring-1 ring-gray-200/80"
          @click.stop
        >
          <div class="flex gap-4 p-6">
            <div
              class="flex-shrink-0"
              :class="variant === 'success' ? 'text-emerald-500' : 'text-red-500'"
            >
              <CheckCircleIcon v-if="variant === 'success'" class="h-10 w-10" />
              <XCircleIcon v-else class="h-10 w-10" />
            </div>
            <div class="min-w-0 flex-1 pt-0.5">
              <h3 id="message-modal-title" class="text-lg font-semibold text-gray-900">
                {{ title }}
              </h3>
              <p class="mt-2 text-sm leading-relaxed text-gray-600 whitespace-pre-wrap">
                {{ message }}
              </p>
              <div class="mt-6 flex flex-wrap justify-end gap-2">
                <button type="button" class="btn btn-primary min-w-[5rem]" @click="close">
                  OK
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { CheckCircleIcon, XCircleIcon } from '@heroicons/vue/24/solid'

defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  message: { type: String, default: '' },
  variant: { type: String, default: 'success' },
})

const emit = defineEmits(['update:modelValue'])

function close() {
  emit('update:modelValue', false)
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
