import { createRouter, createWebHashHistory } from 'vue-router'
import Style from '@/views/StyleView.vue'
import Home from '@/views/HomeView.vue'

const routes = [
  {
    meta: {
      title: 'Select style',
    },
    path: '/styles',
    name: 'style',
    component: Style,
  },
  {
    // Document title tag
    // We combine it with defaultDocumentTitle set in `src/main.js` on router.afterEach hook
    meta: {
      title: 'Dashboard',
    },
    path: '/dashboard',
    name: 'dashboard',
    component: Home,
  },
  {
    meta: {
      title: 'Tables',
    },
    path: '/tables',
    name: 'tables',
    component: () => import('@/views/TablesView.vue'),
  },
  {
    meta: {
      title: 'Forms',
    },
    path: '/forms',
    name: 'forms',
    component: () => import('@/views/FormsView.vue'),
  },
  {
    meta: {
      title: 'Profile',
    },
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
  },
  {
    meta: {
      title: 'Ui',
    },
    path: '/ui',
    name: 'ui',
    component: () => import('@/views/UiView.vue'),
  },
  {
    meta: {
      title: 'Responsive layout',
    },
    path: '/responsive',
    name: 'responsive',
    component: () => import('@/views/ResponsiveView.vue'),
  },
  {
    meta: {
      title: 'Login',
    },
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
  },
  {
    meta: {
      title: 'Error',
    },
    path: '/error',
    name: 'error',
    component: () => import('@/views/ErrorView.vue'),
  },
  // Chatbot Management Routes
  {
    meta: {
      title: 'Chào mừng đến với Hệ thống Quản lý Chatbot',
    },
    path: '/chatbot/welcome',
    name: 'chatbot-welcome',
    component: () => import('@/views/chatbot/WelcomeView.vue'),
  },
  {
    meta: {
      title: 'Tổng quan Chatbot',
    },
    path: '/chatbot/dashboard',
    name: 'chatbot-dashboard',
    component: () => import('@/views/chatbot/DashboardView.vue'),
  },
  {
    meta: {
      title: 'Quản lý Intent',
    },
    path: '/chatbot/intents',
    name: 'chatbot-intents',
    component: () => import('@/views/chatbot/intents/IntentsView.vue'),
  },
  {
    meta: {
      title: 'Quản lý Response',
    },
    path: '/chatbot/responses',
    name: 'chatbot-responses',
    component: () => import('@/views/chatbot/responses/ResponsesView.vue'),
  },
  {
    meta: {
      title: 'Quản lý Mẫu câu NLU',
    },
    path: '/chatbot/nlu-examples',
    name: 'chatbot-nlu-examples',
    component: () => import('@/views/chatbot/nlu-examples/NluExamplesView.vue'),
  },
  {
    meta: {
      title: 'Tương tác với Chatbot',
    },
    path: '/chatbot/interactions',
    name: 'chatbot-interactions',
    component: () => import('@/views/chatbot/interactions/InteractionsView.vue'),
  },
  {
    meta: {
      title: 'Nhập liệu từ URL',
    },
    path: '/chatbot/data-ingestion',
    name: 'chatbot-data-ingestion',
    component: () => import('@/views/chatbot/data-ingestion/DataIngestionView.vue'),
  },
  {
    meta: {
      title: 'Xem nguồn dữ liệu',
    },
    path: '/chatbot/data-source/:id',
    name: 'chatbot-data-source-view',
    component: () => import('@/views/chatbot/data-ingestion/DataSourceView.vue'),
  },
  // Redirects
  {
    path: '/chatbot',
    redirect: '/chatbot/welcome',
  },
  {
    path: '/',
    redirect: '/chatbot/welcome',
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  },
})

export default router
