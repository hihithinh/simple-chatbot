<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { mdiContentSave, mdiClose } from '@mdi/js'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import FormCheckRadioGroup from '@/components/FormCheckRadioGroup.vue'
import NotificationBarInCard from '@/components/NotificationBarInCard.vue'

const props = defineProps({
  intent: {
    type: Object,
    default: () => ({
      name: '',
      description: '',
      is_active: true
    })
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const form = reactive({
  name: '',
  description: '',
  is_active: true
})

const errors = ref({})
const isSubmitting = ref(false)
const formStatusOptions = ['success', 'danger']
const formStatusCurrent = ref(null)
const formStatusMessage = ref('')

// Reset form when intent prop changes
watch(
  () => props.intent,
  (newVal) => {
    if (newVal) {
      form.name = newVal.name || ''
      form.description = newVal.description || ''
      form.is_active = newVal.is_active !== undefined ? newVal.is_active : true
    }
  },
  { immediate: true, deep: true }
)

const title = computed(() => props.isEdit ? 'Chỉnh sửa Intent' : 'Thêm Intent mới')

const validateForm = () => {
  const newErrors = {}
  
  if (!form.name.trim()) {
    newErrors.name = 'Tên intent không được để trống'
  }
  
  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isSubmitting.value = true
  formStatusCurrent.value = null
  
  try {
    emit('submit', { ...form })
    formStatusCurrent.value = 'success'
    formStatusMessage.value = props.isEdit ? 'Cập nhật intent thành công!' : 'Tạo intent mới thành công!'
  } catch (error) {
    console.error('Form submission error:', error)
    formStatusCurrent.value = 'danger'
    formStatusMessage.value = 'Có lỗi xảy ra. Vui lòng thử lại!'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div>
    <NotificationBarInCard
      v-if="formStatusCurrent"
      :color="formStatusCurrent"
    >
      {{ formStatusMessage }}
    </NotificationBarInCard>
    
    <form @submit.prevent="handleSubmit">
      <FormField label="Tên Intent" :help="errors.name" help-class="text-red-500">
        <FormControl
          v-model="form.name"
          placeholder="Nhập tên intent"
          :disabled="isSubmitting"
        />
      </FormField>
      
      <FormField label="Mô tả" help="Mô tả ngắn gọn về intent này">
        <FormControl
          v-model="form.description"
          type="textarea"
          placeholder="Mô tả về intent này"
          :disabled="isSubmitting"
        />
      </FormField>
      
      <FormField label="Trạng thái">
        <FormCheckRadioGroup
          v-model="form.is_active"
          name="is_active"
          type="switch"
          :options="{ true: 'Hoạt động' }"
          :disabled="isSubmitting"
        />
      </FormField>
      
      <BaseButtons>
        <BaseButton
          type="submit"
          color="info"
          :icon="mdiContentSave"
          label="Lưu"
          :disabled="isSubmitting"
        />
        <BaseButton
          type="button"
          color="danger"
          :icon="mdiClose"
          outline
          label="Hủy"
          :disabled="isSubmitting"
          @click="emit('cancel')"
        />
      </BaseButtons>
    </form>
  </div>
</template>
