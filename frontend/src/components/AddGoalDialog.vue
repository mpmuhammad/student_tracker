<template>
  <Dialog
    v-model:open="open"
    :title="`Add goal · ${student?.name1 || ''}`"
    message="Set a goal for this student. You can update their progress later."
  >
    <form
      id="add-goal-form"
      class="flex flex-col gap-4"
      @submit.prevent="submit"
    >
      <Select
        v-model="goalTerm"
        label="Goal term"
        :options="goalTermOptions"
      />

      <Textarea
        v-model="taskDescription"
        label="Task description"
        placeholder="Describe the goal or task for this student..."
        :rows="5"
        required
        :error="error"
      />

      <p class="text-xs text-ink-gray-5">
        The goal will start at 0% progress with Started status.
      </p>
    </form>

    <template #actions>
      <div class="flex justify-end gap-2">
        <Button
          label="Cancel"
          @click="open = false"
        />

        <Button
          type="submit"
          form="add-goal-form"
          variant="solid"
          label="Save goal"
          :loading="saving"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import {
  Button,
  Dialog,
  Select,
  Textarea,
  call,
  toast,
} from 'frappe-ui'

const props = defineProps({
  student: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['saved'])

const open = defineModel('open', {
  type: Boolean,
  default: false,
})

const goalTermOptions = [
  { label: 'Short Term', value: 'Short Term' },
  { label: 'Long Term', value: 'Long Term' },
]

const taskDescription = ref('')
const goalTerm = ref('Short Term')
const saving = ref(false)
const error = ref('')

watch(open, (isOpen) => {
  if (isOpen) {
    taskDescription.value = ''
    goalTerm.value = 'Short Term'
    error.value = ''
  }
})

async function submit() {
  const description = taskDescription.value.trim()

  if (!description) {
    error.value = 'Please enter a task description'
    return
  }

  if (!props.student?.name) {
    error.value = 'Student information is missing'
    return
  }

  saving.value = true
  error.value = ''

  try {
    const doc = await call('student_tracker.api.create_goal', {
      student: props.student.name,
      task_description: description,
      goal_term: goalTerm.value,
    })

    toast.success('Goal saved')
    open.value = false
    emit('saved', doc)
  } catch (e) {
    error.value =
      e?.messages?.join('\n') ||
      e?.message ||
      'Could not save the goal'
  } finally {
    saving.value = false
  }
}
</script>