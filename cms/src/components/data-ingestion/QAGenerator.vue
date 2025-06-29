<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { mdiRobotExcited, mdiLoading, mdiCheckboxMarked, mdiCheckboxBlankOutline, mdiSchool } from '@mdi/js'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import CardBox from '@/components/CardBox.vue'
import CardBoxComponentTitle from '@/components/CardBoxComponentTitle.vue'
import QAGeneratorService from '@/services/qa-generator.service'
import IntentService from '@/services/intent.service'
import NluExampleService from '@/services/nlu-example.service'

const props = defineProps({
  intents: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  selectedIntents: {
    type: Array,
    default: () => []
  },
  dataSourceId: {
    type: Number,
    required: true
  },
  nluExamplesByIntent: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:selectedIntents', 'generate-examples', 'start-training'])

const intentExamples = ref({})
const loadingIntents = ref({})
const loadedIntents = ref([])
const localNluExamplesByIntent = ref({})
const isLoadingData = ref(false)
const hasExistingData = ref(false)

// Combine props.nluExamplesByIntent and localNluExamplesByIntent
const combinedNluExamples = computed(() => {
  const combined = { ...localNluExamplesByIntent.value }
  
  // Add examples from props
  Object.keys(props.nluExamplesByIntent).forEach(intentId => {
    if (props.nluExamplesByIntent[intentId] && props.nluExamplesByIntent[intentId].length > 0) {
      combined[intentId] = props.nluExamplesByIntent[intentId]
    }
  })
  
  console.log('Combined NLU examples:', combined)
  return combined
})

const allSelected = computed(() => {
  const intentsToUse = props.intents.length > 0 ? props.intents : loadedIntents.value
  return intentsToUse.length > 0 && props.selectedIntents.length === intentsToUse.length
})

const allIntentsHaveExamples = computed(() => {
  const intentsToUse = props.intents.length > 0 ? props.intents : loadedIntents.value
  if (intentsToUse.length === 0) return false
  
  return intentsToUse.every(intent => {
    // Kiểm tra xem intent có examples không
    return (
      (intentExamples.value[intent.intent_id] && intentExamples.value[intent.intent_id].length > 0) ||
      (combinedNluExamples.value[intent.intent_id] && combinedNluExamples.value[intent.intent_id].length > 0)
    )
  })
})

const toggleSelectAll = () => {
  if (allSelected.value) {
    emit('update:selectedIntents', [])
  } else {
    const intentsToUse = props.intents.length > 0 ? props.intents : loadedIntents.value
    const allIntentIds = intentsToUse.map(intent => intent.intent_id)
    emit('update:selectedIntents', allIntentIds)
  }
}

const toggleIntent = (intentId) => {
  const selectedIntents = [...props.selectedIntents]
  const index = selectedIntents.indexOf(intentId)
  
  if (index === -1) {
    selectedIntents.push(intentId)
  } else {
    selectedIntents.splice(index, 1)
  }
  
  emit('update:selectedIntents', selectedIntents)
}

const isSelected = (intentId) => {
  return props.selectedIntents.includes(intentId)
}

const handleGenerateExamples = async (intentId) => {
  loadingIntents.value[intentId] = true
  
  try {
    const response = await QAGeneratorService.generateNluExamples(intentId)
    intentExamples.value[intentId] = response.data
  } catch (error) {
    console.error(`Error generating examples for intent ${intentId}:`, error)
  } finally {
    loadingIntents.value[intentId] = false
  }
}

const handleGenerateAllExamples = () => {
  emit('generate-examples')
}

const handleStartTraining = () => {
  emit('start-training')
}

const loadIntentsAndExamples = async () => {
  isLoadingData.value = true
  try {
    // Load intents if not provided by parent
    if (props.intents.length === 0) {
      const intentsResponse = await QAGeneratorService.getIntentsForDataSource(props.dataSourceId)
      
      if (intentsResponse && intentsResponse.data) {
        loadedIntents.value = intentsResponse.data
        
        // Nếu có intents, load nlu examples cho mỗi intent
        if (loadedIntents.value.length > 0) {
          hasExistingData.value = true
          
          // Load NLU examples cho mỗi intent
          for (const intent of loadedIntents.value) {
            const examplesResponse = await NluExampleService.getNluExamples({
              intent_id: intent.intent_id,
              limit: 10,
              skip: 0
            })
            
            // Kiểm tra cấu trúc phản hồi
            if (examplesResponse && Array.isArray(examplesResponse.data)) {
              // API trả về mảng trực tiếp
              localNluExamplesByIntent.value[intent.intent_id] = examplesResponse.data.map(item => item.text)
            } else if (examplesResponse && examplesResponse.data && examplesResponse.data.items) {
              // API trả về cấu trúc { data: { items: [...] } }
              localNluExamplesByIntent.value[intent.intent_id] = examplesResponse.data.items.map(item => item.text)
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Error loading intents and examples:', error)
  } finally {
    isLoadingData.value = false
  }
}

// Watch for changes in intents prop to reset examples
watch(() => props.intents, () => {
  intentExamples.value = {}
  loadingIntents.value = {}
}, { deep: true })

// Load intents and examples when component is mounted
onMounted(() => {
  loadIntentsAndExamples()
})
</script>

<template>
  <div>
    <CardBoxComponentTitle title="Bước 2: Tạo dữ liệu câu hỏi" />
    
    <p class="text-gray-600 mb-4">
      Chọn các intent bạn muốn tạo câu hỏi huấn luyện NLU cho RASA.
      Mỗi intent sẽ được tạo 5 câu hỏi mẫu.
    </p>
    
    <div v-if="isLoadingData || props.isLoading" class="flex justify-center my-8">
      <BaseIcon :path="mdiLoading" size="36" class="text-blue-500 animate-spin" />
      <span class="ml-2">Đang tải dữ liệu...</span>
    </div>
    
    <template v-else>
      <div class="mb-4 flex justify-between items-center">
        <div class="flex items-center cursor-pointer" @click="toggleSelectAll">
          <BaseIcon
            :path="allSelected ? mdiCheckboxMarked : mdiCheckboxBlankOutline"
            size="24"
            class="text-blue-500"
          />
          <span class="ml-2">{{ allSelected ? 'Bỏ chọn tất cả' : 'Chọn tất cả' }}</span>
        </div>
        
        <div class="flex gap-2">
          <BaseButton
            v-if="allIntentsHaveExamples"
            :icon="mdiSchool"
            color="success"
            label="Bắt đầu huấn luyện mô hình"
            @click="handleStartTraining"
          />
          
          <BaseButton
            :icon="props.isLoading ? mdiLoading : mdiRobotExcited"
            color="info"
            label="Tạo câu hỏi cho các intent đã chọn"
            :loading="props.isLoading"
            :disabled="props.isLoading || props.selectedIntents.length === 0"
            @click="handleGenerateAllExamples"
          />
        </div>
      </div>
      
      <div class="space-y-4 max-h-96 overflow-y-auto">
        <!-- Hiển thị intents từ props nếu có -->
        <template v-if="props.intents.length > 0">
          <CardBox v-for="intent in props.intents" :key="intent.intent_id" class="mb-2">
            <div class="space-y-2">
              <div class="flex justify-between items-center">
                <div 
                  class="flex items-center cursor-pointer" 
                  @click="toggleIntent(intent.intent_id)"
                >
                  <BaseIcon
                    :path="isSelected(intent.intent_id) ? mdiCheckboxMarked : mdiCheckboxBlankOutline"
                    size="24"
                    class="text-blue-500"
                  />
                  <h5 class="ml-2 font-semibold">{{ intent.intent_name }}</h5>
                </div>
                
                <BaseButton
                  :icon="loadingIntents[intent.intent_id] ? mdiLoading : mdiRobotExcited"
                  color="info"
                  small
                  label="Xem câu hỏi mẫu"
                  :loading="loadingIntents[intent.intent_id]"
                  :disabled="loadingIntents[intent.intent_id]"
                  @click="handleGenerateExamples(intent.intent_id)"
                  v-if="!intentExamples[intent.intent_id]"
                />
              </div>
              
              <div class="bg-gray-50 p-3 rounded">
                <p class="text-gray-700">{{ intent.response_text }}</p>
              </div>
              
              <div v-if="intentExamples[intent.intent_id]" class="mt-4">
                <h6 class="font-medium text-sm mb-2">Câu hỏi mẫu:</h6>
                <ul class="list-disc list-inside space-y-1 pl-2">
                  <li v-for="(example, index) in intentExamples[intent.intent_id]" :key="index" class="text-gray-700">
                    {{ example }}
                  </li>
                </ul>
              </div>
              <div v-else-if="combinedNluExamples[intent.intent_id]" class="mt-4">
                <h6 class="font-medium text-sm mb-2">Câu hỏi mẫu:</h6>
                <ul class="list-disc list-inside space-y-1 pl-2">
                  <li v-for="(example, index) in combinedNluExamples[intent.intent_id]" :key="index" class="text-gray-700">
                    {{ example }}
                  </li>
                </ul>
              </div>
              <div v-else class="mt-4 p-3 bg-yellow-50 text-yellow-700 rounded">
                <p>Chưa có bộ câu hỏi mẫu, hãy chọn item và nhấp "tạo câu hỏi cho các intent đã chọn" để generate</p>
              </div>
            </div>
          </CardBox>
        </template>
        
        <!-- Hiển thị intents đã load nếu không có intents từ props -->
        <template v-else-if="loadedIntents.length > 0">
          <CardBox v-for="intent in loadedIntents" :key="intent.intent_id" class="mb-2">
            <div class="space-y-2">
              <div class="flex justify-between items-center">
                <div 
                  class="flex items-center cursor-pointer" 
                  @click="toggleIntent(intent.intent_id)"
                >
                  <BaseIcon
                    :path="isSelected(intent.intent_id) ? mdiCheckboxMarked : mdiCheckboxBlankOutline"
                    size="24"
                    class="text-blue-500"
                  />
                  <h5 class="ml-2 font-semibold">{{ intent.intent_name }}</h5>
                </div>
              </div>
              
              <div class="bg-gray-50 p-3 rounded">
                <p class="text-gray-700">{{ intent.response_text }}</p>
              </div>
              
              <div v-if="intentExamples[intent.intent_id]" class="mt-4">
                <h6 class="font-medium text-sm mb-2">Câu hỏi mẫu:</h6>
                <ul class="list-disc list-inside space-y-1 pl-2">
                  <li v-for="(example, index) in intentExamples[intent.intent_id]" :key="index" class="text-gray-700">
                    {{ example }}
                  </li>
                </ul>
              </div>
              <div v-else-if="combinedNluExamples[intent.intent_id]" class="mt-4">
                <h6 class="font-medium text-sm mb-2">Câu hỏi mẫu:</h6>
                <ul class="list-disc list-inside space-y-1 pl-2">
                  <li v-for="(example, index) in combinedNluExamples[intent.intent_id]" :key="index" class="text-gray-700">
                    {{ example }}
                  </li>
                </ul>
              </div>
              <div v-else class="mt-4 p-3 bg-yellow-50 text-yellow-700 rounded">
                <p>Chưa có bộ câu hỏi mẫu, hãy chọn item và nhấp "tạo câu hỏi cho các intent đã chọn" để generate</p>
              </div>
            </div>
          </CardBox>
        </template>
        
        <div v-else class="text-center py-8">
          <p class="text-gray-500">Không có intent nào. Hãy tạo intent từ bước 1.</p>
        </div>
      </div>
    </template>
  </div>
</template>
