import {
  mdiAccount,
  mdiCogOutline,
  mdiLogout,
  mdiThemeLightDark,
} from '@mdi/js'

export default [
  {
    isCurrentUser: true,
    menu: [
      {
        icon: mdiAccount,
        label: 'Hồ sơ',
        to: '/profile',
      },
      {
        icon: mdiCogOutline,
        label: 'Cài đặt',
      },
      {
        isDivider: true,
      },
      {
        icon: mdiLogout,
        label: 'Đăng xuất',
        isLogout: true,
      },
    ],
  },
  {
    icon: mdiThemeLightDark,
    label: 'Sáng/Tối',
    isDesktopNoLabel: true,
    isToggleLightDark: true,
  },
  {
    icon: mdiLogout,
    label: 'Đăng xuất',
    isDesktopNoLabel: true,
    isLogout: true,
  },
]
