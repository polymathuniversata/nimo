// src/stores/tokens.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface TokenTransaction {
  id: string
  type: 'transfer' | 'stake' | 'reward' | 'purchase'
  amount: number
  timestamp: string
  fromAddress?: string
  toAddress?: string
  description: string
  txHash?: string
}

export interface TokenBalance {
  nimoTokens: number
  adaBalance: number
  stakedTokens: number
  availableTokens: number
}

export const useTokensStore = defineStore('tokens', () => {
  // State
  const balance = ref<TokenBalance>({
    nimoTokens: 0,
    adaBalance: 0,
    stakedTokens: 0,
    availableTokens: 0
  })
  const transactions = ref<TokenTransaction[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  const fetchBalance = async () => {
    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await api.get('/tokens/balance')

      // Mock balance data for development
      balance.value = {
        nimoTokens: Math.floor(Math.random() * 10000) + 1000,
        adaBalance: Math.random() * 500 + 50,
        stakedTokens: Math.floor(Math.random() * 500) + 100,
        availableTokens: Math.floor(Math.random() * 800) + 200
      }

    } catch (err) {
      error.value = 'Failed to fetch token balance.'

      // Provide mock data as fallback
      balance.value = {
        nimoTokens: 2500,
        adaBalance: 125.5,
        stakedTokens: 300,
        availableTokens: 400
      }

      console.warn('Using mock token balance due to API failure')
    } finally {
      loading.value = false
    }
  }

  const fetchTransactions = async () => {
    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await api.get('/tokens/transactions')

      // Mock transactions for development
      const mockTransactions: TokenTransaction[] = [
        {
          id: '1',
          type: 'reward',
          amount: 50,
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          description: 'Contribution reward - Community organizing',
          txHash: 'mock_tx_123'
        },
        {
          id: '2',
          type: 'transfer',
          amount: -25,
          timestamp: new Date(Date.now() - 172800000).toISOString(),
          fromAddress: 'addr1...',
          toAddress: 'addr2...',
          description: 'Transfer to fellow contributor',
          txHash: 'mock_tx_124'
        },
        {
          id: '3',
          type: 'stake',
          amount: 100,
          timestamp: new Date(Date.now() - 259200000).toISOString(),
          description: 'Staked for governance participation',
          txHash: 'mock_tx_125'
        }
      ]

      transactions.value = mockTransactions

    } catch (err) {
      error.value = 'Failed to fetch transactions.'

      // Provide mock data as fallback
      transactions.value = [
        {
          id: 'mock-1',
          type: 'reward',
          amount: 50,
          timestamp: new Date().toISOString(),
          description: 'Sample contribution reward',
          txHash: 'mock_tx_sample'
        }
      ]

      console.warn('Using mock transactions due to API failure')
    } finally {
      loading.value = false
    }
  }

  const transferTokens = async (transferData: {
    toAddress: string
    amount: number
    description?: string
  }) => {
    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await api.post('/tokens/transfer', transferData)

      // Optimistically update balance
      balance.value.nimoTokens -= transferData.amount
      balance.value.availableTokens -= transferData.amount

      // Add transaction to list
      const newTransaction: TokenTransaction = {
        id: Date.now().toString(),
        type: 'transfer',
        amount: -transferData.amount,
        timestamp: new Date().toISOString(),
        toAddress: transferData.toAddress,
        description: transferData.description || 'Token transfer',
        txHash: 'pending'
      }

      transactions.value.unshift(newTransaction)

      // Refresh data after successful transfer
      await Promise.all([fetchBalance(), fetchTransactions()])

    } catch (err) {
      error.value = 'Token transfer failed.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const stakeTokens = async (stakeData: {
    amount: number
    duration?: number
  }) => {
    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await api.post('/tokens/stake', stakeData)

      // Optimistically update balance
      balance.value.nimoTokens -= stakeData.amount
      balance.value.availableTokens -= stakeData.amount
      balance.value.stakedTokens += stakeData.amount

      // Add transaction to list
      const newTransaction: TokenTransaction = {
        id: Date.now().toString(),
        type: 'stake',
        amount: stakeData.amount,
        timestamp: new Date().toISOString(),
        description: `Staked ${stakeData.amount} NIMO tokens`,
        txHash: 'pending'
      }

      transactions.value.unshift(newTransaction)

      // Refresh data after successful staking
      await Promise.all([fetchBalance(), fetchTransactions()])

    } catch (err) {
      error.value = 'Token staking failed.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const refreshData = async () => {
    await Promise.all([fetchBalance(), fetchTransactions()])
  }

  return {
    // State
    balance,
    transactions,
    loading,
    error,

    // Actions
    fetchBalance,
    fetchTransactions,
    transferTokens,
    stakeTokens,
    refreshData
  }
})
