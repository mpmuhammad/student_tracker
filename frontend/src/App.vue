<template>
  <FrappeUIProvider>
    <div class="min-h-screen bg-surface-gray-1 text-ink-gray-9">
      <AppHeader v-if="showHeader" />
      <router-view />
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { FrappeUIProvider } from 'frappe-ui'
import AppHeader from './components/AppHeader.vue'
import { session } from './session'

const route = useRoute()
const showHeader = computed(() => !route.meta.public && session.isLoggedIn)
</script>
