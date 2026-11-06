<template>
  <Dialog
    v-model:open="open"
    :title="`Add activity · ${student?.name1 || ''}`"
    message="Record what the student did. It will appear in their activity history."
  >
    <form id="add-activity-form" class="flex flex-col gap-4" @submit.prevent="submit">
      <DatePicker
        v-model="form.activity_date"
        label="Activity date"
        :max="today"
        :clearable="false"
        required
      />
      <Textarea
        v-model="form.activity_note"
        label="Activity note"
        placeholder="e.g. Completed the Quran recitation assignment, attended all classes this week…"
        :rows="6"
        required
        :error="error"
      />
    </form>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button label="Cancel" @click="open = false" />
        <Button
          type="submit"
          form="add-activity-form"
          variant="solid"
          label="Save activity"
          :loading="saving"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { Button, DatePicker, Dialog, Textarea, call, dayjs, toast } from 'frappe-ui'

const props = defineProps({
  student: { type: Object, default: null },
})
const emit = defineEmits(['saved'])
const open = defineModel('open', { type: Boolean, default: false })

const today = dayjs().format('YYYY-MM-DD')
const form = reactive({ activity_date: today, activity_note: '' })
const saving = ref(false)
const error = ref('')

watch(open, (isOpen) => {
  if (isOpen) {
    form.activity_date = today
    form.activity_note = ''
    error.value = ''
  }
})

async function submit() {
  if (!form.activity_note.trim()) {
    error.value = 'Please write an activity note'
    return
  }
  saving.value = true
  error.value = ''
  try {
    const doc = await call('student_tracker.api.add_activity', {
      student: props.student.name,
      activity_date: form.activity_date || today,
      activity_note: form.activity_note,
    })
    toast.success('Activity saved')
    open.value = false
    emit('saved', doc)
  } catch (e) {
    error.value = e?.messages?.join('\n') || e?.message || 'Could not save the activity'
  } finally {
    saving.value = false
  }
}
</script>
