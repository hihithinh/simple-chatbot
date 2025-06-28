<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { mdiDatabase, mdiWeb, mdiLoading } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import NotificationBar from '@/components/NotificationBar.vue'
import DataSourceService from '@/services/data-source.service'

const router = useRouter()
const notification = ref(null)
const isLoading = ref(false)

const form = reactive({
  url: '',
  name: '',
  description: ''
})

const showNotification = (type, message) => {
  notification.value = { type, message }
  setTimeout(() => {
    notification.value = null
  }, 3000)
}

const handleSubmit = async () => {
  if (!form.url) {
    showNotification('danger', 'Vui lòng nhập URL')
    return
  }

  isLoading.value = true
  try {
    const response = await DataSourceService.crawlUrl(form.url, form.name, form.description)
    showNotification('success', 'Đã tải nội dung từ URL thành công!')
    
    console.log('Crawl response:', response)
    
    // Redirect to data source view page
    if (response && response.data && response.data.data_source && response.data.data_source.id) {
      router.push({
        name: 'chatbot-data-source-view',
        params: { id: response.data.data_source.id }
      })
    } else {
      console.error('Invalid response structure:', response)
      showNotification('danger', 'Lỗi định dạng phản hồi từ API')
    }
  } catch (error) {
    console.error('Error crawling URL:', error)
    showNotification('danger', `Lỗi khi tải nội dung: ${error.response?.data?.detail || error.message}`)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiWeb" title="Nhập liệu từ URL" main />

      <NotificationBar v-if="notification" :color="notification.type">
        {{ notification.message }}
      </NotificationBar>

      <CardBox class="mb-6" has-table>
        <form @submit.prevent="handleSubmit">
          <FormField label="URL" help="Nhập URL của trang web cần tải nội dung">
            <FormControl
              v-model="form.url"
              type="url"
              placeholder="https://example.com/thong-bao-tuyen-sinh"
              required
            />
          </FormField>

          <FormField label="Tên" help="Tên của nguồn dữ liệu (không bắt buộc)">
            <FormControl
              v-model="form.name"
              placeholder="Thông báo tuyển sinh đợt 1 2025"
            />
          </FormField>

          <FormField label="Mô tả" help="Mô tả ngắn về nguồn dữ liệu (không bắt buộc)">
            <FormControl
              v-model="form.description"
              type="textarea"
              placeholder="Thông tin về đợt tuyển sinh..."
            />
          </FormField>

          <div class="flex justify-end mt-6">
            <BaseButton
              type="submit"
              color="info"
              label="Bắt đầu"
              :icon="isLoading ? mdiLoading : mdiDatabase"
              :loading="isLoading"
              :disabled="isLoading"
            />
          </div>
        </form>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
