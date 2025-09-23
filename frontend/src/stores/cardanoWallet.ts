// src/stores/cardanoWallet.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface WalletInfo {
  address: string
  stakeAddress?: string
  balance: number
  adaBalance: number
  nimoTokenBalance: number
  network: 'mainnet' | 'testnet' | 'preview'
  walletName: string
}

export interface WalletTransaction {
  txHash: string
  timestamp: string
  amount: number
  type: 'sent' | 'received' | 'stake' | 'reward'
  description: string
}

export const useCardanoWalletStore = defineStore('cardanoWallet', () => {
  // State
  const wallet = ref<WalletInfo | null>(null)
  const connectedWallet = ref<string | null>(null)
  const transactions = ref<WalletTransaction[]>([])
  const isConnecting = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const availableWallets = ref<string[]>(['nami', 'eternl', 'flint', 'gerowallet', 'yoroi'])
  const lastRefresh = ref<number>(0)

  // Getters
  const isConnected = computed(() => {
    return wallet.value !== null && connectedWallet.value !== null
  })

  const balance = computed(() => wallet.value?.balance || 0)

  const adaBalance = computed(() => wallet.value?.adaBalance || 0)

  const address = computed(() => wallet.value?.address || '')

  const network = computed(() => wallet.value?.network || 'preview')

  const stakeAddress = computed(() => wallet.value?.stakeAddress)

  const walletName = computed(() => wallet.value?.walletName || '')

  const canRefresh = computed(() => {
    const now = Date.now()
    return now - lastRefresh.value >= 30000 // 30 seconds minimum between refreshes
  })

  const recentTransactions = computed(() => {
    return transactions.value
      .slice()
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, 10)
  })

  const pendingTransactions = computed(() => {
    return transactions.value.filter(tx =>
      new Date(tx.timestamp).getTime() > Date.now() - 600000 // Last 10 minutes
    )
  })

  // Actions
  const connectWallet = async (walletName: string) => {
    isConnecting.value = true
    error.value = null

    try {
      // TODO: Replace with actual Cardano wallet integration
      // This would integrate with wallet APIs like Nami, Eternl, etc.

      // Mock wallet connection for development
      const mockWallet: WalletInfo = {
        address: 'addr1qxqs59lphg8g6qndelq8xwqn60ag3aeylg2qnkww6y4kyeh5q9q0l0n8dv6c9e9n2p6x8y2q2g2x9q2g2x9q2g2x9q2g2x9q2g2x9q2g2',
        stakeAddress: 'stake1uxqs59lphg8g6qndelq8xwqn60ag3aeylg2qnkww6y4kyeh5q9q0l0n8dv6c9e9n2p6x8y2q2g2x9q2g2x9q2g2x9q2g2x9q2g2x9q2g2',
        balance: 250.75,
        adaBalance: 245.50,
        nimoTokenBalance: 1250,
        network: 'preview',
        walletName: walletName
      }

      wallet.value = mockWallet
      connectedWallet.value = walletName
      lastRefresh.value = Date.now()

      // Load initial wallet data
      await Promise.all([loadWalletInfo(), loadTransactions()])

    } catch (err) {
      error.value = `Failed to connect to ${walletName} wallet.`
      throw err
    } finally {
      isConnecting.value = false
    }
  }

  const disconnectWallet = async () => {
    isLoading.value = true

    try {
      // TODO: Replace with actual wallet disconnect logic
      // This would call wallet API disconnect methods

      // Clear wallet state
      wallet.value = null
      connectedWallet.value = null
      transactions.value = []

    } catch (err) {
      error.value = 'Failed to disconnect wallet.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const loadWalletInfo = async () => {
    if (!connectedWallet.value || !wallet.value) return

    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual wallet API calls
      // const response = await api.get(`/wallet/${wallet.value.address}/info`)

      // Mock wallet info update
      if (wallet.value) {
        wallet.value.balance = Math.random() * 500 + 100
        wallet.value.adaBalance = wallet.value.balance * 0.8
        wallet.value.nimoTokenBalance = Math.floor(Math.random() * 2000) + 500
      }

    } catch (err) {
      error.value = 'Failed to load wallet information.'
      console.warn('Using cached wallet info due to API failure')
    } finally {
      isLoading.value = false
    }
  }

  const loadTransactions = async () => {
    if (!connectedWallet.value || !wallet.value) return

    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual wallet/blockchain API calls
      // const response = await api.get(`/wallet/${wallet.value.address}/transactions`)

      // Mock transactions
      const mockTransactions: WalletTransaction[] = [
        {
          txHash: 'a1b2c3d4e5f6...',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          amount: 50.0,
          type: 'received',
          description: 'NIMO token reward'
        },
        {
          txHash: 'f6e5d4c3b2a1...',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          amount: -25.5,
          type: 'sent',
          description: 'Transfer to contribution wallet'
        },
        {
          txHash: '1a2b3c4d5e6f...',
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          amount: 100.0,
          type: 'stake',
          description: 'Governance staking'
        }
      ]

      transactions.value = mockTransactions

    } catch (err) {
      error.value = 'Failed to load wallet transactions.'
      console.warn('Using mock transactions due to API failure')
    } finally {
      isLoading.value = false
    }
  }

  const sendTransaction = async (transactionData: {
    toAddress: string
    amount: number
    metadata?: Record<string, any>
  }) => {
    if (!wallet.value) {
      throw new Error('No wallet connected')
    }

    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual Cardano transaction
      // This would use wallet APIs to sign and submit transactions

      console.log('Sending transaction:', transactionData)

      // Mock transaction success
      const newTransaction: WalletTransaction = {
        txHash: 'mock_tx_' + Date.now(),
        timestamp: new Date().toISOString(),
        amount: -transactionData.amount,
        type: 'sent',
        description: `Transfer to ${transactionData.toAddress.substring(0, 20)}...`
      }

      transactions.value.unshift(newTransaction)

      // Update balance
      if (wallet.value) {
        wallet.value.adaBalance -= transactionData.amount
        wallet.value.balance = wallet.value.adaBalance + (wallet.value.nimoTokenBalance * 0.001) // Rough conversion
      }

    } catch (err) {
      error.value = 'Transaction failed.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const sendToken = async (tokenData: {
    toAddress: string
    assetId: string
    amount: number
  }) => {
    if (!wallet.value) {
      throw new Error('No wallet connected')
    }

    isLoading.value = true
    error.value = null

    try {
      // TODO: Replace with actual token transaction
      console.log('Sending token:', tokenData)

      // Mock token transaction success
      const newTransaction: WalletTransaction = {
        txHash: 'mock_token_tx_' + Date.now(),
        timestamp: new Date().toISOString(),
        amount: -tokenData.amount,
        type: 'sent',
        description: `Token transfer: ${tokenData.assetId}`
      }

      transactions.value.unshift(newTransaction)

      // Update token balance
      if (wallet.value && tokenData.assetId.includes('NIMO')) {
        wallet.value.nimoTokenBalance -= tokenData.amount
      }

    } catch (err) {
      error.value = 'Token transfer failed.'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const refreshWallet = async () => {
    if (!canRefresh.value) {
      console.log('Wallet refresh throttled. Please wait 30 seconds.')
      return
    }

    lastRefresh.value = Date.now()
    await Promise.all([loadWalletInfo(), loadTransactions()])
  }

  const checkConnection = async () => {
    if (!connectedWallet.value) return false

    try {
      // TODO: Replace with actual wallet connection check
      // This would ping the wallet API to verify connection

      return true // Mock successful connection check

    } catch (err) {
      error.value = 'Wallet connection lost.'
      return false
    }
  }

  const initialize = async () => {
    // Check for previously connected wallet
    const savedWallet = localStorage.getItem('connected_wallet')
    if (savedWallet && availableWallets.value.includes(savedWallet)) {
      try {
        await connectWallet(savedWallet)
      } catch (err) {
        // Failed to reconnect, clear saved wallet
        localStorage.removeItem('connected_wallet')
      }
    }
  }

  const validateAddress = (address: string): boolean => {
    // Basic Cardano address validation
    const cardanoAddressRegex = /^addr[0-9a-z]{99}$/
    const stakeAddressRegex = /^stake[0-9a-z]{54}$/

    return cardanoAddressRegex.test(address) || stakeAddressRegex.test(address)
  }

  const formatADA = (amount: number): string => {
    return `${amount.toFixed(2)} ADA`
  }

  const getWalletInstallUrl = (walletName: string): string => {
    const urls: Record<string, string> = {
      nami: 'https://namiwallet.io/',
      eternl: 'https://eternl.io/',
      flint: 'https://flint-wallet.com/',
      gerowallet: 'https://gerowallet.io/',
      yoroi: 'https://yoroi-wallet.com/'
    }

    return urls[walletName] || '#'
  }

  const getSupportedWallets = (): string[] => {
    return availableWallets.value
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    wallet,
    connectedWallet,
    transactions,
    isConnecting,
    isLoading,
    error,
    availableWallets,
    lastRefresh,

    // Getters
    isConnected,
    balance,
    adaBalance,
    address,
    network,
    stakeAddress,
    walletName,
    canRefresh,
    recentTransactions,
    pendingTransactions,

    // Actions
    connectWallet,
    disconnectWallet,
    loadWalletInfo,
    loadTransactions,
    sendTransaction,
    sendToken,
    refreshWallet,
    checkConnection,
    initialize,
    validateAddress,
    formatADA,
    getWalletInstallUrl,
    getSupportedWallets,
    clearError
  }
})
