<template>
  <router-view />
</template>

<script>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { authService } from './services'

export default {
  name: 'App',

  setup() {
    const router = useRouter()
    const $q = useQuasar()

    // Initialize authentication on app startup
    onMounted(() => {
      // Check for stored token and set up auth interceptors
      authService.initAuth()
      
      // Set up global error handling for API calls
      window.addEventListener('unhandledrejection', event => {
        console.error('Unhandled Promise Rejection:', event.reason)
        
        // Show user-friendly error message
        if (event.reason && event.reason.response) {
          const status = event.reason.response.status
          
          if (status === 401) {
            // Auth error already handled by interceptor
            return
          }
          
          if (status === 403) {
            $q.notify({
              type: 'negative',
              message: 'You do not have permission to perform this action',
              icon: 'lock'
            })
            return
          }
          
          if (status === 404) {
            $q.notify({
              type: 'negative',
              message: 'The requested resource was not found',
              icon: 'error'
            })
            return
          }
          
          if (status >= 500) {
            $q.notify({
              type: 'negative',
              message: 'Server error. Please try again later',
              icon: 'error'
            })
            return
          }
          
          // General error with custom message from API
          const message = event.reason.response.data?.message || 'An error occurred'
          $q.notify({
            type: 'negative',
            message,
            icon: 'error'
          })
        }
      })
    })
  }
}
</script>