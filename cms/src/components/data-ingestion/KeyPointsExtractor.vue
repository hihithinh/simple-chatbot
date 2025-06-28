<script setup>
import { ref, computed, watch } from 'vue'
import { mdiMagnify, mdiLoading, mdiContentSave, mdiPlus, mdiDelete, mdiRefresh } from '@mdi/js'
import BaseButton from '@/components/BaseButton.vue'
import CardBox from '@/components/CardBox.vue'
import CardBoxComponentTitle from '@/components/CardBoxComponentTitle.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseIcon from '@/components/BaseIcon.vue'

const props = defineProps({
  keyPoints: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['extract', 'create-intents', 'update-key-points'])

const hasKeyPoints = computed(() => props.keyPoints.length > 0)
const editableKeyPoints = ref([])

// Initialize editableKeyPoints whenever props.keyPoints changes
const initEditableKeyPoints = () => {
  editableKeyPoints.value = props.keyPoints.map(point => ({
    ...point,
    isEditing: false
  }))
}

// Watch for changes in props.keyPoints
watch(() => props.keyPoints, () => {
  initEditableKeyPoints()
}, { immediate: true, deep: true })

const handleExtract = () => {
  // Nếu đã có key points, gửi chúng lên để tránh trích xuất trùng lặp
  if (editableKeyPoints.value.length > 0) {
    emit('extract', editableKeyPoints.value.map(point => ({
      title: point.title,
      code: point.code,
      content: point.content
    })))
  } else {
    emit('extract')
  }
}

const handleCreateIntents = () => {
  // Emit the updated key points before creating intents
  emit('update-key-points', editableKeyPoints.value.map(point => ({
    title: point.title,
    code: point.code,
    content: point.content
  })))
  emit('create-intents')
}

const toggleEdit = (index) => {
  editableKeyPoints.value[index].isEditing = !editableKeyPoints.value[index].isEditing
}

const addNewKeyPoint = () => {
  editableKeyPoints.value.push({
    title: 'Tiêu đề mới',
    code: `new_key_point_${Date.now()}`,
    content: 'Nội dung mới',
    isEditing: true
  })
}

const deleteKeyPoint = (index) => {
  editableKeyPoints.value.splice(index, 1)
  // Update parent component with the changes
  emit('update-key-points', editableKeyPoints.value.map(point => ({
    title: point.title,
    code: point.code,
    content: point.content
  })))
}
</script>

<template>
  <div>
    <CardBoxComponentTitle title="Bước 1: Trích xuất thông tin chính" />

    <p class="text-gray-600 mb-4">
      Hệ thống sẽ sử dụng AI để phân tích nội dung và trích xuất các điểm thông tin chính.
      Mỗi điểm thông tin sẽ được chuyển thành một intent và response trong chatbot.
    </p>

    <div v-if="!hasKeyPoints" class="flex justify-center mt-6">
      <BaseButton
        :icon="props.isLoading ? mdiLoading : mdiMagnify"
        color="info"
        label="Bắt đầu trích xuất thông tin"
        :loading="props.isLoading"
        :disabled="props.isLoading"
        @click="handleExtract"
      />
    </div>

    <div v-else>
      <div class="mb-4 flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <h4 class="font-medium">Đã trích xuất {{ editableKeyPoints.length }} điểm thông tin:</h4>
          <BaseButton
            :icon="mdiRefresh"
            color="info"
            label="Trích xuất thêm thông tin"
            :loading="props.isLoading"
            :disabled="props.isLoading"
            small
            @click="handleExtract"
          />
        </div>
        <div class="flex space-x-2">
          <BaseButton
            :icon="mdiPlus"
            color="info"
            label="Thêm mới"
            small
            @click="addNewKeyPoint"
          />
          <BaseButton
            :icon="props.isLoading ? mdiLoading : mdiContentSave"
            color="success"
            label="Tạo intent và response"
            :loading="props.isLoading"
            :disabled="props.isLoading"
            @click="handleCreateIntents"
          />
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200">
          <thead>
            <tr>
              <th class="px-4 py-2 border-b border-gray-200 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tiêu đề
              </th>
              <th class="px-4 py-2 border-b border-gray-200 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Mã
              </th>
              <th class="px-4 py-2 border-b border-gray-200 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nội dung
              </th>
              <th class="px-4 py-2 border-b border-gray-200 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Thao tác
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(point, index) in editableKeyPoints" :key="index" class="hover:bg-gray-50">
              <td class="px-4 py-2 border-b border-gray-200">
                <input
                  v-if="point.isEditing"
                  v-model="point.title"
                  class="w-full px-2 py-1 border border-gray-300 rounded"
                />
                <span v-else>{{ point.title }}</span>
              </td>
              <td class="px-4 py-2 border-b border-gray-200" style="word-break: break-all">
                <input
                  v-if="point.isEditing"
                  v-model="point.code"
                  class="w-full px-2 py-1 border border-gray-300 rounded"
                />
                <span v-else class="text-xs text-gray-500">{{ point.code }}</span>
              </td>
              <td class="px-4 py-2 border-b border-gray-200">
                <textarea
                  v-if="point.isEditing"
                  v-model="point.content"
                  class="w-full px-2 py-1 border border-gray-300 rounded"
                  rows="3"
                ></textarea>
                <span v-else>{{ point.content }}</span>
              </td>
              <td class="px-4 py-2 border-b border-gray-200 whitespace-nowrap">
                <div class="flex space-x-2">
                  <button
                    @click="toggleEdit(index)"
                    class="px-2 py-1 text-xs font-medium rounded"
                    :class="point.isEditing ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'"
                  >
                    {{ point.isEditing ? 'Lưu' : 'Sửa' }}
                  </button>
                  <button
                    @click="deleteKeyPoint(index)"
                    class="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded"
                  >
                    Xóa
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overflow-x-auto {
  max-height: 500px;
  overflow-y: auto;
}
</style>
