
<template>
  <NotMentor v-if="!session.isMentor" />

  <main v-else class="mx-auto max-w-6xl px-4 py-6">
    <Button
      variant="ghost"
      icon-left="lucide-arrow-left"
      label="All students"
      :route="{ name: 'Students' }"
    />

    <div
      v-if="student.error"
      class="mt-4 rounded-lg bg-surface-red-2 p-4 text-sm text-ink-red-8"
    >
      {{ student.error.messages?.join(', ') || student.error.message }}
    </div>

    <!-- Full-width vertical layout -->
    <div v-else class="mt-4 flex flex-col gap-6">

      <!-- Student Profile -->
      <aside class="w-full rounded-xl border border-outline-gray-2 bg-surface-base p-5">
        <div
          v-if="!s"
          class="h-48 animate-pulse rounded-lg bg-surface-gray-3"
        />

        <template v-else>
          <div class="flex flex-col items-center gap-6 sm:flex-row sm:items-start">

            <!-- Student image -->
            <div class="flex shrink-0 justify-center sm:w-48">
              <div class="scale-110">
                <StudentPhoto :src="s.photo" :name="s.name1" size="lg" />
              </div>
            </div>

            <!-- Student details -->
            <div class="min-w-0 flex-1">
              <div class="border-b border-outline-gray-1 pb-4">
                <h1 class="text-xl font-semibold">
                  {{ s.name1 || s.name }}
                </h1>

                <p class="mt-1 text-xs text-ink-gray-5">
                  {{ s.name }}
                </p>
              </div>

              <dl class="mt-4 grid grid-cols-1 gap-x-8 gap-y-4 text-sm sm:grid-cols-2 lg:grid-cols-3">
                <Field label="House name" :value="s.house_name" />
                <Field label="Phone" :value="s.phone_number" />
                <Field label="Parent" :value="s.parent_name" />
                <Field label="Parent contact" :value="s.parent_contact_number" />
                <Field label="School" :value="join(s.school_name, s.school_class)" />
                <Field label="Madrassa" :value="join(s.madrassa_name, s.madrassa_class)" />
              </dl>
            </div>
          </div>
        </template>
      </aside>

      <!-- Student Goal -->
      <div class="w-full rounded-xl border border-outline-gray-2 bg-surface-base p-5">
        <div class="mb-4 flex items-center justify-between gap-2">
          <h2 class="text-base font-semibold">Student Goal</h2>

          <Badge
            v-if="goal.data"
            :label="goal.data.status"
            :theme="goal.data.status === 'Complete' ? 'green' : 'gray'"
          />
        </div>

        <!-- Loading -->
        <div
          v-if="goal.loading"
          class="py-4 text-sm text-ink-gray-5"
        >
          Loading goal...
        </div>

        <!-- Existing Goal -->
        <div v-else-if="goal.data" class="space-y-4">

          <!-- Goal information -->
          <div class="space-y-4">
            <div>
              <p class="text-xs font-medium text-ink-gray-5">
                Task
              </p>

              <p class="mt-1 text-sm font-medium leading-relaxed text-ink-gray-9">
                {{ goal.data.task_description }}
              </p>
            </div>

            <!-- Goal dates -->
            <div class="grid grid-cols-1 gap-3 border-t border-outline-gray-1 pt-3 sm:grid-cols-2">
              <div>
                <p class="text-xs text-ink-gray-5">
                  Goal started on
                </p>

                <p class="mt-1 text-sm text-ink-gray-8">
                  {{
                    goal.data.created_on
                      ? dayjs(goal.data.created_on).format('DD MMM YYYY, hh:mm A')
                      : '—'
                  }}
                </p>
              </div>

              <div>
                <p class="text-xs text-ink-gray-5">
                  Goal ended on
                </p>

                <p class="mt-1 text-sm text-ink-gray-8">
                  {{
                    goal.data.closed_on
                      ? dayjs(goal.data.closed_on).format('DD MMM YYYY, hh:mm A')
                      : 'Not ended'
                  }}
                </p>
              </div>
            </div>
          </div>

          <!-- Progress -->
          <div class="border-t border-outline-gray-1 pt-4">
            <div class="mb-3 flex items-center justify-between">
              <p class="text-sm font-medium text-ink-gray-7">
                Progress
              </p>

              <span class="text-sm font-semibold text-ink-gray-8">
                {{ goal.data.actual_percentage || 0 }}%
              </span>
            </div>

            <!-- Frappe UI Slider -->
            <Slider
              :model-value="[Number(goal.data.actual_percentage || 0)]"
              :min="0"
              :max="100"
              :step="1"
              size="md"
              :disabled="
                updatingProgress ||
                closingGoal ||
                Number(goal.data.actual_percentage) >= 100
              "
              @value-commit="updateProgress"
            />

            <!-- Coloured progress bar -->
            <div class="mt-5 h-2 overflow-hidden rounded-full bg-surface-gray-3">
              <div
                class="h-full rounded-full transition-all duration-300"
                :class="
                  Number(goal.data.actual_percentage) >= 100
                    ? 'bg-green-500'
                    : 'bg-blue-500'
                "
                :style="{
                  width: `${Number(goal.data.actual_percentage || 0)}%`,
                }"
              />
            </div>

            <!-- Percentage below progress bar -->
            <div class="mt-3 flex justify-end">
              <span class="text-xs font-medium text-ink-gray-8">
                {{ goal.data.actual_percentage || 0 }}%
              </span>
            </div>

            <p
              v-if="updatingProgress"
              class="mt-2 text-xs text-ink-gray-5"
            >
              Updating progress...
            </p>

            <p
              v-else-if="Number(goal.data.actual_percentage) >= 100"
              class="mt-2 text-xs font-medium text-ink-green-7"
            >
              Goal completed! You can now mark it as complete.
            </p>
          </div>

          <!-- Mark as Complete -->
          <Button
            v-if="Number(goal.data.actual_percentage) >= 100"
            block
            variant="solid"
            icon-left="lucide-check-circle"
            label="Mark as complete"
            :loading="closingGoal"
            :disabled="closingGoal || updatingProgress"
            @click="closeGoal"
          />
        </div>

        <!-- No Active Goal -->
        <div v-else class="py-3 text-center">
          <p class="text-sm text-ink-gray-5">
            No goal set for this student.
          </p>

          <Button
            class="mt-3"
            variant="subtle"
            icon-left="lucide-plus"
            label="Set New Goal"
            :disabled="!s"
            @click="showGoalDialog = true"
          />
        </div>
      </div>

      <!-- Activity Notes -->
      <section class="w-full">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold">
              Activity notes
            </h2>

            <p class="text-sm text-ink-gray-5">
              {{ activities.data?.length ?? 0 }}
              record{{ activities.data?.length === 1 ? '' : 's' }}
            </p>
          </div>

          <Button
            variant="solid"
            icon-left="lucide-plus"
            label="Add activity"
            :disabled="!s"
            @click="showAdd = true"
          />
        </div>

        <!-- Loading -->
        <div
          v-if="activities.loading && !activities.data"
          class="mt-4 space-y-3"
        >
          <div
            v-for="i in 3"
            :key="i"
            class="h-24 animate-pulse rounded-xl bg-surface-gray-3"
          />
        </div>

        <!-- Empty Activity History -->
        <div
          v-else-if="!activities.data?.length"
          class="mt-4 rounded-xl border border-dashed border-outline-gray-3 p-10 text-center"
        >
          <span class="lucide-notebook-pen mx-auto block size-8 text-ink-gray-4" />

          <p class="mt-3 font-medium">
            No activities recorded yet
          </p>

          <p class="mt-1 text-sm text-ink-gray-5">
            Add the first activity note for this student.
          </p>
        </div>

        <!-- Activity Timeline -->
        <ol
          v-else
          class="relative mt-4 space-y-4 border-l border-outline-gray-2 pl-6"
        >
          <li
            v-for="a in activities.data"
            :key="a.name"
            class="relative"
          >
            <span
              class="absolute -left-[31px] top-4 size-3 rounded-full border-2 border-surface-base bg-surface-gray-7"
            />

            <div class="rounded-xl border border-outline-gray-2 bg-surface-base p-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="font-medium">
                  {{ formatDate(a.activity_date) }}
                </div>

                <div class="text-xs text-ink-gray-5">
                  by {{ a.owner }} · {{ fromNow(a.creation) }}
                </div>
              </div>

              <div
                class="activity-note mt-2 text-sm text-ink-gray-8"
                v-html="a.activity_note || '<p>—</p>'"
              />
            </div>
          </li>
        </ol>
      </section>
    </div>

    <!-- Activity Dialog -->
    <AddActivityDialog
      v-model:open="showAdd"
      :student="s"
      @saved="activities.reload()"
    />

    <!-- Goal Dialog -->
    <AddGoalDialog
      v-model:open="showGoalDialog"
      :student="s"
      @saved="refreshAfterGoalSaved"
    />
  </main>
</template>

<script setup>
import { computed, h, ref } from 'vue'

import {
  Badge,
  Button,
  createResource,
  dayjs,
  call,
  toast,
  Slider,
} from 'frappe-ui'

import StudentPhoto from '../components/StudentPhoto.vue'
import AddActivityDialog from '../components/AddActivityDialog.vue'
import AddGoalDialog from '../components/AddGoalDialog.vue'
import NotMentor from '../components/NotMentor.vue'
import { session } from '../session'

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
})

// Student information
const student = createResource({
  url: 'student_tracker.api.get_student',
  params: { student: props.name },
  auto: session.isMentor,
})

// Activity records
const activities = createResource({
  url: 'student_tracker.api.get_activities',
  params: { student: props.name },
  auto: session.isMentor,
})

// Latest active goal
const goal = createResource({
  url: 'student_tracker.api.get_goal',
  params: { student: props.name },
  auto: session.isMentor,
})

const s = computed(() => student.data)

// Activity dialog
const showAdd = ref(false)

// Goal dialog
const showGoalDialog = ref(false)

// Progress update state
const updatingProgress = ref(false)

// Goal closing state
const closingGoal = ref(false)

// Update goal progress
async function updateProgress(value) {
  const percentage = Number(Array.isArray(value) ? value[0] : value)

  if (!goal.data || updatingProgress.value || closingGoal.value) return

  if (
    !Number.isInteger(percentage) ||
    percentage < 0 ||
    percentage > 100
  ) {
    toast.error('Progress must be between 0 and 100')
    return
  }

  updatingProgress.value = true

  try {
    await call('student_tracker.api.update_goal_progress', {
      goal: goal.data.name,
      actual_percentage: percentage,
    })

    toast.success('Goal progress updated')
    await goal.reload()
  } catch (error) {
    toast.error(
      error.messages?.[0] ||
      error.message ||
      'Failed to update progress'
    )

    await goal.reload()
  } finally {
    updatingProgress.value = false
  }
}

// Mark a 100% completed goal as closed
async function closeGoal() {
  if (!goal.data?.name || closingGoal.value || updatingProgress.value) {
    return
  }

  closingGoal.value = true

  try {
    await call('student_tracker.api.close_goal', {
      goal: goal.data.name,
    })

    toast.success('Goal marked as complete')

    // Refresh the active goal and activity history.
    await Promise.all([
      goal.reload(),
      activities.reload(),
    ])
  } catch (error) {
    toast.error(
      error.messages?.[0] ||
      error.message ||
      'Could not close the goal'
    )
  } finally {
    closingGoal.value = false
  }
}

// Refresh both sections after creating a new goal.
async function refreshAfterGoalSaved() {
  await Promise.all([
    goal.reload(),
    activities.reload(),
  ])
}

// Profile field component
const Field = (p) =>
  h('div', [
    h('dt', { class: 'text-xs text-ink-gray-5' }, p.label),
    h('dd', { class: 'text-ink-gray-9' }, p.value || '—'),
  ])

Field.props = ['label', 'value']

const join = (a, b) => [a, b].filter(Boolean).join(' · ')

const formatDate = (d) =>
  dayjs(d).format('dddd, DD MMM YYYY')

const fromNow = (d) =>
  dayjs(d).fromNow?.() ?? dayjs(d).format('DD MMM YYYY HH:mm')
</script>
