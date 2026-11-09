
<template>
  <NotMentor v-if="!session.isMentor" />
  <main v-else class="mx-auto max-w-6xl px-4 py-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold">My students</h1>
        <p class="mt-1 text-sm text-ink-gray-5">
          <template v-if="students.data">
            {{ students.data.length }} student{{ students.data.length === 1 ? '' : 's' }}
            assigned to you
          </template>
          <template v-else>Students assigned to you</template>
        </p>
      </div>

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
      <p class="mt-3 font-medium">No students assigned yet</p>
      <p class="mt-1 text-sm text-ink-gray-5">
        An administrator can assign students to you by setting the
        <b>Mentor</b> field on the Student record.
      </p>
    </div>

    <!-- Student grid -->
    <div v-else class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="s in filtered"
        :key="s.name"
        class="flex flex-col rounded-xl border border-outline-gray-2 bg-surface-base p-4 transition hover:shadow-md"
      >
        <!-- Student information -->
        <div class="flex gap-4">
          <StudentPhoto :src="s.photo" :name="s.name1" />

          <div class="min-w-0 flex-1">
            <router-link
              :to="{ name: 'Student', params: { name: s.name } }"
              class="block truncate text-lg font-semibold hover:underline"
            >
              {{ s.name1 || s.name }}
            </router-link>

            <div class="text-xs text-ink-gray-5">{{ s.name }}</div>

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
            <dt class="text-xs text-ink-gray-5">School</dt>
            <dd class="truncate">
              {{ s.school_name || '—' }}
              <span v-if="s.school_class" class="text-ink-gray-5">
                · {{ s.school_class }}
              </span>
            </dd>
          </div>

          <div>
            <dt class="text-xs text-ink-gray-5">Madrassa</dt>
            <dd class="truncate">
              {{ s.madrassa_name || '—' }}
              <span v-if="s.madrassa_class" class="text-ink-gray-5">
                · {{ s.madrassa_class }}
              </span>
            </dd>
          </div>

          <div class="col-span-2">
            <dt class="text-xs text-ink-gray-5">Parent</dt>
            <dd class="truncate">
              {{ s.parent_name || '—' }}
              <span v-if="s.parent_contact_number" class="text-ink-gray-5">
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

          <span v-if="s.last_activity_date" class="text-xs text-ink-gray-5">
            Last: {{ formatDate(s.last_activity_date) }}
          </span>
        </div>

        <!-- Student Goal -->
        
        <!-- Student Goal -->
        <div class="mt-4 border-t border-outline-gray-1 pt-4">
          <div v-if="s.goal" class="space-y-3">
            <div class="flex items-center justify-between gap-2">
              <span class="text-sm font-medium text-ink-gray-7">
                Current Goal
              </span>

              <Badge
                :label="s.goal.status"
                :theme="s.goal.status === 'Complete' ? 'green' : 'gray'"
              />
            </div>

            <p class="text-sm text-ink-gray-5">
              {{ s.goal.task_description }}
            </p>

            <div class="flex items-center gap-3">
              <div class="h-2 flex-1 overflow-hidden rounded-full bg-surface-gray-3">
                <div
                  class="h-full rounded-full transition-all duration-300"
                  :class="Number(s.goal.actual_percentage) >= 100 ? 'bg-green-500' : 'bg-blue-500'"
                  :style="{ width: `${s.goal.actual_percentage || 0}%` }"
                />
              </div>

              <span class="text-xs font-medium text-ink-gray-6">
                {{ s.goal.actual_percentage || 0 }}%
              </span>
            </div>

            <Button
              v-if="Number(s.goal.actual_percentage) >= 100"
              block
              size="sm"
              variant="solid"
              icon-left="lucide-check-circle"
              label="Mark as complete"
              :loading="closingGoal === s.goal.name"
              :disabled="!!closingGoal"
              @click="closeGoal(s.goal)"
            />
          </div>

          <div v-else class="flex items-center justify-between gap-2">
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

      <p
        v-if="!filtered.length"
        class="col-span-full py-10 text-center text-sm text-ink-gray-5"
      >
        No students match “{{ search }}”.
      </p>
    </div>

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
import { Badge, Button, TextInput, createResource, dayjs, call, toast } from 'frappe-ui'
import StudentPhoto from '../components/StudentPhoto.vue'
import AddActivityDialog from '../components/AddActivityDialog.vue'
import AddGoalDialog from '../components/AddGoalDialog.vue'
import NotMentor from '../components/NotMentor.vue'
import { session } from '../session'

const students = createResource({
  url: 'student_tracker.api.get_my_students',
  auto: session.isMentor,
  cache: 'mentor-students',
})

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

const closingGoal = ref(null)

async function closeGoal(goal) {
  if (!goal?.name || closingGoal.value) return

  closingGoal.value = goal.name

  try {
    await call('student_tracker.api.close_goal', {
      goal: goal.name,
    })

    toast.success('Goal marked as complete')
    await students.reload()
  } catch (error) {
    toast.error(
      error.messages?.[0] ||
      error.message ||
      'Could not close the goal'
    )
  } finally {
    closingGoal.value = null
  }
}

function openGoalDialog(student) {
  selectedGoalStudent.value = student
  showGoalDialog.value = true
}

function formatDate(d) {
  return dayjs(d).format('DD MMM YYYY')
}
</script>
