<script setup>
import { ref } from 'vue'
import { mdiRobotExcited, mdiLoading, mdiCheck, mdiAlert } from '@mdi/js'
import BaseButton from '@/components/BaseButton.vue'
import CardBoxComponentTitle from '@/components/CardBoxComponentTitle.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import RasaIntegrationService from '@/services/rasa-integration.service'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['train', 'notification'])

const isTraining = ref(false)
const isComplete = ref(false)
const hasError = ref(false)
const trainingStatus = ref('')
const trainingSteps = ref([
  { id: 1, text: 'Chuẩn bị dữ liệu huấn luyện', done: false, active: false },
  { id: 2, text: 'Xuất dữ liệu NLU', done: false, active: false },
  { id: 3, text: 'Xuất dữ liệu Domain', done: false, active: false },
  { id: 4, text: 'Xuất dữ liệu Rules và Stories', done: false, active: false },
  { id: 5, text: 'Huấn luyện mô hình Rasa', done: false, active: false }
])

const showNotification = (type, message) => {
  emit('notification', { type, message })
}

const handleTrainRasa = async () => {
  isTraining.value = true
  hasError.value = false
  isComplete.value = false
  
  // Reset training steps
  trainingSteps.value.forEach(step => {
    step.done = false
    step.active = false
  })
  
  try {
    // Step 1: Preparing data
    trainingSteps.value[0].active = true
    trainingStatus.value = 'Đang chuẩn bị dữ liệu huấn luyện...'
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate preparation time
    trainingSteps.value[0].done = true
    trainingSteps.value[0].active = false
    
    // Step 2: Export NLU data
    trainingSteps.value[1].active = true
    trainingStatus.value = 'Đang xuất dữ liệu NLU...'
    await RasaIntegrationService.exportNlu()
    trainingSteps.value[1].done = true
    trainingSteps.value[1].active = false
    
    // Step 3: Export Domain data
    trainingSteps.value[2].active = true
    trainingStatus.value = 'Đang xuất dữ liệu Domain...'
    await RasaIntegrationService.exportDomain()
    trainingSteps.value[2].done = true
    trainingSteps.value[2].active = false
    
    // Step 4: Export Rules and Stories
    trainingSteps.value[3].active = true
    trainingStatus.value = 'Đang xuất dữ liệu Rules và Stories...'
    await RasaIntegrationService.exportRulesAndStories()
    trainingSteps.value[3].done = true
    trainingSteps.value[3].active = false
    
    // Step 5: Train Rasa model
    trainingSteps.value[4].active = true
    trainingStatus.value = 'Đang huấn luyện mô hình Rasa...'
    await RasaIntegrationService.trainModel()
    trainingSteps.value[4].done = true
    trainingSteps.value[4].active = false
    
    // Complete
    isComplete.value = true
    trainingStatus.value = 'Đã hoàn thành huấn luyện mô hình!'
    showNotification('success', 'Đã hoàn thành huấn luyện mô hình Rasa!')
    
    // Emit train event to parent
    emit('train')
  } catch (error) {
    console.error('Error training Rasa:', error)
    hasError.value = true
    trainingStatus.value = `Lỗi: ${error.message}`
    showNotification('danger', `Lỗi khi huấn luyện mô hình: ${error.response?.data?.detail || error.message}`)
  } finally {
    isTraining.value = false
  }
}
</script>

<template>
  <div>
    <CardBoxComponentTitle title="Bước 3: Huấn luyện lại RASA" />
    
    <p class="text-gray-600 mb-4">
      Hệ thống sẽ xuất dữ liệu từ cơ sở dữ liệu ra các file cấu hình của Rasa và tiến hành huấn luyện lại mô hình.
      Quá trình này có thể mất vài phút tùy thuộc vào lượng dữ liệu.
    </p>
    
    <div v-if="!isTraining && !isComplete" class="flex justify-center mt-6">
      <BaseButton
        :icon="props.isLoading ? mdiLoading : mdiRobotExcited"
        color="info"
        label="Bắt đầu huấn luyện"
        :loading="props.isLoading"
        :disabled="props.isLoading"
        @click="handleTrainRasa"
      />
    </div>
    
    <div v-if="isTraining || isComplete" class="mt-6">
      <div class="mb-4">
        <div class="flex items-center">
          <BaseIcon
            :path="isComplete ? mdiCheck : hasError ? mdiAlert : mdiLoading"
            :class="[
              isComplete ? 'text-green-500' : hasError ? 'text-red-500' : 'text-blue-500',
              isTraining && !hasError && !isComplete ? 'animate-spin' : ''
            ]"
            size="24"
          />
          <span 
            class="ml-2 font-medium"
            :class="[
              isComplete ? 'text-green-500' : hasError ? 'text-red-500' : 'text-blue-500'
            ]"
          >
            {{ trainingStatus }}
          </span>
        </div>
      </div>
      
      <div class="space-y-3 mt-6">
        <div 
          v-for="step in trainingSteps" 
          :key="step.id"
          class="flex items-center"
        >
          <div 
            class="w-6 h-6 rounded-full flex items-center justify-center"
            :class="[
              step.done ? 'bg-green-500' : 
              step.active ? 'bg-blue-500' : 
              'bg-gray-200'
            ]"
          >
            <BaseIcon 
              v-if="step.done" 
              :path="mdiCheck" 
              class="text-white" 
              size="16" 
            />
            <div 
              v-else-if="step.active" 
              class="w-3 h-3 rounded-full bg-white animate-pulse"
            ></div>
          </div>
          <span 
            class="ml-2"
            :class="[
              step.done ? 'text-green-500 font-medium' : 
              step.active ? 'text-blue-500 font-medium' : 
              'text-gray-500'
            ]"
          >
            {{ step.text }}
          </span>
        </div>
      </div>
      
      <div v-if="isComplete" class="flex justify-center mt-6">
        <BaseButton
          :icon="mdiCheck"
          color="success"
          label="Hoàn thành"
          @click="emit('train')"
        />
      </div>
    </div>
  </div>
</template>
