
<template>
  <NotMentor v-if="!session.isMentor" />

  <main v-else class="mx-auto max-w-6xl px-4 py-6">
    <!-- Navigation -->
    <Button
      variant="ghost"
      icon-left="lucide-arrow-left"
      label="All students"
      :route="{ name: 'Students' }"
    />

    <!-- Error -->
    <div
      v-if="student.error"
      class="mt-4 rounded-xl border border-outline-red-2 bg-surface-red-2 p-4 text-sm text-ink-red-8"
    >
      {{ student.error.messages?.join(', ') || student.error.message }}
    </div>

    <div v-else class="mt-5 flex flex-col gap-7">
      <!-- Combined Student and Goal Card -->
      <div
        class="overflow-hidden rounded-2xl border border-outline-gray-2 bg-surface-base shadow-sm"
      >
        <div class="grid grid-cols-1 md:grid-cols-2">
          <!-- STUDENT PROFILE -->
          <section class="min-w-0 p-6 lg:p-7">
            <!-- Section heading -->
            <div class="mb-6 flex items-center gap-2">
              <span
                class="flex size-8 items-center justify-center rounded-lg bg-surface-gray-2 text-ink-gray-7"
              >
                <span class="lucide-user-round size-4" />
              </span>

              <div>
                <p class="text-xs font-semibold uppercase tracking-wider text-ink-gray-5">
                  Student information
                </p>
                <p class="text-xs text-ink-gray-4">
                  Personal and academic details
                </p>
              </div>
            </div>

            <!-- Loading -->
            <div
              v-if="!s"
              class="h-48 animate-pulse rounded-xl bg-surface-gray-3"
            />

            <template v-else>
              <!-- Student identity -->
              <div class="flex items-center gap-5 border-b border-outline-gray-1 pb-6">
                <div
                  class="flex size-24 shrink-0 items-center justify-center overflow-hidden rounded-2xl bg-surface-gray-2"
                >
                  <StudentPhoto
                    :src="s.photo"
                    :name="s.name1"
                    size="lg"
                  />
                </div>

                <div class="min-w-0">
                  <h1 class="text-xl font-semibold leading-snug text-ink-gray-9">
                    {{ s.name1 || s.name }}
                  </h1>

                  <p class="mt-1 text-sm text-ink-gray-5">
                    {{ s.name }}
                  </p>

                  <div class="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-surface-gray-2 px-2.5 py-1">
                    <span class="lucide-id-card size-3.5 text-ink-gray-5" />
                    <span class="text-xs font-medium text-ink-gray-7">
                      Student record
                    </span>
                  </div>
                </div>
              </div>

              <!-- Student details -->
              <div class="mt-6">
                <p class="mb-4 text-xs font-semibold uppercase tracking-wider text-ink-gray-5">
                  Contact & academic details
                </p>

                <dl class="grid grid-cols-1 gap-x-5 gap-y-5 sm:grid-cols-2">
                  <Field
                    label="House name"
                    :value="s.house_name"
                    icon="lucide-house"
                  />

                  <Field
                    label="Phone"
                    :value="s.phone_number"
                    icon="lucide-phone"
                  />

                  <Field
                    label="Parent"
                    :value="s.parent_name"
                    icon="lucide-user-round"
                  />

                  <Field
                    label="Parent contact"
                    :value="s.parent_contact_number"
                    icon="lucide-phone-call"
                  />

                  <Field
                    label="School"
                    :value="join(s.school_name, s.school_class)"
                    icon="lucide-school"
                  />

                  <Field
                    label="Madrassa"
                    :value="join(s.madrassa_name, s.madrassa_class)"
                    icon="lucide-book-open"
                  />
                </dl>
              </div>
            </template>
          </section>

          <!-- STUDENT GOAL -->
          <section
            class="min-w-0 border-t border-outline-gray-2 bg-surface-gray-1/30 p-6 md:border-l md:border-t-0 lg:p-7"
          >
            <!-- Goal heading -->
            <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
              <div class="flex items-center gap-2">
                <span
                  class="flex size-8 items-center justify-center rounded-lg bg-surface-gray-2 text-ink-gray-7"
                >
                  <span class="lucide-target size-4" />
                </span>

                <div>
                  <p class="text-xs font-semibold uppercase tracking-wider text-ink-gray-5">
                    Student goal
                  </p>
                  <p class="text-xs text-ink-gray-4">
                    Goal tracking and progress
                  </p>
                </div>
              </div>

              <!-- Goal badges -->
              <!-- Status badge only -->
              <div
                v-if="goal.data && !showGoalDialog"
                class="flex flex-wrap items-center gap-2"
              >
                <Badge
                  :label="goal.data.status"
                  :theme="
                    isGoalCompleted(goal.data)
                      ? 'green'
                      : goal.data.status === 'Ongoing'
                        ? 'blue'
                        : 'gray'
                  "
                />
              </div>
            </div>

            <!-- Loading -->
            <div
              v-if="goal.loading"
              class="rounded-xl border border-outline-gray-1 bg-surface-base p-5"
            >
              <div class="h-4 w-32 animate-pulse rounded bg-surface-gray-3" />
              <div class="mt-4 h-12 animate-pulse rounded bg-surface-gray-3" />
              <div class="mt-5 h-3 animate-pulse rounded bg-surface-gray-3" />
            </div>

            <!-- Existing Goal -->
            <div
              v-else-if="goal.data && !showGoalDialog"
              class="space-y-5"
            >
              <!-- Task description -->
              <div class="rounded-xl border border-outline-gray-1 bg-surface-base p-4">
                <div class="mb-2 flex items-center gap-2">
                  <span class="lucide-clipboard-list size-4 text-ink-gray-5" />
                  <p class="text-xs font-semibold uppercase tracking-wider text-ink-gray-5">
                    Goal description
                  </p>
                </div>

                <p class="text-sm font-medium leading-relaxed text-ink-gray-9">
                  {{ goal.data.task_description }}
                </p>
              </div>

              <!-- Goal metadata -->
              <div class="grid grid-cols-2 gap-3">
                <!-- Started date -->
                <div class="rounded-xl border border-outline-gray-1 bg-surface-base p-3.5">
                  <div class="flex items-center gap-2">
                    <span class="lucide-calendar-plus size-4 text-ink-gray-5" />
                    <p class="text-xs text-ink-gray-5">
                      Started on
                    </p>
                  </div>

                  <p class="mt-2 text-sm font-medium text-ink-gray-8">
                    {{
                      goal.data.created_on
                        ? dayjs(goal.data.created_on).format('DD MMM YYYY')
                        : '—'
                    }}
                  </p>

                  <p class="mt-0.5 text-xs text-ink-gray-5">
                    {{
                      goal.data.created_on
                        ? dayjs(goal.data.created_on).format('hh:mm A')
                        : ''
                    }}
                  </p>
                </div>

                <!-- Ended date -->
                <div class="rounded-xl border border-outline-gray-1 bg-surface-base p-3.5">
                  <div class="flex items-center gap-2">
                    <span class="lucide-calendar-check size-4 text-ink-gray-5" />
                    <p class="text-xs text-ink-gray-5">
                      Ended on
                    </p>
                  </div>

                  <p class="mt-2 text-sm font-medium text-ink-gray-8">
                    {{
                      goal.data.closed_on
                        ? dayjs(goal.data.closed_on).format('DD MMM YYYY')
                        : 'Not ended'
                    }}
                  </p>

                  <p class="mt-0.5 text-xs text-ink-gray-5">
                    {{
                      goal.data.closed_on
                        ? dayjs(goal.data.closed_on).format('hh:mm A')
                        : 'Currently active'
                    }}
                  </p>
                </div>
              </div>

              <!-- Goal term -->
              <div class="flex items-center justify-between rounded-xl border border-outline-gray-1 bg-surface-base px-4 py-3">
                <div class="flex items-center gap-2">
                  <span class="lucide-clock-3 size-4 text-ink-gray-5" />
                  <span class="text-sm text-ink-gray-6">
                    Goal duration
                  </span>
                </div>

                <Badge
                  :label="goal.data.goal_term || 'Short Term'"
                  :theme="
                    goal.data.goal_term === 'Long Term'
                      ? 'violet'
                      : 'amber'
                  "
                />
              </div>

              <!-- Progress section -->
              <div class="rounded-xl border border-outline-gray-1 bg-surface-base p-4">
                <div class="mb-4 flex items-center justify-between">
                  <div>
                    <p class="text-sm font-semibold text-ink-gray-8">
                      Overall progress
                    </p>
                    <p class="mt-0.5 text-xs text-ink-gray-5">
                      {{
                        isGoalCompleted(goal.data)
                          ? 'Goal successfully completed'
                          : "Update the student's goal progress"
                      }}
                    </p>
                  </div>

                  <div class="text-right">
                    <p
                      class="text-2xl font-semibold tabular-nums"
                      :class="isGoalCompleted(goal.data) ? 'text-green-600' : 'text-ink-gray-9'"
                    >
                      {{ goal.data.actual_percentage || 0 }}%
                    </p>
                  </div>
                </div>

                <!-- Interactive Frappe UI Slider -->
                <Slider
                  :model-value="[
                    Number(goal.data.actual_percentage || 0),
                  ]"
                  :min="0"
                  :max="100"
                  :step="1"
                  size="md"
                  :disabled="
                    updatingProgress ||
                    isGoalCompleted(goal.data)
                  "
                  @value-commit="updateProgress"
                />

                <div class="mt-2 flex justify-between text-xs text-ink-gray-5">
                  <span>0%</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>

                <p
                  v-if="updatingProgress"
                  class="mt-3 text-xs text-ink-gray-5"
                >
                  Updating progress...
                </p>

                <p
                  v-else-if="isGoalCompleted(goal.data)"
                  class="mt-3 flex items-center gap-2 text-xs font-medium text-ink-green-7"
                >
                  <span class="lucide-check-circle size-4" />
                  Goal completed successfully.
                </p>
              </div>

              <!-- Goal actions -->
              <!-- Completed: show both buttons side by side -->
              <div
                v-if="isGoalCompleted(goal.data)"
                class="flex flex-col gap-2 sm:flex-row"
              >
                <Button
                  class="flex-1"
                  variant="solid"
                  icon-left="lucide-plus"
                  label="Set New Goal"
                  @click="showGoalDialog = true"
                />

                <Button
                  class="flex-1"
                  variant="subtle"
                  icon-left="lucide-history"
                  label="View Goal History"
                  @click="showGoalHistory = true"
                />
              </div>

              <!-- Active: show history button in the same action position -->
              <Button
                v-else
                block
                variant="subtle"
                icon-left="lucide-history"
                label="View Goal History"
                @click="showGoalHistory = true"
              />
            </div>

            <!-- No Active Goal -->
            <div
              v-else-if="!goal.data && !showGoalDialog"
              class="flex min-h-64 flex-col items-center justify-center rounded-xl border border-dashed border-outline-gray-2 bg-surface-base px-5 py-8 text-center"
            >
              <div class="flex size-12 items-center justify-center rounded-2xl bg-surface-gray-2">
                <span class="lucide-target size-6 text-ink-gray-5" />
              </div>

              <p class="mt-4 text-sm font-semibold text-ink-gray-8">
                No active goal
              </p>

              <p class="mt-1 max-w-xs text-xs leading-relaxed text-ink-gray-5">
                Set a goal for this student to start tracking their progress.
              </p>

              <Button
                class="mt-4"
                variant="solid"
                icon-left="lucide-plus"
                label="Set New Goal"
                :disabled="!s"
                @click="showGoalDialog = true"
              />
            </div>
          </section>
        </div>
      </div>

      <!-- ACTIVITY NOTES -->
      <section class="w-full">
        <!-- Activity heading -->
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink-gray-9">
              Activity notes
            </h2>

            <p class="mt-0.5 text-sm text-ink-gray-5">
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
          class="mt-4 rounded-xl border border-dashed border-outline-gray-3 bg-surface-base p-10 text-center"
        >
          <span
            class="lucide-notebook-pen mx-auto block size-8 text-ink-gray-4"
          />

          <p class="mt-3 font-medium text-ink-gray-8">
            No activities recorded yet
          </p>

          <p class="mt-1 text-sm text-ink-gray-5">
            Add the first activity note for this student.
          </p>
        </div>

        <!-- Activity Timeline -->
        <ol
          v-else
          class="relative mt-5 space-y-4 border-l border-outline-gray-2 pl-6"
        >
          <li
            v-for="a in activities.data"
            :key="a.name"
            class="relative"
          >
            <span
              class="absolute -left-[31px] top-4 size-3 rounded-full border-2 border-surface-base bg-surface-gray-7"
            />

            <div
              class="rounded-xl border border-outline-gray-2 bg-surface-base p-4 shadow-sm"
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="font-medium text-ink-gray-9">
                  {{ formatDate(a.activity_date) }}
                </div>

                <div class="text-xs text-ink-gray-5">
                  by {{ a.owner }} · {{ fromNow(a.creation) }}
                </div>
              </div>

              <div
                class="activity-note mt-3 text-sm text-ink-gray-8"
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

    <!-- Goal History Dialog -->
    <GoalHistoryDialog
      v-model:open="showGoalHistory"
      :student="s.name"
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

import GoalHistoryDialog from '../components/GoalHistoryDialog.vue'
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

// Latest goal, including completed goals
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

// Goal history dialog
const showGoalHistory = ref(false)

// Progress update state
const updatingProgress = ref(false)

// Check whether the goal is completed.
// This also handles older records where is_closed may not be set.
function isGoalCompleted(goalRecord) {
  return (
    !!goalRecord?.is_closed ||
    Number(goalRecord?.actual_percentage) >= 100 ||
    goalRecord?.status === 'Complete'
  )
}

// Update goal progress.
// Reaching 100% automatically closes the goal in the backend.
async function updateProgress(value) {
  const percentage = Number(Array.isArray(value) ? value[0] : value)

  if (!goal.data || updatingProgress.value) return

  if (isGoalCompleted(goal.data)) return

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
    const result = await call(
      'student_tracker.api.update_goal_progress',
      {
        goal: goal.data.name,
        actual_percentage: percentage,
      }
    )

    if (Number(result.actual_percentage) === 100 && result.is_closed) {
      toast.success('Goal completed successfully')
    } else {
      toast.success('Goal progress updated')
    }

    // Reload the goal and activity history.
    // get_goal returns completed goals as well.
    await Promise.all([
      goal.reload(),
      activities.reload(),
    ])
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

// Refresh both sections after creating a new goal.
async function refreshAfterGoalSaved() {
  await Promise.all([
    goal.reload(),
    activities.reload(),
  ])
}

// Profile field component
const Field = (p) =>
  h('div', { class: 'min-w-0' }, [
    h('dt', { class: 'flex items-center gap-2 text-xs text-ink-gray-5' }, [
      p.icon
        ? h('span', { class: `${p.icon} size-3.5 shrink-0` })
        : null,
      p.label,
    ]),
    h(
      'dd',
      {
        class:
          'mt-1 break-words text-sm font-medium leading-relaxed text-ink-gray-9',
      },
      p.value || '—'
    ),
  ])

Field.props = ['label', 'value', 'icon']

const join = (a, b) => [a, b].filter(Boolean).join(' · ')

const formatDate = (d) =>
  dayjs(d).format('dddd, DD MMM YYYY')

const fromNow = (d) =>
  dayjs(d).fromNow?.() ?? dayjs(d).format('DD MMM YYYY HH:mm')
</script>
