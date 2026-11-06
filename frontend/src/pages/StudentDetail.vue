<template>
  <NotMentor v-if="!session.isMentor" />
  <main v-else class="mx-auto max-w-6xl px-4 py-6">
    <Button variant="ghost" icon-left="lucide-arrow-left" label="All students" :route="{ name: 'Students' }" />

    <div v-if="student.error" class="mt-4 rounded-lg bg-surface-red-2 p-4 text-sm text-ink-red-8">
      {{ student.error.messages?.join(', ') || student.error.message }}
    </div>

    <div v-else class="mt-4 grid gap-6 lg:grid-cols-[320px_1fr]">
      <!-- Profile -->
      <aside class="h-fit rounded-xl border border-outline-gray-2 bg-surface-base p-5">
        <div v-if="!s" class="h-80 animate-pulse rounded-lg bg-surface-gray-3" />
        <template v-else>
          <div class="flex flex-col items-center text-center">
            <StudentPhoto :src="s.photo" :name="s.name1" size="lg" />
            <h1 class="mt-3 text-xl font-semibold">{{ s.name1 || s.name }}</h1>
            <div class="text-xs text-ink-gray-5">{{ s.name }}</div>
          </div>
          <dl class="mt-5 space-y-3 text-sm">
            <Field label="House name" :value="s.house_name" />
            <Field label="Phone" :value="s.phone_number" />
            <Field label="Parent" :value="s.parent_name" />
            <Field label="Parent contact" :value="s.parent_contact_number" />
            <Field label="School" :value="join(s.school_name, s.school_class)" />
            <Field label="Madrassa" :value="join(s.madrassa_name, s.madrassa_class)" />
          </dl>
        </template>
      </aside>

      <!-- Activities -->
      <section>
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold">Activity notes</h2>
            <p class="text-sm text-ink-gray-5">
              {{ activities.data?.length ?? 0 }} record{{ activities.data?.length === 1 ? '' : 's' }}
            </p>
          </div>
          <Button variant="solid" icon-left="lucide-plus" label="Add activity" :disabled="!s" @click="showAdd = true" />
        </div>

        <div v-if="activities.loading && !activities.data" class="mt-4 space-y-3">
          <div v-for="i in 3" :key="i" class="h-24 animate-pulse rounded-xl bg-surface-gray-3" />
        </div>

        <div
          v-else-if="!activities.data?.length"
          class="mt-4 rounded-xl border border-dashed border-outline-gray-3 p-10 text-center"
        >
          <span class="lucide-notebook-pen mx-auto block size-8 text-ink-gray-4" />
          <p class="mt-3 font-medium">No activities recorded yet</p>
          <p class="mt-1 text-sm text-ink-gray-5">Add the first activity note for this student.</p>
        </div>

        <ol v-else class="relative mt-4 space-y-4 border-l border-outline-gray-2 pl-6">
          <li v-for="a in activities.data" :key="a.name" class="relative">
            <span class="absolute -left-[31px] top-4 size-3 rounded-full border-2 border-surface-base bg-surface-gray-7" />
            <div class="rounded-xl border border-outline-gray-2 bg-surface-base p-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="font-medium">{{ formatDate(a.activity_date) }}</div>
                <div class="text-xs text-ink-gray-5">
                  by {{ a.owner }} · {{ fromNow(a.creation) }}
                </div>
              </div>
              <div class="activity-note mt-2 text-sm text-ink-gray-8" v-html="a.activity_note || '<p>—</p>'" />
            </div>
          </li>
        </ol>
      </section>
    </div>

    <AddActivityDialog v-model:open="showAdd" :student="s" @saved="activities.reload()" />
  </main>
</template>

<script setup>
import { computed, h, ref } from 'vue'
import { Button, createResource, dayjs } from 'frappe-ui'
import StudentPhoto from '../components/StudentPhoto.vue'
import AddActivityDialog from '../components/AddActivityDialog.vue'
import NotMentor from '../components/NotMentor.vue'
import { session } from '../session'

const props = defineProps({ name: { type: String, required: true } })

const student = createResource({
  url: 'student_tracker.api.get_student',
  params: { student: props.name },
  auto: session.isMentor,
})
const activities = createResource({
  url: 'student_tracker.api.get_activities',
  params: { student: props.name },
  auto: session.isMentor,
})
const s = computed(() => student.data)
const showAdd = ref(false)

const Field = (p) =>
  h('div', [
    h('dt', { class: 'text-xs text-ink-gray-5' }, p.label),
    h('dd', { class: 'text-ink-gray-9' }, p.value || '—'),
  ])
Field.props = ['label', 'value']

const join = (a, b) => [a, b].filter(Boolean).join(' · ')
const formatDate = (d) => dayjs(d).format('dddd, DD MMM YYYY')
const fromNow = (d) => dayjs(d).fromNow?.() ?? dayjs(d).format('DD MMM YYYY HH:mm')
</script>
