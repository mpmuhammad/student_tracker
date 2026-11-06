<template>
  <div class="flex min-h-screen items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <div class="mb-6 flex flex-col items-center gap-2 text-center">
        <span class="lucide-graduation-cap size-10 text-ink-gray-7" />
        <h1 class="text-2xl font-semibold">Mentor login</h1>
        <p class="text-sm text-ink-gray-5">
          Sign in to see your students and record their activities.
        </p>
      </div>

      <div
        v-if="session.isLoggedIn && !session.isMentor"
        class="mb-4 rounded-lg bg-surface-amber-2 p-3 text-sm text-ink-amber-8"
      >
        You are signed in as <b>{{ session.user }}</b>, but this account does not
        have the <b>Mentor</b> role. Sign in with a mentor account.
      </div>

      <form
        class="flex flex-col gap-4 rounded-xl border border-outline-gray-2 bg-surface-base p-6 shadow-sm"
        @submit.prevent="submit"
      >
        <TextInput
          v-model="email"
          label="Email"
          type="email"
          placeholder="mentor@example.com"
          autocomplete="username"
          required
        />
        <Password
          v-model="password"
          label="Password"
          placeholder="••••••••"
          autocomplete="current-password"
          required
        />
        <ErrorMessage :message="error" />
        <Button type="submit" variant="solid" size="md" :loading="loading" label="Log in" />
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, ErrorMessage, Password, TextInput } from 'frappe-ui'
import { session, login } from '../session'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
  } catch (e) {
    error.value = e?.messages?.join('\n') || e?.message || 'Invalid email or password'
    loading.value = false
  }
}
</script>
