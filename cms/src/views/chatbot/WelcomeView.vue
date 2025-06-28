<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { mdiRobotExcited, mdiArrowRight } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'

const router = useRouter()

const navigateToDashboard = () => {
  router.push({ name: 'chatbot-dashboard' })
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <div class="flex flex-col items-center justify-center min-h-[70vh]">
        <CardBox class="max-w-3xl w-full text-center">
          <div class="mb-6">
            <div class="flex justify-center mb-4">
              <svg-icon :path="mdiRobotExcited" class="text-blue-500" w="64" h="64" />
            </div>
            <h1 class="text-3xl font-bold mb-2">Chào mừng đến với Hệ thống Quản lý Chatbot</h1>
            <p class="text-gray-500 mb-6">
              Hệ thống quản lý chatbot tuyển sinh thạc sĩ UIT - Đại học Quốc gia TP.HCM
            </p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="font-bold mb-2">Quản lý Intent & Response</h3>
              <p class="text-sm text-gray-600 mb-4">
                Thêm, sửa, xóa các intent và response để dạy chatbot hiểu và trả lời các câu hỏi.
              </p>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="font-bold mb-2">Quản lý Mẫu câu NLU</h3>
              <p class="text-sm text-gray-600 mb-4">
                Thêm các mẫu câu để huấn luyện chatbot nhận diện ý định người dùng chính xác hơn.
              </p>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="font-bold mb-2">Tương tác với Chatbot</h3>
              <p class="text-sm text-gray-600 mb-4">
                Kiểm tra chatbot, huấn luyện mô hình và xem lịch sử tương tác.
              </p>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="font-bold mb-2">Tổng quan Hệ thống</h3>
              <p class="text-sm text-gray-600 mb-4">
                Xem thống kê và trạng thái của hệ thống chatbot.
              </p>
            </div>
          </div>
          
          <BaseButton
            label="Bắt đầu sử dụng"
            color="info"
            :icon="mdiArrowRight"
            @click="navigateToDashboard"
            class="px-8"
          />
        </CardBox>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>
