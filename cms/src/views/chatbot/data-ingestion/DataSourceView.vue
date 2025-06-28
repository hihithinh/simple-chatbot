<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiDatabase" title="Xem nguồn dữ liệu" main />

      <NotificationBar v-if="notification" :color="notification.type">
        {{ notification.message }}
      </NotificationBar>

      <template v-if="dataSource && crawledContent">
        <CardBox class="mb-6">
          <div class="space-y-4">
            <div>
              <h3 class="text-lg font-semibold">{{ dataSource.name }}</h3>
              <p class="text-gray-500">{{ dataSource.description }}</p>
            </div>

            <div>
              <h4 class="font-medium">URL:</h4>
              <a :href="dataSource.url" target="_blank" class="text-blue-500 hover:underline">
                {{ dataSource.url }}
              </a>
            </div>

            <div>
              <h4 class="font-medium">Nội dung đã crawl:</h4>
              <div class="mt-2 p-4 bg-gray-100 rounded-lg max-h-96 overflow-y-auto">
                <h5 class="font-semibold mb-2">{{ crawledContent.title }}</h5>
                <div v-html="crawledContent.content" class="formatted-content"></div>
              </div>
            </div>
          </div>
        </CardBox>

        <CardBox class="mb-6">
          <div class="mb-6">
            <h3 class="text-lg font-semibold mb-4">Tạo bộ câu hỏi QA</h3>
            <StepIndicator :steps="steps" :current-step="currentStep" />
          </div>

          <div v-if="currentStep === 0" class="mt-6">
            <KeyPointsExtractor
              :key-points="keyPoints"
              :is-loading="isLoading"
              @extract="handleExtractKeyPoints"
              @create-intents="handleCreateIntents"
              @update-key-points="updateKeyPoints"
            />
          </div>

          <div v-else-if="currentStep === 1" class="mt-6">
            <QAGenerator
              :intents="createdIntents"
              :is-loading="isLoading"
              v-model:selected-intents="selectedIntents"
              @generate-examples="handleGenerateNluExamples"
            />
          </div>

          <div v-else-if="currentStep === 2" class="mt-6">
            <RasaTrainer
              :is-loading="isLoading"
              @train="handleTrainRasa"
              @notification="showNotification"
            />
          </div>
        </CardBox>
      </template>

      <template v-else>
        <CardBox class="mb-6">
          <div class="text-center py-12">
            <p class="text-gray-500">Không tìm thấy nguồn dữ liệu</p>
          </div>
        </CardBox>
      </template>

      <div v-if="isLoading" class="flex justify-center items-center h-64">
        <BaseButton :icon="mdiLoading" color="info" label="Đang tải..." loading />
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { mdiDatabase, mdiRobotExcited, mdiLoading, mdiCheck, mdiChevronRight } from '@mdi/js'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import NotificationBar from '@/components/NotificationBar.vue'
import StepIndicator from '@/components/data-ingestion/StepIndicator.vue'
import KeyPointsExtractor from '@/components/data-ingestion/KeyPointsExtractor.vue'
import QAGenerator from '@/components/data-ingestion/QAGenerator.vue'
import RasaTrainer from '@/components/data-ingestion/RasaTrainer.vue'
import DataSourceService from '@/services/data-source.service'
import QAGeneratorService from '@/services/qa-generator.service'

const route = useRoute()
const notification = ref(null)
const isLoading = ref(false)
const dataSource = ref(null)
const crawledContent = ref(null)
const currentStep = ref(0)
const steps = ['Trích xuất thông tin chính', 'Tạo dữ liệu câu hỏi', 'Huấn luyện lại RASA']
const keyPoints = ref([])
const createdIntents = ref([])
const selectedIntents = ref([])

const dataSourceId = computed(() => Number(route.params.id))

// Giữ lại hàm showNotification cho các component con sử dụng
const showNotification = (type, message) => {
  if (typeof type === 'object' && type.type && type.message) {
    notification.value = type
  } else {
    notification.value = { type, message }
  }

  // Thêm hiển thị toast
  alert(message)
}

const updateKeyPoints = (updatedKeyPoints) => {
  keyPoints.value = updatedKeyPoints
}

const loadDataSource = async () => {
  isLoading.value = true
  try {
    console.log('Loading data source with ID:', dataSourceId.value)
    const response = await DataSourceService.getWithContent(dataSourceId.value)
    console.log('Data source response:', response)

    if (response && response.data) {
      dataSource.value = response.data.data_source
      crawledContent.value = response.data.crawled_content
      console.log('Data source loaded:', dataSource.value)
      console.log('Crawled content loaded:', crawledContent.value)
    } else {
      console.error('Invalid response structure:', response)
      alert('Lỗi định dạng phản hồi từ API')
    }
  } catch (error) {
    console.error('Error loading data source:', error)
    alert(error.userMessage || `Lỗi khi tải dữ liệu: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const handleExtractKeyPoints = async (previousPoints = []) => {
  isLoading.value = true
  try {
    // Gửi các điểm thông tin đã trích xuất trước đó để tránh trùng lặp
    const response = await QAGeneratorService.extractKeyPoints(dataSourceId.value, previousPoints)
    keyPoints.value = response.data
    alert(`Đã trích xuất ${keyPoints.value.length} điểm chính từ nội dung`)
  } catch (error) {
    console.error('Error extracting key points:', error)
    // Toast đã được hiển thị trong axios interceptor
  } finally {
    isLoading.value = false
  }
}

const handleCreateIntents = async () => {
  isLoading.value = true
  try {
    const response = await QAGeneratorService.createIntents(dataSourceId.value, keyPoints.value)
    createdIntents.value = response.data
    alert(`Đã tạo ${createdIntents.value.length} intent và response`)
    currentStep.value = 1
  } catch (error) {
    console.error('Error creating intents:', error)
    // Toast đã được hiển thị trong axios interceptor
  } finally {
    isLoading.value = false
  }
}

const handleGenerateNluExamples = async () => {
  if (selectedIntents.value.length === 0) {
    alert('Vui lòng chọn ít nhất một intent')
    return
  }

  isLoading.value = true
  try {
    for (const intentId of selectedIntents.value) {
      await QAGeneratorService.generateNluExamples(intentId)
    }
    alert(`Đã bắt đầu tạo câu hỏi cho ${selectedIntents.value.length} intent`)
    currentStep.value = 2
  } catch (error) {
    console.error('Error generating NLU examples:', error)
    // Toast đã được hiển thị trong axios interceptor
  } finally {
    isLoading.value = false
  }
}

const handleTrainRasa = async () => {
  alert('Đã hoàn thành quá trình nhập liệu')
}

onMounted(() => {
  loadDataSource()
})
</script>

<style>
.formatted-content {
  /* General styling */
  font-family: inherit;
  line-height: 1.5;

  /* Table styling */
  table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1rem;
  }

  table, th, td {
    border: 1px solid #e2e8f0;
  }

  th, td {
    padding: 0.5rem;
    text-align: left;
  }

  th {
    background-color: #f1f5f9;
    font-weight: 600;
  }

  /* List styling */
  ul, ol {
    padding-left: 1.5rem;
    margin-bottom: 1rem;
  }

  ul {
    list-style-type: disc;
  }

  ol {
    list-style-type: decimal;
  }

  /* Heading styling */
  h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
  }

  /* Link styling */
  a {
    color: #3b82f6;
    text-decoration: underline;
  }

  /* Image styling */
  img {
    max-width: 100%;
    height: auto;
    margin: 0.5rem 0;
  }

  /* Paragraph spacing */
  p {
    margin-bottom: 0.75rem;
  }
}
</style>
