import {
  mdiAccountCircle,
  mdiMonitor,
  mdiGithub,
  mdiLock,
  mdiAlertCircle,
  mdiSquareEditOutline,
  mdiTable,
  mdiViewList,
  mdiTelevisionGuide,
  mdiResponsive,
  mdiPalette,
  mdiReact,
  mdiRobotExcited,
  mdiMessageText,
  mdiTextBox,
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
    label: 'Chatbot',
    icon: mdiRobotExcited,
    menu: [
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
    ],
  },
  {
    to: '/dashboard',
    icon: mdiMonitor,
    label: 'Dashboard',
  },
  {
    to: '/tables',
    label: 'Tables',
    icon: mdiTable,
  },
  {
    to: '/forms',
    label: 'Forms',
    icon: mdiSquareEditOutline,
  },
  {
    to: '/ui',
    label: 'UI',
    icon: mdiTelevisionGuide,
  },
  {
    to: '/responsive',
    label: 'Responsive',
    icon: mdiResponsive,
  },
  {
    to: '/styles',
    label: 'Styles',
    icon: mdiPalette,
  },
  {
    to: '/profile',
    label: 'Profile',
    icon: mdiAccountCircle,
  },
  {
    to: '/login',
    label: 'Login',
    icon: mdiLock,
  },
  {
    to: '/error',
    label: 'Error',
    icon: mdiAlertCircle,
  },
  {
    label: 'Dropdown',
    icon: mdiViewList,
    menu: [
      {
        label: 'Item One',
      },
      {
        label: 'Item Two',
      },
    ],
  },
  {
    href: 'https://github.com/justboil/admin-one-vue-tailwind',
    label: 'GitHub',
    icon: mdiGithub,
    target: '_blank',
  },
  {
    href: 'https://github.com/justboil/admin-one-react-tailwind',
    label: 'React version',
    icon: mdiReact,
    target: '_blank',
  },
]
