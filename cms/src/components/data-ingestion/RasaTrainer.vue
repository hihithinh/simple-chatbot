<script setup>
import { ref, onUnmounted, computed } from 'vue'
import { mdiRobotExcited, mdiLoading, mdiCheck, mdiAlert, mdiConsole, mdiChevronDown, mdiChevronUp } from '@mdi/js'
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
const currentTaskId = ref(null)
const pollingInterval = ref(null)
const taskLogs = ref([])
const showLogs = ref(false)
const currentTask = ref(null)
const taskHistory = ref([])
const trainingSteps = ref([
  { id: 1, text: 'Xuất dữ liệu từ PostgreSQL', done: false, active: false, taskId: null, logs: [] },
  { id: 2, text: 'Huấn luyện mô hình Rasa', done: false, active: false, taskId: null, logs: [] },
  { id: 3, text: 'Khởi động lại Rasa server', done: false, active: false, taskId: null, logs: [] }
])

const formattedTime = computed(() => {
  if (!currentTask.value || !currentTask.value.start_time) return ''
  
  const startTime = new Date(currentTask.value.start_time)
  const endTime = currentTask.value.end_time ? new Date(currentTask.value.end_time) : new Date()
  const durationMs = endTime - startTime
  
  // Format duration as mm:ss
  const minutes = Math.floor(durationMs / 60000)
  const seconds = Math.floor((durationMs % 60000) / 1000)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

const showNotification = (type, message) => {
  emit('notification', { type, message })
}

// Hàm kiểm tra trạng thái task
const checkTaskStatus = async () => {
  if (!currentTaskId.value) return
  
  try {
    const response = await RasaIntegrationService.getTaskStatus(currentTaskId.value)
    currentTask.value = response
    
    // Cập nhật logs
    if (response.logs && response.logs.length > 0) {
      taskLogs.value = response.logs
      
      // Cập nhật logs cho bước hiện tại
      const currentStepIndex = trainingSteps.value.findIndex(step => step.active)
      if (currentStepIndex !== -1) {
        trainingSteps.value[currentStepIndex].logs = response.logs
      }
    }
    
    if (response.status === 'completed') {
      // Task hoàn thành, chuyển sang bước tiếp theo
      return true
    } else if (response.status === 'error') {
      // Task lỗi, dừng quá trình
      hasError.value = true
      trainingStatus.value = `Lỗi: ${response.error || response.message}`
      showNotification('danger', `Lỗi: ${response.error || response.message}`)
      clearInterval(pollingInterval.value)
      isTraining.value = false
      return false
    }
    
    // Cập nhật trạng thái
    trainingStatus.value = response.message
    return false
  } catch (error) {
    console.error('Error checking task status:', error)
    return false
  }
}

// Bước 1: Xuất dữ liệu từ PostgreSQL
const exportData = async () => {
  trainingSteps.value[0].active = true
  trainingStatus.value = 'Đang xuất dữ liệu từ PostgreSQL ra các file Rasa...'
  taskLogs.value = []
  
  try {
    const response = await RasaIntegrationService.exportData()
    currentTaskId.value = response.task_id
    trainingSteps.value[0].taskId = response.task_id
    
    // Đợi cho đến khi task hoàn thành
    pollingInterval.value = setInterval(async () => {
      const completed = await checkTaskStatus()
      if (completed) {
        clearInterval(pollingInterval.value)
        trainingSteps.value[0].done = true
        trainingSteps.value[0].active = false
        
        // Lưu task vào lịch sử
        if (currentTask.value) {
          taskHistory.value.push({...currentTask.value, step: 1})
        }
        
        // Chuyển sang bước tiếp theo
        trainModel()
      }
    }, 2000)
  } catch (error) {
    console.error('Error exporting data:', error)
    hasError.value = true
    trainingStatus.value = `Lỗi khi xuất dữ liệu: ${error.response?.data?.detail || error.message}`
    showNotification('danger', `Lỗi khi xuất dữ liệu: ${error.response?.data?.detail || error.message}`)
    isTraining.value = false
    trainingSteps.value[0].active = false
  }
}

// Bước 2: Huấn luyện mô hình Rasa
const trainModel = async () => {
  trainingSteps.value[1].active = true
  trainingStatus.value = 'Đang huấn luyện mô hình Rasa...'
  taskLogs.value = []
  
  try {
    const response = await RasaIntegrationService.trainModel()
    currentTaskId.value = response.task_id
    trainingSteps.value[1].taskId = response.task_id
    
    // Đợi cho đến khi task hoàn thành
    pollingInterval.value = setInterval(async () => {
      const completed = await checkTaskStatus()
      if (completed) {
        clearInterval(pollingInterval.value)
        trainingSteps.value[1].done = true
        trainingSteps.value[1].active = false
        
        // Lưu task vào lịch sử
        if (currentTask.value) {
          taskHistory.value.push({...currentTask.value, step: 2})
        }
        
        // Chuyển sang bước tiếp theo
        restartServer()
      }
    }, 2000)
  } catch (error) {
    console.error('Error training model:', error)
    hasError.value = true
    trainingStatus.value = `Lỗi khi huấn luyện mô hình: ${error.response?.data?.detail || error.message}`
    showNotification('danger', `Lỗi khi huấn luyện mô hình: ${error.response?.data?.detail || error.message}`)
    isTraining.value = false
    trainingSteps.value[1].active = false
  }
}

// Bước 3: Khởi động lại Rasa server
const restartServer = async () => {
  trainingSteps.value[2].active = true
  trainingStatus.value = 'Đang khởi động lại Rasa server...'
  taskLogs.value = []
  
  try {
    const response = await RasaIntegrationService.restartServer()
    currentTaskId.value = response.task_id
    trainingSteps.value[2].taskId = response.task_id
    
    // Đợi cho đến khi task hoàn thành
    pollingInterval.value = setInterval(async () => {
      const completed = await checkTaskStatus()
      if (completed) {
        clearInterval(pollingInterval.value)
        trainingSteps.value[2].done = true
        trainingSteps.value[2].active = false
        
        // Lưu task vào lịch sử
        if (currentTask.value) {
          taskHistory.value.push({...currentTask.value, step: 3})
        }
        
        // Hoàn thành
        isComplete.value = true
        trainingStatus.value = 'Đã hoàn thành huấn luyện mô hình!'
        showNotification('success', 'Đã hoàn thành huấn luyện mô hình Rasa!')
        isTraining.value = false
        
        // Lưu toàn bộ quá trình vào localStorage
        saveTrainingHistory()
      }
    }, 2000)
  } catch (error) {
    console.error('Error restarting server:', error)
    hasError.value = true
    trainingStatus.value = `Lỗi khi khởi động lại server: ${error.response?.data?.detail || error.message}`
    showNotification('danger', `Lỗi khi khởi động lại server: ${error.response?.data?.detail || error.message}`)
    isTraining.value = false
    trainingSteps.value[2].active = false
  }
}

// Lưu lịch sử huấn luyện vào localStorage
const saveTrainingHistory = () => {
  try {
    const history = JSON.parse(localStorage.getItem('rasaTrainingHistory') || '[]')
    history.push({
      id: Date.now(),
      timestamp: new Date().toISOString(),
      steps: trainingSteps.value.map(step => ({
        id: step.id,
        text: step.text,
        taskId: step.taskId,
        logs: step.logs
      })),
      successful: isComplete.value
    })
    localStorage.setItem('rasaTrainingHistory', JSON.stringify(history))
  } catch (error) {
    console.error('Error saving training history:', error)
  }
}

// Hàm bắt đầu quá trình huấn luyện
const handleTrainRasa = async () => {
  isTraining.value = true
  hasError.value = false
  isComplete.value = false
  showLogs.value = false
  taskLogs.value = []
  taskHistory.value = []
  currentTask.value = null
  
  // Reset training steps
  trainingSteps.value.forEach(step => {
    step.done = false
    step.active = false
    step.taskId = null
    step.logs = []
  })
  
  // Bắt đầu từ bước 1
  exportData()
}

// Hàm chuyển đổi hiển thị logs
const toggleLogs = () => {
  showLogs.value = !showLogs.value
}

// Hàm hiển thị logs của một bước cụ thể
const showStepLogs = (step) => {
  if (step.logs && step.logs.length > 0) {
    taskLogs.value = step.logs
    showLogs.value = true
  }
}

// Dọn dẹp khi component bị hủy
onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
})

// Khôi phục lịch sử huấn luyện từ localStorage khi component được tạo
const loadTrainingHistory = () => {
  try {
    const lastTraining = JSON.parse(localStorage.getItem('rasaTrainingHistory') || '[]').pop()
    if (lastTraining && lastTraining.successful) {
      isComplete.value = true
      trainingStatus.value = 'Đã hoàn thành huấn luyện mô hình!'
      
      // Khôi phục trạng thái các bước
      lastTraining.steps.forEach((historyStep, index) => {
        if (index < trainingSteps.value.length) {
          trainingSteps.value[index].done = true
          trainingSteps.value[index].logs = historyStep.logs || []
        }
      })
    }
  } catch (error) {
    console.error('Error loading training history:', error)
  }
}

loadTrainingHistory()
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
            <span v-if="isTraining && currentTask" class="text-sm ml-2 text-gray-500">
              ({{ formattedTime }})
            </span>
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
          
          <BaseButton
            v-if="step.logs && step.logs.length > 0"
            :icon="mdiConsole"
            color="info"
            small
            outline
            class="ml-2"
            @click="showStepLogs(step)"
          />
        </div>
      </div>
      
      <!-- Log Console -->
      <div class="mt-6">
        <div 
          class="flex items-center justify-between p-2 bg-gray-100 rounded-t cursor-pointer"
          @click="toggleLogs"
        >
          <div class="flex items-center">
            <BaseIcon :path="mdiConsole" class="text-gray-700" size="20" />
            <span class="ml-2 font-medium text-gray-700">Logs</span>
          </div>
          <BaseIcon 
            :path="showLogs ? mdiChevronUp : mdiChevronDown" 
            class="text-gray-700" 
            size="20" 
          />
        </div>
        
        <div 
          v-if="showLogs" 
          class="bg-gray-900 text-green-400 p-4 rounded-b font-mono text-sm overflow-auto"
          style="max-height: 300px; min-height: 100px;"
        >
          <div v-if="taskLogs.length === 0" class="text-gray-400">
            Chưa có logs nào được ghi lại...
          </div>
          <div v-else>
            <div v-for="(log, index) in taskLogs" :key="index" class="mb-1">
              <span v-if="log.startsWith('ERROR:')" class="text-red-400">{{ log }}</span>
              <span v-else>{{ log }}</span>
            </div>
          </div>
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
