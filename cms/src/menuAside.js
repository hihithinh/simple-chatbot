import {
  mdiRobotExcited,
  mdiMessageText,
  mdiTextBox,
  mdiViewList,
  mdiChatProcessing,
  mdiViewDashboard,
  mdiHome,
  mdiWeb,
} from '@mdi/js'

export default [
  {
    to: '/chatbot/welcome',
    icon: mdiHome,
    label: 'Trang chủ',
  },
  {
    to: '/chatbot/dashboard',
    label: 'Tổng quan Chatbot',
    icon: mdiViewDashboard,
  },
  {
    to: '/chatbot/intents',
    label: 'Quản lý Intent',
    icon: mdiMessageText,
  },
  {
    to: '/chatbot/responses',
    label: 'Quản lý Response',
    icon: mdiTextBox,
  },
  {
    to: '/chatbot/nlu-examples',
    label: 'Quản lý Mẫu câu NLU',
    icon: mdiViewList,
  },
  {
    to: '/chatbot/interactions',
    label: 'Tương tác với Chatbot',
    icon: mdiChatProcessing,
  },
  {
    to: '/chatbot/data-ingestion',
    label: 'Nhập liệu từ URL',
    icon: mdiWeb,
  },
]
