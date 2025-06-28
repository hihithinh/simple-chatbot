<script setup>
import { mdiCheck } from '@mdi/js'
import BaseIcon from '@/components/BaseIcon.vue'

const props = defineProps({
  steps: {
    type: Array,
    required: true
  },
  currentStep: {
    type: Number,
    default: 0
  }
})
</script>

<template>
  <div class="flex items-center w-full">
    <template v-for="(step, index) in props.steps" :key="index">
      <!-- Step circle -->
      <div 
        class="flex items-center justify-center w-8 h-8 rounded-full"
        :class="[
          index < props.currentStep 
            ? 'bg-green-500 text-white' 
            : index === props.currentStep 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-200 text-gray-600'
        ]"
      >
        <template v-if="index < props.currentStep">
          <BaseIcon :path="mdiCheck" size="16" />
        </template>
        <template v-else>
          {{ index + 1 }}
        </template>
      </div>
      
      <!-- Step name -->
      <div class="ml-2">
        <span 
          class="text-sm font-medium"
          :class="[
            index <= props.currentStep ? 'text-gray-900' : 'text-gray-500'
          ]"
        >
          {{ step }}
        </span>
      </div>
      
      <!-- Connector line -->
      <div 
        v-if="index < props.steps.length - 1" 
        class="flex-grow mx-4 h-0.5" 
        :class="[
          index < props.currentStep ? 'bg-green-500' : 'bg-gray-200'
        ]"
      ></div>
    </template>
  </div>
</template>
