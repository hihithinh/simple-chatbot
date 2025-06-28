<script setup>
import { ref, onMounted, computed } from 'vue'
import { mdiRobotExcited, mdiMessageText, mdiTextBox, mdiViewList, mdiChatProcessing } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import NotificationBar from '@/components/NotificationBar.vue'
import BaseLevel from '@/components/BaseLevel.vue'
import BaseButton from '@/components/BaseButton.vue'
import IntentService from '@/services/intent.service'
import ResponseService from '@/services/response.service'
import NluExampleService from '@/services/nlu-example.service'
import RasaIntegrationService from '@/services/rasa-integration.service'

const notification = ref(null)
const stats = ref({
  intents: 0,
  responses: 0,
  nluExamples: 0,
})
const isLoading = ref(true)
const rasaStatus = ref(null)

const fetchStats = async () => {
  isLoading.value = true
  
  try {
    // Fetch intents count
    const intentsResponse = await IntentService.getIntents()
    stats.value.intents = intentsResponse.data.length
    
    // Fetch responses count
    const responsesResponse = await ResponseService.getResponses()
    stats.value.responses = responsesResponse.data.length
    
    // Fetch NLU examples count
    const nluExamplesResponse = await NluExampleService.getNluExamples()
    stats.value.nluExamples = nluExamplesResponse.data.length
  } catch (error) {
    console.error('Error fetching stats:', error)
    showNotification('danger', 'Có lỗi xảy ra khi tải dữ liệu thống kê')
  } finally {
    isLoading.value = false
  }
}

const checkRasaStatus = async () => {
  try {
    const response = await RasaIntegrationService.checkHealth()
    rasaStatus.value = response.data.status === 'ok' ? 'online' : 'offline'
  } catch (error) {
    console.error('Error checking Rasa status:', error)
    rasaStatus.value = 'offline'
  }
}

const showNotification = (type, message) => {
  notification.value = { type, message }
  setTimeout(() => {
    notification.value = null
  }, 3000)
}

onMounted(() => {
  fetchStats()
  checkRasaStatus()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiRobotExcited" title="Tổng quan Chatbot" main />
      
      <NotificationBar v-if="notification" :color="notification.type">
        {{ notification.message }}
      </NotificationBar>
      
      <!-- Status Card -->
      <CardBox class="mb-6">
        <BaseLevel>
          <div>
            <h3 class="text-lg font-bold mb-2">Trạng thái hệ thống</h3>
            <div class="flex items-center">
              <span class="mr-2">Rasa Server:</span>
              <span 
                class="px-3 py-1 rounded-full text-sm"
                :class="rasaStatus === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
              >
                {{ rasaStatus === 'online' ? 'Online' : 'Offline' }}
              </span>
            </div>
          </div>
          <div>
            <BaseButton
              color="info"
              label="Làm mới"
              @click="fetchStats"
              :loading="isLoading"
            />
          </div>
        </BaseLevel>
      </CardBox>
      
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <!-- Intents Stats -->
        <CardBox>
          <BaseLevel>
            <div>
              <h3 class="text-lg font-bold">Intents</h3>
              <p class="text-3xl font-bold mt-2">{{ stats.intents }}</p>
            </div>
            <BaseButton
              :icon="mdiMessageText"
              color="info"
              :to="{ name: 'chatbot-intents' }"
              small
              rounded
            />
          </BaseLevel>
        </CardBox>
        
        <!-- Responses Stats -->
        <CardBox>
          <BaseLevel>
            <div>
              <h3 class="text-lg font-bold">Responses</h3>
              <p class="text-3xl font-bold mt-2">{{ stats.responses }}</p>
            </div>
            <BaseButton
              :icon="mdiTextBox"
              color="info"
              :to="{ name: 'chatbot-responses' }"
              small
              rounded
            />
          </BaseLevel>
        </CardBox>
        
        <!-- NLU Examples Stats -->
        <CardBox>
          <BaseLevel>
            <div>
              <h3 class="text-lg font-bold">Mẫu câu NLU</h3>
              <p class="text-3xl font-bold mt-2">{{ stats.nluExamples }}</p>
            </div>
            <BaseButton
              :icon="mdiViewList"
              color="info"
              :to="{ name: 'chatbot-nlu-examples' }"
              small
              rounded
            />
          </BaseLevel>
        </CardBox>
      </div>
      
      <!-- Quick Actions -->
      <CardBox title="Thao tác nhanh" class="mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <BaseButton
            label="Quản lý Intent"
            :icon="mdiMessageText"
            color="info"
            :to="{ name: 'chatbot-intents' }"
          />
          <BaseButton
            label="Quản lý Response"
            :icon="mdiTextBox"
            color="info"
            :to="{ name: 'chatbot-responses' }"
          />
          <BaseButton
            label="Quản lý Mẫu câu NLU"
            :icon="mdiViewList"
            color="info"
            :to="{ name: 'chatbot-nlu-examples' }"
          />
          <BaseButton
            label="Tương tác với Chatbot"
            :icon="mdiChatProcessing"
            color="success"
            :to="{ name: 'chatbot-interactions' }"
          />
        </div>
      </CardBox>
      
      <!-- Guide -->
      <CardBox title="Hướng dẫn sử dụng" class="mb-6">
        <div class="space-y-4">
          <p>
            <strong>Quản lý Intent:</strong> Thêm, sửa, xóa các intent trong hệ thống.
          </p>
          <p>
            <strong>Quản lý Response:</strong> Thêm, sửa, xóa các response tương ứng với intent.
          </p>
          <p>
            <strong>Quản lý Mẫu câu NLU:</strong> Thêm, sửa, xóa các mẫu câu huấn luyện cho NLU.
          </p>
          <p>
            <strong>Tương tác với Chatbot:</strong> Kiểm tra chatbot và xem lịch sử tương tác.
          </p>
          <p class="mt-4 text-sm text-gray-500">
            Sau khi thay đổi dữ liệu, bạn cần huấn luyện lại mô hình Rasa để cập nhật thay đổi.
            Bạn có thể huấn luyện lại mô hình trong trang "Tương tác với Chatbot".
          </p>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
