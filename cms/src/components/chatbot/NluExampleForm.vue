<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { mdiContentSave, mdiClose } from '@mdi/js'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import NotificationBarInCard from '@/components/NotificationBarInCard.vue'
import IntentService from '@/services/intent.service'

const props = defineProps({
  nluExample: {
    type: Object,
    default: () => ({
      intent_id: null,
      text: ''
    })
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const form = reactive({
  intent_id: null,
  text: ''
})

const errors = ref({})
const isSubmitting = ref(false)
const formStatusOptions = ['success', 'danger']
const formStatusCurrent = ref(null)
const formStatusMessage = ref('')
const intents = ref([])
const isLoadingIntents = ref(false)

// Reset form when nluExample prop changes
watch(
  () => props.nluExample,
  (newVal) => {
    if (newVal) {
      form.intent_id = newVal.intent_id || null
      form.text = newVal.text || ''
    }
  },
  { immediate: true, deep: true }
)

const title = computed(() => props.isEdit ? 'Chỉnh sửa mẫu câu' : 'Thêm mẫu câu mới')

const validateForm = () => {
  const newErrors = {}
  
  if (!form.intent_id) {
    newErrors.intent_id = 'Vui lòng chọn intent'
  }
  
  if (!form.text.trim()) {
    newErrors.text = 'Nội dung mẫu câu không được để trống'
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
    formStatusMessage.value = props.isEdit ? 'Cập nhật mẫu câu thành công!' : 'Tạo mẫu câu mới thành công!'
  } catch (error) {
    console.error('Form submission error:', error)
    formStatusCurrent.value = 'danger'
    formStatusMessage.value = 'Có lỗi xảy ra. Vui lòng thử lại!'
  } finally {
    isSubmitting.value = false
  }
}

const fetchIntents = async () => {
  isLoadingIntents.value = true
  try {
    const response = await IntentService.getIntents()
    intents.value = response.data
  } catch (error) {
    console.error('Error fetching intents:', error)
  } finally {
    isLoadingIntents.value = false
  }
}

onMounted(() => {
  fetchIntents()
})
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
      <FormField label="Intent" :help="errors.intent_id" help-class="text-red-500">
        <FormControl
          v-model="form.intent_id"
          type="select"
          placeholder="Chọn intent"
          :options="intents.map(intent => ({ value: intent.id, label: intent.name }))"
          :disabled="isSubmitting || isLoadingIntents"
        />
      </FormField>
      
      <FormField label="Nội dung" :help="errors.text" help-class="text-red-500">
        <FormControl
          v-model="form.text"
          type="textarea"
          placeholder="Nhập nội dung mẫu câu"
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
