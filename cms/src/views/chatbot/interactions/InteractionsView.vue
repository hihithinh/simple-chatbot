<script setup>
import { ref, onMounted } from 'vue'
import { mdiRobotExcited, mdiHistory, mdiRefresh } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import ChatInterface from '@/components/chatbot/ChatInterface.vue'
import ChatbotInteractionService from '@/services/chatbot-interaction.service'
import RasaIntegrationService from '@/services/rasa-integration.service'
import NotificationBar from '@/components/NotificationBar.vue'

const notification = ref(null)
const chatRef = ref(null)
const isTraining = ref(false)
const rasaStatus = ref(null)

const checkRasaStatus = async () => {
  try {
    const response = await RasaIntegrationService.checkHealth()
    rasaStatus.value = response.data.status === 'ok' ? 'online' : 'offline'
    if (rasaStatus.value === 'online') {
      showNotification('success', 'Rasa server is online')
    } else {
      showNotification('danger', 'Rasa server is offline or unreachable')
    }
  } catch (error) {
    console.error('Error checking Rasa status:', error)
    rasaStatus.value = 'offline'
    showNotification('danger', 'Rasa server is offline or unreachable')
  }
}

const trainRasaModel = async () => {
  isTraining.value = true
  showNotification('info', 'Đang huấn luyện mô hình Rasa...')

  try {
    await RasaIntegrationService.trainModel()
    showNotification('success', 'Huấn luyện mô hình thành công!')
  } catch (error) {
    console.error('Error training Rasa model:', error)
    showNotification('danger', 'Có lỗi xảy ra khi huấn luyện mô hình')
  } finally {
    isTraining.value = false
  }
}

const clearChatHistory = async () => {
  try {
    await ChatbotInteractionService.clearInteractions()
    showNotification('success', 'Lịch sử chat đã được xóa')
    // Refresh chat interface
    if (chatRef.value) {
      // This assumes we add a refresh method to the ChatInterface component
      // We'll need to implement this method
    }
  } catch (error) {
    console.error('Error clearing chat history:', error)
    showNotification('danger', 'Có lỗi xảy ra khi xóa lịch sử chat')
  }
}

const showNotification = (type, message) => {
  notification.value = { type, message }
  setTimeout(() => {
    notification.value = null
  }, 3000)
}

onMounted(() => {
  checkRasaStatus()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiRobotExcited" title="Tương tác với Chatbot" main />

      <NotificationBar v-if="notification" :color="notification.type">
        {{ notification.message }}
      </NotificationBar>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-8">
          <CardBox class="h-[600px] flex flex-col">
            <ChatInterface ref="chatRef" />
          </CardBox>
        </div>

        <div class="lg:col-span-4">
          <CardBox title="Quản lý Chatbot" class="mb-6">
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span>Trạng thái Rasa:</span>
                <span
                  class="px-3 py-1 rounded-full text-sm"
                  :class="rasaStatus === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ rasaStatus === 'online' ? 'Online' : 'Offline' }}
                </span>
              </div>

              <BaseButtons>
                <BaseButton
                  color="info"
                  :icon="mdiRefresh"
                  label="Kiểm tra kết nối"
                  @click="checkRasaStatus"
                />
              </BaseButtons>

              <BaseButtons>
                <BaseButton
                  color="success"
                  label="Huấn luyện mô hình"
                  :loading="isTraining"
                  :disabled="isTraining || rasaStatus !== 'online'"
                  @click="trainRasaModel"
                />
              </BaseButtons>

              <BaseButtons>
                <BaseButton
                  color="danger"
                  :icon="mdiHistory"
                  label="Xóa lịch sử chat"
                  @click="clearChatHistory"
                />
              </BaseButtons>
            </div>
          </CardBox>

          <CardBox title="Thông tin" class="mb-6">
            <div class="space-y-2">
              <p>
                Sử dụng giao diện chat để tương tác với chatbot và kiểm tra các intent, response đã được cấu hình.
              </p>
              <p>
                Sau khi thay đổi intent, response hoặc mẫu câu, bạn cần huấn luyện lại mô hình để cập nhật thay đổi.
              </p>
            </div>
          </CardBox>
        </div>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>
