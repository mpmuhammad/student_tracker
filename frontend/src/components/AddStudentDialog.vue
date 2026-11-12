
<script setup>
import { ref, watch } from 'vue'
import {
  Button,
  Dialog,
  TextInput,
  Select,
  FileUploader,
  call,
  toast,
} from 'frappe-ui'

const open = defineModel('open', { default: false })
const emit = defineEmits(['saved'])

const name1 = ref('')
const houseName = ref('')
const phoneNumber = ref('')
const parentName = ref('')
const parentContactNumber = ref('')
const schoolName = ref('')
const schoolClass = ref('')
const madrassaName = ref('')
const madrassaClass = ref('')
const photo = ref('')

const saving = ref(false)
const loadingClasses = ref(false)
const classOptions = ref([])

function resetForm() {
  name1.value = ''
  houseName.value = ''
  phoneNumber.value = ''
  parentName.value = ''
  parentContactNumber.value = ''
  schoolName.value = ''
  schoolClass.value = ''
  madrassaName.value = ''
  madrassaClass.value = ''
  photo.value = ''
}

async function loadClasses() {
  loadingClasses.value = true

  try {
    const result = await call('frappe.client.get_list', {
      doctype: 'Class',
      fields: ['name'],
      filters: {
        enabled: 1,
      },
      limit_page_length: 100,
    })

    // Sort naturally: Class 1, Class 2 ... Class 12
    result.sort((a, b) => {
      const numberA = Number(a.name.match(/\d+/)?.[0] || 0)
      const numberB = Number(b.name.match(/\d+/)?.[0] || 0)
      return numberA - numberB
    })

    classOptions.value = result.map((item) => ({
      label: item.name,
      value: item.name,
    }))
  } catch (error) {
    toast.error('Failed to load classes')
    console.error(error)
  } finally {
    loadingClasses.value = false
  }
}

watch(open, (value) => {
  if (value) {
    resetForm()
    loadClasses()
  }
})

function handlePhotoUpload(file) {
  photo.value = file.file_url
  toast.success('Photo uploaded successfully')
}

function validatePhoto(file) {
  if (!file.type.startsWith('image/')) {
    return 'Please select an image file'
  }
}

async function submit() {
  if (!name1.value.trim()) {
    toast.error('Student name is required')
    return
  }

  saving.value = true

  try {
    await call('student_tracker.api.create_student', {
      name1: name1.value,
      house_name: houseName.value,
      phone_number: phoneNumber.value,
      parent_name: parentName.value,
      parent_contact_number: parentContactNumber.value,
      school_name: schoolName.value,
      school_class: schoolClass.value,
      madrassa_name: madrassaName.value,
      madrassa_class: madrassaClass.value,
      photo: photo.value,
    })

    toast.success('Student added successfully')
    open.value = false
    emit('saved')
  } catch (error) {
    toast.error(error.messages?.[0] || 'Failed to add student')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Dialog v-model:open="open" title="Add Student">
    <div class="space-y-0">

      <!-- Student Photo -->
      <div class="border-b border-gray-200 px-1 pb-5">
        <div class="flex items-center gap-4">
          <div
            class="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-full border border-gray-200 bg-gray-100"
          >
            <img
              v-if="photo"
              :src="photo"
              alt="Student photo"
              class="h-full w-full object-cover"
            />

            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              class="h-10 w-10 text-gray-400"
            >
              <circle cx="12" cy="8" r="4" />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M4 21a8 8 0 0 1 16 0"
              />
            </svg>
          </div>

          <div class="space-y-1">
            <p class="text-sm font-medium text-gray-800">Student Photo</p>
            <p class="text-xs text-gray-500">
              Upload in JPEG, PNG, or GIF format.
            </p>

            <FileUploader
              file-types="image/*"
              :validate-file="validatePhoto"
              @success="handlePhotoUpload"
            >
              <template #default="{ openFileSelector, uploading, progress, error }">
                <div class="space-y-1">
                  <Button
                    variant="outline"
                    size="sm"
                    :loading="uploading"
                    :disabled="uploading"
                    @click="openFileSelector"
                  >
                    {{ uploading ? `Uploading ${progress}%` : photo ? 'Change Photo' : 'Choose Photo' }}
                  </Button>

                  <p v-if="error" class="text-xs text-red-600">
                    {{ error }}
                  </p>
                </div>
              </template>
            </FileUploader>

            <button
              v-if="photo"
              type="button"
              class="text-xs text-red-600"
              @click="photo = ''"
            >
              Remove photo
            </button>
          </div>
        </div>
      </div>

      <!-- Personal Details -->
      <section class="border-b border-gray-200 px-1 py-5">
        <h3 class="mb-5 text-sm font-semibold text-gray-900">
          Personal Details
        </h3>

        <div class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-sm text-gray-600">Name *</label>
            <TextInput v-model="name1" placeholder="Enter student name" />
          </div>

          <div>
            <label class="mb-1 block text-sm text-gray-600">Parent Name</label>
            <TextInput v-model="parentName" placeholder="Enter parent name" />
          </div>

          <div>
            <label class="mb-1 block text-sm text-gray-600">House Name</label>
            <TextInput v-model="houseName" placeholder="Enter house name" />
          </div>

          <div>
            <label class="mb-1 block text-sm text-gray-600">
              Parent Contact Number
            </label>
            <TextInput
              v-model="parentContactNumber"
              placeholder="Enter parent contact number"
            />
          </div>

          <div>
            <label class="mb-1 block text-sm text-gray-600">Phone Number</label>
            <TextInput v-model="phoneNumber" placeholder="Enter phone number" />
          </div>
        </div>
      </section>

      <!-- Education Details -->
      <section class="px-1 pt-5 pb-2">
        <h3 class="mb-5 text-sm font-semibold text-gray-900">
          Education Details
        </h3>

        <div class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-sm text-gray-600">School Name</label>
            <TextInput v-model="schoolName" placeholder="Enter school name" />
          </div>

          <div>
            <label class="mb-1 block text-sm text-gray-600">Madrassa Name</label>
            <TextInput
              v-model="madrassaName"
              placeholder="Enter madrassa name"
            />
          </div>

          <div>
            <label class="mb-1 block text-sm text-gray-600">School Class</label>
            <Select
              v-model="schoolClass"
              :options="classOptions"
              :disabled="loadingClasses"
              placeholder="Select school class"
            />
          </div>

          <div>
            <label class="mb-1 block text-sm text-gray-600">Madrassa Class</label>
            <Select
              v-model="madrassaClass"
              :options="classOptions"
              :disabled="loadingClasses"
              placeholder="Select madrassa class"
            />
          </div>
        </div>
      </section>
    </div>

    <template #actions>
      <div class="flex items-center justify-end gap-3">
        <Button variant="subtle" @click="open = false">
          Cancel
        </Button>

        <Button
          variant="solid"
          :loading="saving"
          :disabled="saving"
          @click="submit"
        >
          Save Student
        </Button>
      </div>
    </template>
  </Dialog>
</template>
