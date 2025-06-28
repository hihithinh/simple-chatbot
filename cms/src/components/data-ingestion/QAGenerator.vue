<script setup>
import { ref, computed, watch } from 'vue'
import { mdiRobotExcited, mdiLoading, mdiCheckboxMarked, mdiCheckboxBlankOutline } from '@mdi/js'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import CardBox from '@/components/CardBox.vue'
import CardBoxComponentTitle from '@/components/CardBoxComponentTitle.vue'
import QAGeneratorService from '@/services/qa-generator.service'

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
  }
})

const emit = defineEmits(['update:selectedIntents', 'generate-examples'])

const intentExamples = ref({})
const loadingIntents = ref({})

const allSelected = computed(() => {
  return props.intents.length > 0 && props.selectedIntents.length === props.intents.length
})

const toggleSelectAll = () => {
  if (allSelected.value) {
    emit('update:selectedIntents', [])
  } else {
    const allIntentIds = props.intents.map(intent => intent.intent_id)
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

// Watch for changes in intents prop to reset examples
watch(() => props.intents, () => {
  intentExamples.value = {}
  loadingIntents.value = {}
}, { deep: true })
</script>

<template>
  <div>
    <CardBoxComponentTitle title="Bước 2: Tạo dữ liệu câu hỏi" />
    
    <p class="text-gray-600 mb-4">
      Chọn các intent bạn muốn tạo câu hỏi huấn luyện NLU cho RASA.
      Mỗi intent sẽ được tạo 5 câu hỏi mẫu.
    </p>
    
    <div class="mb-4 flex justify-between items-center">
      <div class="flex items-center cursor-pointer" @click="toggleSelectAll">
        <BaseIcon
          :path="allSelected ? mdiCheckboxMarked : mdiCheckboxBlankOutline"
          size="24"
          class="text-blue-500"
        />
        <span class="ml-2">{{ allSelected ? 'Bỏ chọn tất cả' : 'Chọn tất cả' }}</span>
      </div>
      
      <BaseButton
        :icon="props.isLoading ? mdiLoading : mdiRobotExcited"
        color="success"
        label="Tạo câu hỏi cho các intent đã chọn"
        :loading="props.isLoading"
        :disabled="props.isLoading || props.selectedIntents.length === 0"
        @click="handleGenerateAllExamples"
      />
    </div>
    
    <div class="space-y-4 max-h-96 overflow-y-auto">
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
        </div>
      </CardBox>
    </div>
  </div>
</template>
