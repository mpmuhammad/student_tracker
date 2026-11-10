
<script setup>
import { ref, watch } from 'vue'
import { call } from 'frappe-ui'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  student: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['update:open'])

const goals = ref([])
const loading = ref(false)
const error = ref('')

function closeDialog() {
  emit('update:open', false)
}

function isCompleted(goal) {
  return (
    !!goal.is_closed ||
    Number(goal.actual_percentage) >= 100 ||
    goal.status === 'Complete'
  )
}

async function loadHistory() {
  if (!props.student) return

  loading.value = true
  error.value = ''

  try {
    const result = await call('student_tracker.api.get_goal_history', {
      student: props.student,
    })

    goals.value = result || []
  } catch (err) {
    console.error('Failed to load goal history:', err)
    error.value = 'Unable to load goal history. Please try again.'
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.open, props.student],
  ([isOpen]) => {
    if (isOpen) {
      loadHistory()
    }
  },
  { immediate: true },
)
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[100] flex items-center justify-center p-4"
      style="background-color: rgba(0, 0, 0, 0.55);"
      @click.self="closeDialog"
    >
      <!-- Main modal -->
      <div
        class="flex max-h-[85vh] w-full max-w-2xl flex-col overflow-hidden rounded-xl shadow-xl"
        style="
          background-color: #ffffff;
          opacity: 1;
          isolation: isolate;
        "
      >
        <!-- Header -->
        <div
          class="flex shrink-0 items-center justify-between border-b px-5 py-4"
          style="background-color: #ffffff;"
        >
          <div>
            <h2 class="text-lg font-semibold text-gray-900">
              Goal History
            </h2>

            <p class="mt-1 text-sm text-gray-500">
              Previous and current goals for this student
            </p>
          </div>

          <button
            type="button"
            class="rounded-md p-2 text-gray-500 hover:bg-gray-100"
            @click="closeDialog"
          >
            <span class="text-xl">&times;</span>
          </button>
        </div>

        <!-- Content -->
        <div
          class="min-h-0 flex-1 overflow-y-auto p-5"
          style="background-color: #ffffff;"
        >
          <!-- Loading -->
          <div
            v-if="loading"
            class="py-10 text-center text-sm text-gray-500"
          >
            Loading goal history...
          </div>

          <!-- Error -->
          <div
            v-else-if="error"
            class="py-8 text-center text-sm text-red-600"
          >
            {{ error }}

            <button
              type="button"
              class="ml-2 font-medium underline"
              @click="loadHistory"
            >
              Retry
            </button>
          </div>

          <!-- Empty state -->
          <div
            v-else-if="!goals.length"
            class="py-10 text-center text-sm text-gray-500"
          >
            No goal history found for this student.
          </div>

          <!-- Goal history list -->
          <div v-else class="space-y-4">
            <div
              v-for="(goal, index) in goals"
              :key="goal.name"
              class="rounded-lg border border-gray-300 p-4 shadow-sm transition-colors hover:border-gray-400"
              style="background-color: #ffffff;"
            >
              <!-- Goal heading and badges -->
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span class="text-xs font-semibold uppercase text-gray-500">
                  Goal {{ goals.length - index }}
                </span>

                <div class="flex items-center gap-2">
                  <!-- Goal term badge -->
                  <span
                    v-if="goal.goal_term"
                    class="rounded-full px-2.5 py-1 text-xs font-medium"
                    :class="
                      goal.goal_term === 'Long Term'
                        ? 'bg-violet-100 text-violet-700'
                        : 'bg-amber-100 text-amber-700'
                    "
                  >
                    {{ goal.goal_term }} Goal
                  </span>

                  <!-- Status badge -->
                  <span
                    class="rounded-full px-2.5 py-1 text-xs font-medium"
                    :class="
                      isCompleted(goal)
                        ? 'bg-green-100 text-green-700'
                        : 'bg-blue-100 text-blue-700'
                    "
                  >
                    {{
                      isCompleted(goal)
                        ? 'Complete'
                        : goal.status || 'Started'
                    }}
                  </span>
                </div>
              </div>

              <!-- Goal description -->
              <div class="mt-4 rounded-md border border-gray-200 p-4">
                <div
                  class="mb-2 flex items-center gap-2 text-xs font-semibold uppercase text-gray-500"
                >
                  <span>▤</span>
                  Goal Description
                </div>

                <p class="text-sm text-gray-800">
                  {{ goal.task_description || 'No description provided.' }}
                </p>
              </div>

              <!-- Goal dates -->
              <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div class="rounded-md border border-gray-200 p-3">
                  <p class="text-xs text-gray-500">
                    Started on
                  </p>

                  <p class="mt-1 text-sm font-medium text-gray-800">
                    {{ goal.created_on || 'Not available' }}
                  </p>
                </div>

                <div class="rounded-md border border-gray-200 p-3">
                  <p class="text-xs text-gray-500">
                    End date
                  </p>

                  <template v-if="isCompleted(goal)">
                    <p class="mt-1 text-sm font-semibold text-green-600">
                      Goal completed
                    </p>

                    <p
                      v-if="goal.closed_on"
                      class="text-xs text-gray-500"
                    >
                      {{ goal.closed_on }}
                    </p>
                  </template>

                  <template v-else>
                    <p class="mt-1 text-sm font-semibold text-green-600">
                      ACTIVE GOAL
                    </p>

                    <p class="text-xs text-gray-500">
                      Currently in progress
                    </p>
                  </template>
                </div>
              </div>

              <!-- Progress: active goals only -->
              <div
                v-if="!isCompleted(goal)"
                class="mt-4 rounded-md border border-gray-200 p-4"
              >
                <div class="mb-3 flex items-center justify-between">
                  <div>
                    <p class="text-sm font-semibold text-gray-800">
                      Overall progress
                    </p>

                    <p class="text-xs text-gray-500">
                      Current recorded progress
                    </p>
                  </div>

                  <span class="text-lg font-semibold text-gray-900">
                    {{ Number(goal.actual_percentage || 0) }}%
                  </span>
                </div>

                <div class="h-2.5 overflow-hidden rounded-full bg-gray-100">
                  <div
                    class="h-full rounded-full bg-blue-500 transition-all"
                    :style="{
                      width: `${Math.min(
                        100,
                        Math.max(0, Number(goal.actual_percentage || 0)),
                      )}%`,
                    }"
                  ></div>
                </div>

                <div class="mt-2 flex justify-between text-xs text-gray-400">
                  <span>0%</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div
          class="flex shrink-0 justify-end border-t px-5 py-3"
          style="background-color: #ffffff;"
        >
          <button
            type="button"
            class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            @click="closeDialog"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
