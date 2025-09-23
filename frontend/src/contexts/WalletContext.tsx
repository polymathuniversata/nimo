// src/contexts/WalletContext.tsx
import React, { createContext, useContext, useReducer } from 'react'

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

interface WalletState {
  wallet: WalletInfo | null
  connectedWallet: string | null
  transactions: WalletTransaction[]
  isConnecting: boolean
  isLoading: boolean
  error: string | null
  availableWallets: string[]
  lastRefresh: number
}

type WalletAction =
  | { type: 'WALLET_CONNECT_START' }
  | { type: 'WALLET_CONNECT_SUCCESS'; payload: { wallet: WalletInfo; walletName: string } }
  | { type: 'WALLET_CONNECT_ERROR'; payload: string }
  | { type: 'WALLET_DISCONNECT' }
  | { type: 'WALLET_LOAD_INFO_START' }
  | { type: 'WALLET_LOAD_INFO_SUCCESS'; payload: Partial<WalletInfo> }
  | { type: 'WALLET_LOAD_INFO_ERROR'; payload: string }
  | { type: 'WALLET_LOAD_TRANSACTIONS_START' }
  | { type: 'WALLET_LOAD_TRANSACTIONS_SUCCESS'; payload: WalletTransaction[] }
  | { type: 'WALLET_LOAD_TRANSACTIONS_ERROR'; payload: string }
  | { type: 'WALLET_SEND_TRANSACTION'; payload: { amount: number; toAddress: string } }
  | { type: 'WALLET_SEND_TOKEN'; payload: { assetId: string; amount: number } }
  | { type: 'WALLET_REFRESH_START' }
  | { type: 'WALLET_REFRESH_SUCCESS' }
  | { type: 'CLEAR_ERROR' }

const initialState: WalletState = {
  wallet: null,
  connectedWallet: null,
  transactions: [],
  isConnecting: false,
  isLoading: false,
  error: null,
  availableWallets: ['nami', 'eternl', 'flint', 'gerowallet', 'yoroi'],
  lastRefresh: 0
}

function walletReducer(state: WalletState, action: WalletAction): WalletState {
  switch (action.type) {
    case 'WALLET_CONNECT_START':
      return { ...state, isConnecting: true, error: null }
    case 'WALLET_CONNECT_SUCCESS':
      return {
        ...state,
        wallet: action.payload.wallet,
        connectedWallet: action.payload.walletName,
        isConnecting: false,
        lastRefresh: Date.now(),
        error: null
      }
    case 'WALLET_CONNECT_ERROR':
      return { ...state, isConnecting: false, error: action.payload }
    case 'WALLET_DISCONNECT':
      return {
        ...state,
        wallet: null,
        connectedWallet: null,
        transactions: [],
        isLoading: false,
        error: null
      }
    case 'WALLET_LOAD_INFO_START':
    case 'WALLET_LOAD_TRANSACTIONS_START':
    case 'WALLET_REFRESH_START':
      return { ...state, isLoading: true, error: null }
    case 'WALLET_LOAD_INFO_SUCCESS':
      return {
        ...state,
        wallet: state.wallet ? { ...state.wallet, ...action.payload } : null,
        isLoading: false,
        error: null
      }
    case 'WALLET_LOAD_TRANSACTIONS_SUCCESS':
      return { ...state, transactions: action.payload, isLoading: false, error: null }
    case 'WALLET_LOAD_INFO_ERROR':
    case 'WALLET_LOAD_TRANSACTIONS_ERROR':
      return { ...state, isLoading: false, error: action.payload }
    case 'WALLET_SEND_TRANSACTION':
      return {
        ...state,
        transactions: [{
          txHash: 'mock_tx_' + Date.now(),
          timestamp: new Date().toISOString(),
          amount: -action.payload.amount,
          type: 'sent',
          description: `Transfer to ${action.payload.toAddress.substring(0, 20)}...`
        }, ...state.transactions],
        wallet: state.wallet ? {
          ...state.wallet,
          adaBalance: state.wallet.adaBalance - action.payload.amount,
          balance: state.wallet.balance - action.payload.amount
        } : null
      }
    case 'WALLET_SEND_TOKEN':
      return {
        ...state,
        transactions: [{
          txHash: 'mock_token_tx_' + Date.now(),
          timestamp: new Date().toISOString(),
          amount: -action.payload.amount,
          type: 'sent',
          description: `Token transfer: ${action.payload.assetId}`
        }, ...state.transactions],
        wallet: state.wallet && action.payload.assetId.includes('NIMO') ? {
          ...state.wallet,
          nimoTokenBalance: state.wallet.nimoTokenBalance - action.payload.amount
        } : state.wallet
      }
    case 'CLEAR_ERROR':
      return { ...state, error: null }
    default:
      return state
  }
}

interface WalletContextType {
  state: WalletState
  connectWallet: (walletName: string) => Promise<void>
  disconnectWallet: () => Promise<void>
  loadWalletInfo: () => Promise<void>
  loadTransactions: () => Promise<void>
  sendTransaction: (transactionData: { toAddress: string; amount: number; metadata?: Record<string, any> }) => Promise<void>
  sendToken: (tokenData: { toAddress: string; assetId: string; amount: number }) => Promise<void>
  refreshWallet: () => Promise<void>
  checkConnection: () => Promise<boolean>
  validateAddress: (address: string) => boolean
  formatADA: (amount: number) => string
  getWalletInstallUrl: (walletName: string) => string
  getSupportedWallets: () => string[]
  clearError: () => void
  canRefresh: boolean
  isConnected: boolean
  recentTransactions: WalletTransaction[]
  pendingTransactions: WalletTransaction[]
}

const WalletContext = createContext<WalletContextType | undefined>(undefined)

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(walletReducer, initialState)

  const connectWallet = async (walletName: string) => {
    dispatch({ type: 'WALLET_CONNECT_START' })

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

      dispatch({ type: 'WALLET_CONNECT_SUCCESS', payload: { wallet: mockWallet, walletName } })

      // Load initial wallet data
      await Promise.all([loadWalletInfo(), loadTransactions()])

    } catch (err) {
      dispatch({ type: 'WALLET_CONNECT_ERROR', payload: `Failed to connect to ${walletName} wallet.` })
      throw err
    }
  }

  const disconnectWallet = async () => {
    dispatch({ type: 'WALLET_DISCONNECT' })
  }

  const loadWalletInfo = async () => {
    if (!state.connectedWallet || !state.wallet) return

    dispatch({ type: 'WALLET_LOAD_INFO_START' })

    try {
      // TODO: Replace with actual wallet API calls
      // const response = await api.get(`/wallet/${state.wallet.address}/info`)

      // Mock wallet info update
      if (state.wallet) {
        const updatedWallet = {
          ...state.wallet,
          balance: Math.random() * 500 + 100,
          adaBalance: state.wallet.balance * 0.8,
          nimoTokenBalance: Math.floor(Math.random() * 2000) + 500
        }

        dispatch({ type: 'WALLET_LOAD_INFO_SUCCESS', payload: updatedWallet })
      }

    } catch (err) {
      dispatch({ type: 'WALLET_LOAD_INFO_ERROR', payload: 'Failed to load wallet information.' })
      console.warn('Using cached wallet info due to API failure')
    }
  }

  const loadTransactions = async () => {
    if (!state.connectedWallet || !state.wallet) return

    dispatch({ type: 'WALLET_LOAD_TRANSACTIONS_START' })

    try {
      // TODO: Replace with actual wallet/blockchain API calls
      // const response = await api.get(`/wallet/${state.wallet.address}/transactions`)

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

      dispatch({ type: 'WALLET_LOAD_TRANSACTIONS_SUCCESS', payload: mockTransactions })

    } catch (err) {
      dispatch({ type: 'WALLET_LOAD_TRANSACTIONS_ERROR', payload: 'Failed to load wallet transactions.' })
      console.warn('Using mock transactions due to API failure')
    }
  }

  const sendTransaction = async (transactionData: { toAddress: string; amount: number; metadata?: Record<string, any> }) => {
    if (!state.wallet) {
      throw new Error('No wallet connected')
    }

    dispatch({ type: 'WALLET_SEND_TRANSACTION', payload: { amount: transactionData.amount, toAddress: transactionData.toAddress } })

    try {
      // TODO: Replace with actual Cardano transaction
      // This would use wallet APIs to sign and submit transactions

      console.log('Sending transaction:', transactionData)

      // Refresh data after transaction
      await Promise.all([loadWalletInfo(), loadTransactions()])

    } catch (err) {
      dispatch({ type: 'WALLET_LOAD_INFO_ERROR', payload: 'Transaction failed.' })
      throw err
    }
  }

  const sendToken = async (tokenData: { toAddress: string; assetId: string; amount: number }) => {
    if (!state.wallet) {
      throw new Error('No wallet connected')
    }

    dispatch({ type: 'WALLET_SEND_TOKEN', payload: { assetId: tokenData.assetId, amount: tokenData.amount } })

    try {
      // TODO: Replace with actual token transaction
      console.log('Sending token:', tokenData)

      // Refresh data after token transaction
      await Promise.all([loadWalletInfo(), loadTransactions()])

    } catch (err) {
      dispatch({ type: 'WALLET_LOAD_INFO_ERROR', payload: 'Token transfer failed.' })
      throw err
    }
  }

  const refreshWallet = async () => {
    dispatch({ type: 'WALLET_REFRESH_START' })

    try {
      await Promise.all([loadWalletInfo(), loadTransactions()])
      dispatch({ type: 'WALLET_REFRESH_SUCCESS' })
    } catch (err) {
      dispatch({ type: 'WALLET_LOAD_INFO_ERROR', payload: 'Failed to refresh wallet.' })
    }
  }

  const checkConnection = async () => {
    if (!state.connectedWallet) return false

    try {
      // TODO: Replace with actual wallet connection check
      // This would ping the wallet API to verify connection

      return true // Mock successful connection check

    } catch (err) {
      dispatch({ type: 'WALLET_CONNECT_ERROR', payload: 'Wallet connection lost.' })
      return false
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
    return state.availableWallets
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const canRefresh = Date.now() - state.lastRefresh >= 30000 // 30 seconds minimum between refreshes

  const isConnected = state.wallet !== null && state.connectedWallet !== null

  const recentTransactions = state.transactions
    .slice()
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 10)

  const pendingTransactions = state.transactions.filter(tx =>
    new Date(tx.timestamp).getTime() > Date.now() - 600000 // Last 10 minutes
  )

  return (
    <WalletContext.Provider
      value={{
        state,
        connectWallet,
        disconnectWallet,
        loadWalletInfo,
        loadTransactions,
        sendTransaction,
        sendToken,
        refreshWallet,
        checkConnection,
        validateAddress,
        formatADA,
        getWalletInstallUrl,
        getSupportedWallets,
        clearError,
        canRefresh,
        isConnected,
        recentTransactions,
        pendingTransactions
      }}
    >
      {children}
    </WalletContext.Provider>
  )
}

export function useWallet() {
  const context = useContext(WalletContext)
  if (context === undefined) {
    throw new Error('useWallet must be used within a WalletProvider')
  }
  return context
}
