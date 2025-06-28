<script setup>
import { ref } from 'vue'
import { mdiRobotExcited } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import TableIntents from '@/components/chatbot/TableIntents.vue'
import IntentForm from '@/components/chatbot/IntentForm.vue'
import IntentService from '@/services/intent.service'
import NotificationBar from '@/components/NotificationBar.vue'

const showForm = ref(false)
const isEdit = ref(false)
const currentIntent = ref(null)
const notification = ref(null)

const handleCreate = () => {
  currentIntent.value = {
    name: '',
    description: '',
    is_active: true
  }
  isEdit.value = false
  showForm.value = true
}

const handleEdit = (intent) => {
  currentIntent.value = { ...intent }
  isEdit.value = true
  showForm.value = true
}

const handleView = (intent) => {
  // Redirect to intent detail page or show modal with details
  console.log('View intent:', intent)
}

const handleDelete = () => {
  showNotification('success', 'Intent đã được xóa thành công')
}

const handleCancel = () => {
  showForm.value = false
  currentIntent.value = null
}

const handleSubmit = async (formData) => {
  try {
    if (isEdit.value) {
      await IntentService.updateIntent(currentIntent.value.id, formData)
      showNotification('success', 'Intent đã được cập nhật thành công')
    } else {
      await IntentService.createIntent(formData)
      showNotification('success', 'Intent mới đã được tạo thành công')
    }
    showForm.value = false
    currentIntent.value = null
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
      <SectionTitleLineWithButton :icon="mdiRobotExcited" title="Quản lý Intent" main />
      
      <NotificationBar v-if="notification" :color="notification.type">
        {{ notification.message }}
      </NotificationBar>
      
      <CardBox v-if="showForm" class="mb-6" is-form>
        <IntentForm 
          :intent="currentIntent" 
          :is-edit="isEdit" 
          @submit="handleSubmit" 
          @cancel="handleCancel" 
        />
      </CardBox>
      
      <CardBox v-else class="mb-6" has-table>
        <TableIntents 
          @create="handleCreate" 
          @edit="handleEdit" 
          @view="handleView" 
          @delete="handleDelete" 
        />
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
