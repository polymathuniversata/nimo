import { boot } from 'quasar/wrappers'
import { useWalletStore } from 'src/stores/wallet'

export default boot(async ({ app, router }) => {
  const walletStore = useWalletStore()

  // Initialize wallet event listeners when the app starts
  if (typeof window !== 'undefined') {
    walletStore.setupEventListeners()
    
    // Auto-connect if user was previously connected
    await walletStore.autoConnect()
  }

  // Make wallet store globally available
  app.config.globalProperties.$wallet = walletStore

  // Router guard to check wallet connection for protected routes
  router.beforeEach((to, from, next) => {
    // Routes that require wallet connection
    const protectedRoutes = [
      '/dashboard'
    ]

    if (protectedRoutes.some(route => to.path.startsWith(route))) {
      if (!walletStore.isConnected) {
        // Store the intended route to redirect after connection
        localStorage.setItem('intendedRoute', to.fullPath)
        next('/')
        return
      }

      if (!walletStore.isOnCorrectNetwork) {
        // Show network warning but don't block navigation
        console.warn('Wrong network detected')
      }
    }

    next()
  })

  // Handle cleanup on app unmount
  app.onUnmount = () => {
    walletStore.removeEventListeners()
  }
})