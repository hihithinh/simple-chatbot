<script setup>
import { ref } from 'vue'
import { mdiRobotExcited } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import TableResponses from '@/components/chatbot/TableResponses.vue'
import ResponseForm from '@/components/chatbot/ResponseForm.vue'
import ResponseService from '@/services/response.service'
import NotificationBar from '@/components/NotificationBar.vue'

const showForm = ref(false)
const isEdit = ref(false)
const currentResponse = ref(null)
const notification = ref(null)

const handleCreate = () => {
  currentResponse.value = {
    intent_id: null,
    text: '',
    is_active: true
  }
  isEdit.value = false
  showForm.value = true
}

const handleEdit = (response) => {
  currentResponse.value = { ...response }
  isEdit.value = true
  showForm.value = true
}

const handleView = (response) => {
  // Redirect to response detail page or show modal with details
  console.log('View response:', response)
}

const handleDelete = () => {
  showNotification('success', 'Response đã được xóa thành công')
}

const handleCancel = () => {
  showForm.value = false
  currentResponse.value = null
}

const handleSubmit = async (formData) => {
  try {
    if (isEdit.value) {
      await ResponseService.updateResponse(currentResponse.value.id, formData)
      showNotification('success', 'Response đã được cập nhật thành công')
    } else {
      await ResponseService.createResponse(formData)
      showNotification('success', 'Response mới đã được tạo thành công')
    }
    showForm.value = false
    currentResponse.value = null
  } catch (error) {
    console.error('Error submitting form:', error)
    showNotification('danger', 'Có lỗi xảy ra. Vui lòng thử lại!')
  }
}

const showNotification = (type, message) => {
  notification.value = { type, message }
  setTimeout(() => {
    notification.value = null
  }, 3000)
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiRobotExcited" title="Quản lý Response" main />
      
      <NotificationBar v-if="notification" :color="notification.type">
        {{ notification.message }}
      </NotificationBar>
      
      <CardBox v-if="showForm" class="mb-6" is-form>
        <ResponseForm 
          :response="currentResponse" 
          :is-edit="isEdit" 
          @submit="handleSubmit" 
          @cancel="handleCancel" 
        />
      </CardBox>
      
      <CardBox v-else class="mb-6" has-table>
        <TableResponses 
          @create="handleCreate" 
          @edit="handleEdit" 
          @view="handleView" 
          @delete="handleDelete" 
        />
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
