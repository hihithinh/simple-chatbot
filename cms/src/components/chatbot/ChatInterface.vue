<script setup>
import { ref, onMounted, computed } from 'vue'
import { mdiSend, mdiRobotExcited, mdiAccountCircle } from '@mdi/js'
import BaseButton from '@/components/BaseButton.vue'
import FormControl from '@/components/FormControl.vue'
import ChatbotInteractionService from '@/services/chatbot-interaction.service'
import RasaIntegrationService from '@/services/rasa-integration.service'

const props = defineProps({
  showHistory: {
    type: Boolean,
    default: true
  }
})

const messages = ref([])
const newMessage = ref('')
const isLoading = ref(false)
const botTyping = ref(false)
const rasaStatus = ref(null)

const userMessage = (text) => ({
  id: Date.now(),
  text,
  sender: 'user',
  timestamp: new Date().toISOString()
})

const botMessage = (text, intent = null) => ({
  id: Date.now(),
  text,
  sender: 'bot',
  intent,
  timestamp: new Date().toISOString()
})

const sendMessage = async () => {
  if (!newMessage.value.trim() || isLoading.value) return
  
  const messageText = newMessage.value.trim()
  newMessage.value = ''
  
  // Add user message to chat
  messages.value.push(userMessage(messageText))
  
  // Show bot typing indicator
  botTyping.value = true
  
  try {
    // Send message to Rasa
    const response = await RasaIntegrationService.sendMessage(messageText)
    
    // Add bot response to chat
    if (response && response.data) {
      // Small delay to simulate typing
      setTimeout(() => {
        botTyping.value = false
        
        if (response.data.text) {
          messages.value.push(botMessage(response.data.text, response.data.intent))
        } else {
          messages.value.push(botMessage('Sorry, I could not understand that.'))
        }
      }, 500)
    } else {
      botTyping.value = false
      messages.value.push(botMessage('Sorry, there was an error processing your request.'))
    }
  } catch (error) {
    console.error('Error sending message:', error)
    botTyping.value = false
    messages.value.push(botMessage('Sorry, there was an error connecting to the chatbot service.'))
  }
}

const checkRasaStatus = async () => {
  try {
    const response = await RasaIntegrationService.checkHealth()
    rasaStatus.value = response.data.status === 'ok' ? 'online' : 'offline'
  } catch (error) {
    console.error('Error checking Rasa status:', error)
    rasaStatus.value = 'offline'
  }
}

const fetchChatHistory = async () => {
  if (!props.showHistory) return
  
  isLoading.value = true
  try {
    const response = await ChatbotInteractionService.getInteractions()
    
    if (response && response.data) {
      // Format history into messages
      const history = response.data.map(item => {
        if (item.sender === 'user') {
          return userMessage(item.message)
        } else {
          return botMessage(item.response, item.intent)
        }
      })
      
      messages.value = history
    }
  } catch (error) {
    console.error('Error fetching chat history:', error)
  } finally {
    isLoading.value = false
  }
}

const statusColor = computed(() => {
  if (rasaStatus.value === 'online') return 'bg-green-500'
  if (rasaStatus.value === 'offline') return 'bg-red-500'
  return 'bg-gray-500'
})

onMounted(() => {
  checkRasaStatus()
  fetchChatHistory()
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b">
      <div class="flex items-center">
        <BaseButton :icon="mdiRobotExcited" color="info" small rounded />
        <span class="ml-2 font-bold">Chatbot</span>
      </div>
      <div class="flex items-center">
        <span class="text-sm mr-2">Status:</span>
        <span 
          class="w-3 h-3 rounded-full" 
          :class="statusColor"
        ></span>
        <span class="ml-1 text-sm">{{ rasaStatus || 'checking...' }}</span>
      </div>
    </div>
    
    <!-- Chat Messages -->
    <div class="flex-grow overflow-y-auto p-4 space-y-4">
      <div v-if="isLoading" class="text-center py-4">
        <span>Loading chat history...</span>
      </div>
      
      <div v-else-if="messages.length === 0" class="text-center py-4">
        <span>No messages yet. Start a conversation!</span>
      </div>
      
      <template v-else>
        <div 
          v-for="message in messages" 
          :key="message.id"
          :class="[
            'flex', 
            message.sender === 'user' ? 'justify-end' : 'justify-start'
          ]"
        >
          <div 
            :class="[
              'max-w-3/4 rounded-lg p-3', 
              message.sender === 'user' 
                ? 'bg-blue-500 text-white rounded-br-none' 
                : 'bg-gray-200 text-gray-800 rounded-bl-none'
            ]"
          >
            <div class="flex items-center mb-1">
              <BaseButton 
                :icon="message.sender === 'user' ? mdiAccountCircle : mdiRobotExcited" 
                :color="message.sender === 'user' ? 'white' : 'info'"
                small 
                rounded 
              />
              <span class="ml-2 font-bold text-sm">
                {{ message.sender === 'user' ? 'You' : 'Bot' }}
              </span>
              <span v-if="message.intent" class="ml-2 text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded-full">
                {{ message.intent }}
              </span>
            </div>
            <p>{{ message.text }}</p>
            <div class="text-right text-xs opacity-70 mt-1">
              {{ new Date(message.timestamp).toLocaleTimeString() }}
            </div>
          </div>
        </div>
        
        <div v-if="botTyping" class="flex justify-start">
          <div class="bg-gray-200 text-gray-800 rounded-lg rounded-bl-none p-3">
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
          </div>
        </div>
      </template>
    </div>
    
    <!-- Input Area -->
    <div class="p-4 border-t">
      <div class="flex">
        <FormControl
          v-model="newMessage"
          placeholder="Type a message..."
          :disabled="isLoading"
          @keyup.enter="sendMessage"
        />
        <BaseButton
          :icon="mdiSend"
          color="info"
          class="ml-2"
          :disabled="!newMessage.trim() || isLoading"
          @click="sendMessage"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.max-w-3\/4 {
  max-width: 75%;
}
</style>
