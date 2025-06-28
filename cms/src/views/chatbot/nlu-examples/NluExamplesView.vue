<script setup>
import { ref } from 'vue'
import { mdiRobotExcited } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import TableNluExamples from '@/components/chatbot/TableNluExamples.vue'
import NluExampleForm from '@/components/chatbot/NluExampleForm.vue'
import NluExampleService from '@/services/nlu-example.service'
import NotificationBar from '@/components/NotificationBar.vue'

const showForm = ref(false)
const isEdit = ref(false)
const currentNluExample = ref(null)
const notification = ref(null)

const handleCreate = () => {
  currentNluExample.value = {
    intent_id: null,
    text: ''
  }
  isEdit.value = false
  showForm.value = true
}

const handleEdit = (nluExample) => {
  currentNluExample.value = { ...nluExample }
  isEdit.value = true
  showForm.value = true
}

const handleView = (nluExample) => {
  // Redirect to nluExample detail page or show modal with details
  console.log('View NLU example:', nluExample)
}

const handleDelete = () => {
  showNotification('success', 'Mẫu câu đã được xóa thành công')
}

const handleCancel = () => {
  showForm.value = false
  currentNluExample.value = null
}

const handleSubmit = async (formData) => {
  try {
    if (isEdit.value) {
      await NluExampleService.updateNluExample(currentNluExample.value.id, formData)
      showNotification('success', 'Mẫu câu đã được cập nhật thành công')
    } else {
      await NluExampleService.createNluExample(formData)
      showNotification('success', 'Mẫu câu mới đã được tạo thành công')
    }
    showForm.value = false
    currentNluExample.value = null
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
      <SectionTitleLineWithButton :icon="mdiRobotExcited" title="Quản lý mẫu câu NLU" main />
      
      <NotificationBar v-if="notification" :color="notification.type">
        {{ notification.message }}
      </NotificationBar>
      
      <CardBox v-if="showForm" class="mb-6" is-form>
        <NluExampleForm 
          :nlu-example="currentNluExample" 
          :is-edit="isEdit" 
          @submit="handleSubmit" 
          @cancel="handleCancel" 
        />
      </CardBox>
      
      <CardBox v-else class="mb-6" has-table>
        <TableNluExamples 
          @create="handleCreate" 
          @edit="handleEdit" 
          @view="handleView" 
          @delete="handleDelete" 
        />
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
