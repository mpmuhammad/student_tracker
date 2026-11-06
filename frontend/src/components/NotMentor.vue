<template>
  <div class="mx-auto max-w-md px-4 py-20 text-center">
    <span class="lucide-shield-alert mx-auto block size-10 text-ink-amber-6" />
    <h2 class="mt-4 text-xl font-semibold">Mentor access only</h2>
    <p class="mt-2 text-sm text-ink-gray-6">
      Your account ({{ session.user }}) does not have the Mentor role. Ask an
      administrator to assign it, or log in with a mentor account.
    </p>
    <Button class="mt-6" label="Switch account" @click="logout" />
  </div>
</template>

<script setup>
import { Button } from 'frappe-ui'
import { session, logout } from '../session'
</script>
