
<template>
  <header class="sticky top-0 z-10 border-b border-outline-gray-2 bg-surface-base">
    <div class="mx-auto flex min-h-16 max-w-6xl items-center justify-between px-4">
      <!-- Edu Cell branding -->
      <router-link to="/" class="flex items-center gap-2">
        <div class="relative h-12 w-[63px] shrink-0 overflow-hidden">
          <img
            src="/educell-logo.png"
            alt="Edu Cell"
            class="absolute left-0 top-0 h-12 w-[288px] max-w-none"
          />
        </div>
      </router-link>

      <!-- User information and actions -->
      <div class="flex items-center gap-3">
        <div class="hidden text-right sm:block">
          <div class="text-sm font-medium">{{ session.fullName }}</div>
          <div class="text-xs text-ink-gray-5">{{ session.user }}</div>
        </div>

        <Avatar
          :image="session.userImage"
          :label="session.fullName"
          size="md"
        />

        <Button
          variant="ghost"
          icon="lucide-log-out"
          tooltip="Log out"
          :loading="loggingOut"
          @click="onLogout"
        />
      </div>

    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { Avatar, Badge, Button } from 'frappe-ui'
import { session, logout } from '../session'

const loggingOut = ref(false)

async function onLogout() {
  loggingOut.value = true
  try {
    await logout()
  } finally {
    loggingOut.value = false
  }
}
</script>
