
<template>
  <NotMentor v-if="!session.isMentor" />

  <main v-else class="mx-auto max-w-6xl px-4 py-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold">My students</h1>

        <p class="mt-1 text-sm text-ink-gray-5">
          <template v-if="students.data">
            {{ students.data.length }}
            student{{ students.data.length === 1 ? '' : 's' }}
            assigned to you
          </template>

          <template v-else>
            Students assigned to you
          </template>
        </p>
      </div>

      <div class="flex flex-col gap-2 sm:flex-row">
        <Button
          variant="solid"
          icon-left="lucide-user-plus"
          label="Add Student"
          class="w-full sm:w-auto"
          @click="showStudentDialog = true"
        />

        <div class="flex gap-2 sm:w-80">
          <TextInput
            v-model="search"
            class="flex-1"
            placeholder="Search name, ID, school…"
            :debounce="150"
          >
            <template #prefix>
              <span class="lucide-search size-4 text-ink-gray-5" />
            </template>
          </TextInput>

          <Button
            icon="lucide-refresh-cw"
            tooltip="Reload"
            :loading="students.loading"
            @click="students.reload()"
          />
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div
      v-if="students.loading && !students.data"
      class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      <div
        v-for="i in 6"
        :key="i"
        class="h-56 animate-pulse rounded-xl bg-surface-gray-3"
      />
    </div>

    <!-- Error -->
    <div
      v-else-if="students.error"
      class="mt-6 rounded-lg bg-surface-red-2 p-4 text-sm text-ink-red-8"
    >
      {{ students.error.messages?.join(', ') || students.error.message }}
    </div>

    <!-- Empty -->
    <div
      v-else-if="students.data && !students.data.length"
      class="mt-10 rounded-xl border border-dashed border-outline-gray-3 p-10 text-center"
    >
      <span class="lucide-users mx-auto block size-8 text-ink-gray-4" />

      <p class="mt-3 font-medium">
        No students assigned yet
      </p>

      <p class="mt-1 text-sm text-ink-gray-5">
        You can add a student using the Add Student button above.
      </p>
    </div>

    <!-- Student grid -->
    <div
      v-else
      class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      <article
        v-for="s in filtered"
        :key="s.name"
        class="flex flex-col rounded-xl border border-outline-gray-2 bg-surface-base p-4 transition hover:shadow-md"
      >
        <!-- Student information -->
        <div class="flex gap-4">
          <StudentPhoto
            :src="s.photo"
            :name="s.name1"
          />

          <div class="min-w-0 flex-1">
            <router-link
              :to="{ name: 'Student', params: { name: s.name } }"
              class="block truncate text-lg font-semibold hover:underline"
            >
              {{ s.name1 || s.name }}
            </router-link>

            <div class="text-xs text-ink-gray-5">
              {{ s.name }}
            </div>

            <div
              v-if="s.house_name"
              class="mt-1 truncate text-sm text-ink-gray-6"
            >
              <span class="lucide-home mr-1 inline-block size-3.5 align-[-2px]" />
              {{ s.house_name }}
            </div>

            <div
              v-if="s.phone_number"
              class="truncate text-sm text-ink-gray-6"
            >
              <span class="lucide-phone mr-1 inline-block size-3.5 align-[-2px]" />
              {{ s.phone_number }}
            </div>
          </div>
        </div>

        <!-- School and family information -->
        <dl class="mt-4 grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
          <div>
            <dt class="text-xs text-ink-gray-5">
              School
            </dt>

            <dd class="truncate">
              {{ s.school_name || '—' }}

              <span
                v-if="s.school_class"
                class="text-ink-gray-5"
              >
                · {{ s.school_class }}
              </span>
            </dd>
          </div>

          <div>
            <dt class="text-xs text-ink-gray-5">
              Madrassa
            </dt>

            <dd class="truncate">
              {{ s.madrassa_name || '—' }}

              <span
                v-if="s.madrassa_class"
                class="text-ink-gray-5"
              >
                · {{ s.madrassa_class }}
              </span>
            </dd>
          </div>

          <div class="col-span-2">
            <dt class="text-xs text-ink-gray-5">
              Parent
            </dt>

            <dd class="truncate">
              {{ s.parent_name || '—' }}

              <span
                v-if="s.parent_contact_number"
                class="text-ink-gray-5"
              >
                · {{ s.parent_contact_number }}
              </span>
            </dd>
          </div>
        </dl>

        <!-- Activity information -->
        <div class="mt-4 flex items-center gap-2">
          <Badge
            :theme="s.activity_count ? 'green' : 'gray'"
            :label="`${s.activity_count} activit${s.activity_count === 1 ? 'y' : 'ies'}`"
          />

          <span
            v-if="s.last_activity_date"
            class="text-xs text-ink-gray-5"
          >
            Last: {{ formatDate(s.last_activity_date) }}
          </span>
        </div>

        <!-- Student Goal -->
        <div class="mt-4 border-t border-outline-gray-1 pt-4">
          <div v-if="s.goal" class="space-y-3">

            <!-- Goal heading and badges -->
            <div class="flex items-center justify-between gap-2">
              <span class="text-sm font-medium text-ink-gray-7">
                Current Goal
              </span>

              <div class="flex flex-wrap items-center gap-2">
                <Badge
                  :label="`${s.goal.goal_term || 'Short Term'} Goal`"
                  :theme="
                    s.goal.goal_term === 'Long Term'
                      ? 'violet'
                      : 'amber'
                  "
                />

                <Badge
                  :label="s.goal.status"
                  :theme="
                    isGoalCompleted(s.goal)
                      ? 'green'
                      : s.goal.status === 'Ongoing'
                        ? 'blue'
                        : 'gray'
                  "
                />
              </div>
            </div>

            <!-- Goal description -->
            <p class="text-sm text-ink-gray-5">
              {{ s.goal.task_description }}
            </p>

            <!-- Goal progress -->
            <div class="flex items-center gap-3">
              <div class="h-2 flex-1 overflow-hidden rounded-full bg-surface-gray-3">
                <div
                  class="h-full rounded-full transition-all duration-300"
                  :class="
                    isGoalCompleted(s.goal)
                      ? 'bg-green-500'
                      : 'bg-blue-500'
                  "
                  :style="{
                    width: `${getGoalProgress(s.goal)}%`,
                  }"
                />
              </div>

              <span
                class="text-xs font-medium tabular-nums"
                :class="
                  isGoalCompleted(s.goal)
                    ? 'text-green-600'
                    : 'text-ink-gray-6'
                "
              >
                {{ getGoalProgress(s.goal) }}%
              </span>
            </div>

            <!-- Completion information -->
            <div
              v-if="isGoalCompleted(s.goal)"
              class="flex items-center gap-1.5 text-xs font-medium text-green-600"
            >
              <span class="lucide-check-circle size-3.5" />
              Goal completed
              <span v-if="s.goal.closed_on">
                · {{ formatDate(s.goal.closed_on) }}
              </span>
            </div>

            <!-- Set New Goal for completed goal -->
            <Button
              v-if="isGoalCompleted(s.goal)"
              block
              size="sm"
              variant="solid"
              icon-left="lucide-plus"
              label="Set New Goal"
              @click="openGoalDialog(s)"
            />
          </div>

          <!-- No goal -->
          <div
            v-else
            class="flex items-center justify-between gap-2"
          >
            <span class="text-sm text-ink-gray-5">
              No goal set
            </span>

            <Button
              size="sm"
              variant="subtle"
              icon-left="lucide-plus"
              label="Add Goal"
              @click="openGoalDialog(s)"
            />
          </div>
        </div>

        <!-- Actions -->
        <div class="mt-4 flex gap-2 border-t border-outline-gray-1 pt-4">
          <Button
            class="flex-1"
            variant="solid"
            icon-left="lucide-plus"
            label="Add activity"
            @click="openAdd(s)"
          />

          <Button
            class="flex-1"
            icon-left="lucide-history"
            label="View notes"
            :route="{ name: 'Student', params: { name: s.name } }"
          />
        </div>
      </article>

      <!-- No search results -->
      <p
        v-if="!filtered.length"
        class="col-span-full py-10 text-center text-sm text-ink-gray-5"
      >
        No students match “{{ search }}”.
      </p>
    </div>

    <!-- Add Student dialog -->
    <AddStudentDialog
      v-model:open="showStudentDialog"
      @saved="students.reload()"
    />

    <!-- Activity dialog -->
    <AddActivityDialog
      v-model:open="showAdd"
      :student="selected"
      @saved="students.reload()"
    />

    <!-- Goal dialog -->
    <AddGoalDialog
      v-model:open="showGoalDialog"
      :student="selectedGoalStudent"
      @saved="students.reload()"
    />
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'

import {
  Badge,
  Button,
  TextInput,
  createResource,
  dayjs,
} from 'frappe-ui'

import StudentPhoto from '../components/StudentPhoto.vue'
import AddActivityDialog from '../components/AddActivityDialog.vue'
import AddGoalDialog from '../components/AddGoalDialog.vue'
import AddStudentDialog from '../components/AddStudentDialog.vue'
import NotMentor from '../components/NotMentor.vue'
import { session } from '../session'

// Students resource
const students = createResource({
  url: 'student_tracker.api.get_my_students',
  auto: session.isMentor,
  cache: 'mentor-students',
})

// Search
const search = ref('')

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const rows = students.data || []

  if (!q) return rows

  return rows.filter((s) =>
    [
      s.name,
      s.name1,
      s.house_name,
      s.school_name,
      s.madrassa_name,
      s.parent_name,
      s.phone_number,
    ]
      .filter(Boolean)
      .some((v) => String(v).toLowerCase().includes(q)),
  )
})

// Add Student dialog
const showStudentDialog = ref(false)

// Activity dialog
const showAdd = ref(false)
const selected = ref(null)

function openAdd(student) {
  selected.value = student
  showAdd.value = true
}

// Goal dialog
const showGoalDialog = ref(false)
const selectedGoalStudent = ref(null)

function openGoalDialog(student) {
  selectedGoalStudent.value = student
  showGoalDialog.value = true
}

// Determine whether a goal is completed.
function isGoalCompleted(goal) {
  return (
    !!goal &&
    (
      Number(goal.actual_percentage) >= 100 ||
      Number(goal.is_closed) === 1 ||
      goal.is_closed === true ||
      goal.status === 'Complete'
    )
  )
}

// Keep progress within 0–100.
function getGoalProgress(goal) {
  return Math.min(
    100,
    Math.max(0, Number(goal?.actual_percentage) || 0),
  )
}

function formatDate(d) {
  return dayjs(d).format('DD MMM YYYY')
}
</script>
