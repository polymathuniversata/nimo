// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: string
  email: string
  name: string
  roles: string[]
  kycVerified: boolean
  walletAddress?: string
  identityNft?: string
  createdAt: string
  lastLogin: string
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const hasRole = computed(() => (role: string) => {
    return user.value?.roles.includes(role) || false
  })

  const hasPermission = computed(() => (permission: string) => {
    // Basic permission check - can be extended
    return isAuthenticated.value
  })

  const hasAnyRole = computed(() => (roles: string[]) => {
    return roles.some(role => user.value?.roles.includes(role))
  })

  const getUserRoles = computed(() => user.value?.roles || [])

  const getPrimaryRole = computed(() => user.value?.roles[0] || null)

  const getPreferredDashboard = computed(() => {
    if (!user.value) return '/login'

    const roles = user.value.roles
    if (roles.includes('admin')) return '/admin'
    if (roles.includes('diaspora')) return '/diaspora'
    if (roles.includes('organization')) return '/organization'
    if (roles.includes('contributor')) return '/contributor'

    return '/dashboard'
  })

  // Actions
  const login = async (loginData: { email: string; password: string }) => {
    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await api.post('/auth/login', loginData)

      // Mock successful login for development
      const mockUser: User = {
        id: '1',
        email: loginData.email,
        name: 'John Doe',
        roles: ['contributor'],
        kycVerified: true,
        walletAddress: 'addr1...',
        createdAt: new Date().toISOString(),
        lastLogin: new Date().toISOString()
      }

      user.value = mockUser
      isAuthenticated.value = true

      // TODO: Store tokens securely
      localStorage.setItem('auth_token', 'mock_token')

    } catch (err) {
      error.value = 'Login failed. Please check your credentials.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const register = async (registerData: { email: string; password: string; name: string }) => {
    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // await api.post('/auth/register', registerData)

      console.log('Registration successful:', registerData)

    } catch (err) {
      error.value = 'Registration failed. Please try again.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const registerWithWallet = async (walletData: { walletAddress: string; signature: string }) => {
    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await api.post('/auth/register/wallet', walletData)

      const mockUser: User = {
        id: '2',
        email: '',
        name: 'Wallet User',
        roles: ['contributor'],
        kycVerified: false,
        walletAddress: walletData.walletAddress,
        createdAt: new Date().toISOString(),
        lastLogin: new Date().toISOString()
      }

      user.value = mockUser
      isAuthenticated.value = true

    } catch (err) {
      error.value = 'Wallet registration failed. Please try again.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true

    try {
      // TODO: Replace with actual API call
      // await api.post('/auth/logout')

      // Clear state
      user.value = null
      isAuthenticated.value = false

      // Clear stored tokens
      localStorage.removeItem('auth_token')

    } catch (err) {
      // Even if logout API fails, clear local state
      user.value = null
      isAuthenticated.value = false
      localStorage.removeItem('auth_token')
    } finally {
      loading.value = false
    }
  }

  const updateUser = async (userData: Partial<User>) => {
    if (!user.value) return

    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await api.patch(`/users/${user.value.id}`, userData)

      // Update local state
      user.value = { ...user.value, ...userData }

    } catch (err) {
      error.value = 'Failed to update user profile.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('auth_token')

    if (!token) {
      isAuthenticated.value = false
      user.value = null
      return
    }

    loading.value = true

    try {
      // TODO: Replace with actual API call to verify token
      // const response = await api.get('/auth/me')

      // Mock authenticated state for development
      isAuthenticated.value = true

    } catch (err) {
      // Token invalid, clear auth state
      isAuthenticated.value = false
      user.value = null
      localStorage.removeItem('auth_token')
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    user,
    isAuthenticated,
    loading,
    error,

    // Getters
    hasRole,
    hasPermission,
    hasAnyRole,
    getUserRoles,
    getPrimaryRole,
    getPreferredDashboard,

    // Actions
    login,
    register,
    registerWithWallet,
    logout,
    updateUser,
    checkAuthStatus
  }
})
