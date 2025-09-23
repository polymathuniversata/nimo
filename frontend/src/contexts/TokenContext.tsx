// src/contexts/TokenContext.tsx
import React, { createContext, useContext, useReducer } from 'react'

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

interface TokenState {
  balance: TokenBalance
  transactions: TokenTransaction[]
  loading: boolean
  error: string | null
}

type TokenAction =
  | { type: 'FETCH_BALANCE_START' }
  | { type: 'FETCH_BALANCE_SUCCESS'; payload: TokenBalance }
  | { type: 'FETCH_BALANCE_ERROR'; payload: string }
  | { type: 'FETCH_TRANSACTIONS_START' }
  | { type: 'FETCH_TRANSACTIONS_SUCCESS'; payload: TokenTransaction[] }
  | { type: 'FETCH_TRANSACTIONS_ERROR'; payload: string }
  | { type: 'TRANSFER_TOKENS'; payload: { amount: number; toAddress: string } }
  | { type: 'STAKE_TOKENS'; payload: { amount: number } }
  | { type: 'CLEAR_ERROR' }

const initialState: TokenState = {
  balance: {
    nimoTokens: 0,
    adaBalance: 0,
    stakedTokens: 0,
    availableTokens: 0
  },
  transactions: [],
  loading: false,
  error: null
}

function tokenReducer(state: TokenState, action: TokenAction): TokenState {
  switch (action.type) {
    case 'FETCH_BALANCE_START':
    case 'FETCH_TRANSACTIONS_START':
      return { ...state, loading: true, error: null }
    case 'FETCH_BALANCE_SUCCESS':
      return { ...state, balance: action.payload, loading: false, error: null }
    case 'FETCH_TRANSACTIONS_SUCCESS':
      return { ...state, transactions: action.payload, loading: false, error: null }
    case 'FETCH_BALANCE_ERROR':
    case 'FETCH_TRANSACTIONS_ERROR':
      return { ...state, loading: false, error: action.payload }
    case 'TRANSFER_TOKENS':
      return {
        ...state,
        balance: {
          ...state.balance,
          nimoTokens: state.balance.nimoTokens - action.payload.amount,
          availableTokens: state.balance.availableTokens - action.payload.amount
        },
        transactions: [{
          id: Date.now().toString(),
          type: 'transfer',
          amount: -action.payload.amount,
          timestamp: new Date().toISOString(),
          toAddress: action.payload.toAddress,
          description: `Transfer to ${action.payload.toAddress.substring(0, 20)}...`,
          txHash: 'pending'
        }, ...state.transactions]
      }
    case 'STAKE_TOKENS':
      return {
        ...state,
        balance: {
          ...state.balance,
          nimoTokens: state.balance.nimoTokens - action.payload.amount,
          availableTokens: state.balance.availableTokens - action.payload.amount,
          stakedTokens: state.balance.stakedTokens + action.payload.amount
        },
        transactions: [{
          id: Date.now().toString(),
          type: 'stake',
          amount: action.payload.amount,
          timestamp: new Date().toISOString(),
          description: `Staked ${action.payload.amount} NIMO tokens`,
          txHash: 'pending'
        }, ...state.transactions]
      }
    case 'CLEAR_ERROR':
      return { ...state, error: null }
    default:
      return state
  }
}

interface TokenContextType {
  state: TokenState
  fetchBalance: () => Promise<void>
  fetchTransactions: () => Promise<void>
  transferTokens: (transferData: { toAddress: string; amount: number; description?: string }) => Promise<void>
  stakeTokens: (stakeData: { amount: number; duration?: number }) => Promise<void>
  refreshData: () => Promise<void>
  clearError: () => void
}

const TokenContext = createContext<TokenContextType | undefined>(undefined)

export function TokenProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(tokenReducer, initialState)

  const fetchBalance = async () => {
    dispatch({ type: 'FETCH_BALANCE_START' })

    try {
      // TODO: Replace with actual API call
      // const response = await api.get('/tokens/balance')

      // Mock balance data for development
      const mockBalance: TokenBalance = {
        nimoTokens: Math.floor(Math.random() * 10000) + 1000,
        adaBalance: Math.random() * 500 + 50,
        stakedTokens: Math.floor(Math.random() * 500) + 100,
        availableTokens: Math.floor(Math.random() * 800) + 200
      }

      dispatch({ type: 'FETCH_BALANCE_SUCCESS', payload: mockBalance })

    } catch (err) {
      dispatch({ type: 'FETCH_BALANCE_ERROR', payload: 'Failed to fetch token balance.' })

      // Provide mock data as fallback
      const fallbackBalance: TokenBalance = {
        nimoTokens: 2500,
        adaBalance: 125.5,
        stakedTokens: 300,
        availableTokens: 400
      }

      dispatch({ type: 'FETCH_BALANCE_SUCCESS', payload: fallbackBalance })
      console.warn('Using mock token balance due to API failure')
    }
  }

  const fetchTransactions = async () => {
    dispatch({ type: 'FETCH_TRANSACTIONS_START' })

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

      dispatch({ type: 'FETCH_TRANSACTIONS_SUCCESS', payload: mockTransactions })

    } catch (err) {
      dispatch({ type: 'FETCH_TRANSACTIONS_ERROR', payload: 'Failed to fetch transactions.' })

      // Provide mock data as fallback
      const fallbackTransactions: TokenTransaction[] = [
        {
          id: 'mock-1',
          type: 'reward',
          amount: 50,
          timestamp: new Date().toISOString(),
          description: 'Sample contribution reward',
          txHash: 'mock_tx_sample'
        }
      ]

      dispatch({ type: 'FETCH_TRANSACTIONS_SUCCESS', payload: fallbackTransactions })
      console.warn('Using mock transactions due to API failure')
    }
  }

  const transferTokens = async (transferData: { toAddress: string; amount: number; description?: string }) => {
    dispatch({ type: 'TRANSFER_TOKENS', payload: { amount: transferData.amount, toAddress: transferData.toAddress } })

    try {
      // TODO: Replace with actual API call
      // const response = await api.post('/tokens/transfer', transferData)

      // Refresh data after successful transfer
      await Promise.all([fetchBalance(), fetchTransactions()])

    } catch (err) {
      dispatch({ type: 'FETCH_BALANCE_ERROR', payload: 'Token transfer failed.' })
      throw err
    }
  }

  const stakeTokens = async (stakeData: { amount: number; duration?: number }) => {
    dispatch({ type: 'STAKE_TOKENS', payload: { amount: stakeData.amount } })

    try {
      // TODO: Replace with actual API call
      // const response = await api.post('/tokens/stake', stakeData)

      // Refresh data after successful staking
      await Promise.all([fetchBalance(), fetchTransactions()])

    } catch (err) {
      dispatch({ type: 'FETCH_BALANCE_ERROR', payload: 'Token staking failed.' })
      throw err
    }
  }

  const refreshData = async () => {
    await Promise.all([fetchBalance(), fetchTransactions()])
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  return (
    <TokenContext.Provider
      value={{
        state,
        fetchBalance,
        fetchTransactions,
        transferTokens,
        stakeTokens,
        refreshData,
        clearError
      }}
    >
      {children}
    </TokenContext.Provider>
  )
}

export function useTokens() {
  const context = useContext(TokenContext)
  if (context === undefined) {
    throw new Error('useTokens must be used within a TokenProvider')
  }
  return context
}
