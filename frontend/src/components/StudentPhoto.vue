<template>
  <div
    class="flex shrink-0 items-center justify-center overflow-hidden bg-surface-gray-3"
    :class="sizeClass"
  >
    <img
      v-if="src && !failed"
      :src="src"
      :alt="name"
      class="h-full w-full object-cover"
      loading="lazy"
      @error="failed = true"
    />
    <span v-else class="font-semibold text-ink-gray-6" :class="textClass">
      {{ initials }}
    </span>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  name: { type: String, default: '' },
  size: { type: String, default: 'md' }, // md | lg
})

const failed = ref(false)
watch(() => props.src, () => (failed.value = false))

const initials = computed(() =>
  (props.name || '?')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join(''),
)
const sizeClass = computed(() =>
  props.size === 'lg' ? 'size-32 rounded-xl' : 'size-20 rounded-lg',
)
const textClass = computed(() => (props.size === 'lg' ? 'text-3xl' : 'text-xl'))
</script>
